# /// script
# requires-python = ">=3.14"
# dependencies = ["click", "selenium"]
# ///
"""Twitter/X dump - archive tweets to JSONL.

uv run main.py login USERNAME
uv run main.py timeline USERNAME [--no-headless]
uv run main.py user USERNAME target1 target2
"""

import json
import logging
import os
import random
import re
import sys
from contextlib import contextmanager
from contextlib import suppress
from datetime import UTC
from datetime import datetime
from html.parser import HTMLParser
from io import StringIO
from time import sleep
from time import time_ns

import click
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.ui import WebDriverWait

OUTDIR = './export'
TIMEOUT = 15
BACKOFF = 120
BACKOFF_JITTER = 60

log = logging.getLogger('tw-fetch')


# --- browser ---


@contextmanager
def browser(headless=True):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=opts)
    try:
        yield driver
    finally:
        driver.quit()


def inject_cookies(driver, cookies):
    driver.get('https://x.com')
    for c in cookies:
        with suppress(Exception):
            driver.add_cookie(c)
    driver.get('https://x.com')


# --- parsing ---


class _Strip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.buf = StringIO()

    def handle_data(self, d):
        self.buf.write(d)

    def result(self):
        return self.buf.getvalue()


def strip_tags(html):
    s = _Strip()
    s.feed(html)
    return s.result()


def parse_tweet(elem):
    try:
        text_el = elem.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
        text = strip_tags(text_el.get_attribute('innerHTML')).replace('\n', ' ').strip()
        text = re.sub(r'  +', ' ', text)

        author = elem.find_element(
            By.XPATH, ".//div[@data-testid='User-Name']/div[2]/div/div/a/div/span"
        ).get_attribute('innerHTML')

        time_tag = elem.find_element(By.XPATH, './/time[@datetime]')
        published = time_tag.get_attribute('datetime')
        ctime = (
            datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.000Z').replace(tzinfo=UTC).timestamp()
        )

        link = time_tag.find_element(By.XPATH, '..').get_attribute('href')
        if not link:
            return None

        id_ = link.split('/')[-1]
        try:
            id_ = int(id_)
        except ValueError:
            return None

    except (NoSuchElementException, StaleElementReferenceException, WebDriverException):
        return None
    return {'id': id_, 'url': link, 'author': author, 'text': text, 'ctime': ctime}


# --- i/o ---


def seen_ids(path):
    ids = set()
    if not os.path.exists(path):
        return ids
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                with suppress(json.JSONDecodeError, KeyError):
                    ids.add(json.loads(stripped)['id'])
    return ids


def append(f, record, existing):
    if record['id'] in existing:
        return False
    existing.add(record['id'])
    record['collected_at'] = time_ns()
    f.write(json.dumps(record) + '\n')
    f.flush()
    return True


# --- scrolling ---


def wait_timeline(driver, label='Timeline'):
    condition = (By.XPATH, f"//main//section//div[contains(@aria-label, '{label}')]")
    return WebDriverWait(driver, TIMEOUT).until(visibility_of_element_located(condition))


def scroll_down(driver):
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    sleep(2 + random.random())  # noqa: S311


def get_tweets(timeline):
    return timeline.find_elements(By.XPATH, './/article')


# --- commands ---

COOKIE_DIR = './cookies'


def cookie_path(username):
    return os.path.join(COOKIE_DIR, f'{username}.json')


def load_cookies(username):
    path = cookie_path(username)
    if not os.path.exists(path):
        click.echo(f'error: {path} not found, run: uv run main.py login {username}', err=True)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def collect_round(driver, existing, path):
    """One collection round: scroll timeline, parse, write new tweets."""
    try:
        driver.get('https://x.com')
        sleep(3)
        # click Following tab if present
        try:
            tab = driver.find_element(
                By.XPATH, "//div[@role='tablist']//span[contains(text(),'Following')]"
            )
            tab.click()
            sleep(2)
        except (NoSuchElementException, WebDriverException):
            pass

        timeline = wait_timeline(driver)
    except TimeoutException:
        log.exception('could not load timeline')
        return 0

    n = 0
    stale = 0
    with open(path, 'a') as f:
        for _ in range(30):
            batch = 0
            for tag in get_tweets(timeline):
                r = parse_tweet(tag)
                if r and append(f, r, existing):
                    batch += 1
                    n += 1
                    log.info(f'@{r["author"]}: {r["text"][:80]}')

            if batch == 0:
                stale += 1
                if stale >= 3:
                    break
            else:
                stale = 0

            scroll_down(driver)
            try:
                timeline = wait_timeline(driver)
            except TimeoutException:
                break

    return n


@click.group()
@click.option('--debug', is_flag=True)
def main(debug):
    """Twitter/X dump - archive tweets to JSONL."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )


@main.command()
@click.argument('username')
@click.option('--headless/--no-headless', default=True)
def timeline(username, headless):
    """Dump home timeline continuously."""
    cookies = load_cookies(username)
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f'timeline_{username}.jl')
    existing = seen_ids(path)
    total = len(existing)

    if existing:
        log.info(f'resuming, {total} tweets on disk')

    with browser(headless) as driver:
        inject_cookies(driver, cookies)
        rounds = 0
        while True:
            rounds += 1
            n = collect_round(driver, existing, path)
            total += n
            wait = BACKOFF + random.random() * BACKOFF_JITTER  # noqa: S311
            log.info(f'round {rounds}: {n} new, {total} total. sleeping {wait:.0f}s')
            sleep(wait)


@main.command()
@click.argument('username')
@click.argument('targets', nargs=-1, required=True)
@click.option('--headless/--no-headless', default=True)
@click.option('-d', '--delay', type=float, default=30)
def user(username, targets, headless, delay):
    """Dump one or more user profiles."""
    cookies = load_cookies(username)
    os.makedirs(OUTDIR, exist_ok=True)

    with browser(headless) as driver:
        inject_cookies(driver, cookies)

        for i, target in enumerate(targets):
            safe = target.lstrip('@')
            path = os.path.join(OUTDIR, f'user_{safe}.jl')
            existing = seen_ids(path)

            if existing:
                log.info(f'@{safe}: {len(existing)} tweets on disk')

            driver.get(f'https://x.com/{safe}')
            sleep(3)

            try:
                timeline = wait_timeline(driver, 'Timeline')
            except TimeoutException:
                log.exception(f'@{safe}: no timeline found')
                continue

            n = 0
            stale = 0
            with open(path, 'a') as f:
                for _ in range(200):
                    batch = 0
                    for tag in get_tweets(timeline):
                        r = parse_tweet(tag)
                        if r and append(f, r, existing):
                            batch += 1
                            n += 1
                            log.info(f'@{r["author"]}: {r["text"][:80]}')

                    if batch == 0:
                        stale += 1
                        if stale >= 5:
                            break
                    else:
                        stale = 0

                    scroll_down(driver)
                    try:
                        timeline = wait_timeline(driver, 'Timeline')
                    except TimeoutException:
                        break

            log.info(f'@{safe}: {n} new tweets -> {path}')

            if i < len(targets) - 1:
                w = delay + random.random() * delay  # noqa: S311
                log.info(f'sleeping {w:.0f}s')
                sleep(w)


def save_cookies(username, cookies):
    os.makedirs(COOKIE_DIR, exist_ok=True)
    out = cookie_path(username)
    with open(out, 'w') as f:
        json.dump(cookies, f, indent=2)
        f.write('\n')
    log.info(f'saved {len(cookies)} cookies to {out}')


@main.command()
@click.argument('username')
def login(username):
    """Open browser, log in manually, cookies are saved on close.

    Opens x.com in a visible browser. Log in by hand, then press
    Enter in this terminal. Cookies are saved for later headless runs.
    """
    with browser(headless=False) as driver:
        driver.get('https://x.com/i/flow/login')
        input("press Enter after you've logged in...")
        cookies = driver.get_cookies()

    auth = next((c for c in cookies if c['name'] == 'auth_token'), None)
    if not auth:
        log.warning('no auth_token in cookies — login may have failed')
    else:
        log.info(f'auth_token: {auth["value"][:12]}...')

    # strip non-serializable fields selenium adds
    clean = [
        {
            'name': c['name'],
            'value': c['value'],
            'domain': c.get('domain', ''),
            'path': c.get('path', '/'),
            'secure': c.get('secure', False),
            'httpOnly': c.get('httpOnly', False),
            'sameSite': c.get('sameSite', 'Lax'),
            **({'expiry': c['expiry']} if 'expiry' in c else {}),
        }
        for c in cookies
    ]

    save_cookies(username, clean)


if __name__ == '__main__':
    main()
