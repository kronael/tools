# tw-fetch

Two ways to read X (Twitter). They solve different problems; pick by whether
you already know which posts you want.

## mirror.py — read posts you can name, no account

`api.fxtwitter.com` serves a post as JSON without a key. A plain fetch of
`x.com` answers `402`, so the mirror is the only keyless read path.

```bash
uv run --script mirror.py 2089711566392578231
uv run --script mirror.py https://x.com/CryptoHayes/status/2089711566392578231
printf '%s\n' 2089711566392578231 | uv run --script mirror.py
```

One JSON object per post on stdout: id, author, created_at, text, likes,
retweets, replies, views, url. Failures go to stderr and do not stop the run.
Exit code is 1 only when every reference fails.

Limits worth knowing before you plan around it:

- The mirror has **no timeline and no search**. `/<user>/timeline` answers 404,
  and `/<user>/status/latest` answers 200 with "Sorry, that post doesn't
  exist". You must supply the ids.
- A protected account answers `401`. That is the account's setting, not an
  egress fault.
- The client sets `trust_env=True`, so `HTTPS_PROXY` is honoured. Behind a
  filtering proxy, allow `api.fxtwitter.com`.

## main.py — archive a timeline, needs an account

Selenium against the real logged-in site. This is the only path that
discovers posts rather than resolving named ones; it streams tweets into
JSONL files and skips ids already on disk on the next run.

### Auth

```sh
uv run main.py login <username>   # opens a visible browser; log in by hand
```

Cookies land in `./cookies/<username>.json` and are replayed into later
headless runs. There is no API token — X's public API no longer reaches
timelines, so this reads the rendered page through Selenium.

Re-run `login` whenever a run stops returning tweets; `auth_token`
expires and the failure looks like an empty timeline, not an error.

### Commands

Single-file PEP 723 script. Both forms below auto-resolve `selenium` + `click`.

```sh
uv run main.py timeline <username>              # home timeline, continuously
uv run main.py user <username> <target>...      # one or more profiles
uv run main.py login <username>                 # save cookies
```

Common flags:

| flag | default | meaning |
|---|---|---|
| `--headless/--no-headless` | headless | watch the browser work |
| `-d, --delay` | `30` | seconds between profiles in `user` mode |
| `--debug` | off | DEBUG logging (before the subcommand) |

### Output

```
./export/timeline_<username>.jl
./export/user_<target>.jl
```

One tweet object per line — `id`, `url`, `author`, `text`, `ctime`. Existing
ids are read back before each run, so a re-run appends only what is new.

### Requirements

Chrome or Chromium on PATH; Selenium drives it through webdriver. A
headless run still needs the browser installed.

