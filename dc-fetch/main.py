# /// script
# requires-python = ">=3.14"
# dependencies = ["discum", "click"]
# ///

import json
import os
import sys
import time

import click
import discum


def get_bot():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        click.echo("error: DISCORD_TOKEN env var required", err=True)
        sys.exit(1)
    return discum.Client(token=token, log=False)


def last_msg_id(path):
    if not os.path.exists(path):
        return None
    last = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                last = json.loads(line).get("id")
    return last


def dump_channel(bot, ch_id, ch_name, outdir, delay=0.5, limit=None):
    os.makedirs(outdir, exist_ok=True)
    safe = ch_name.replace("/", "_").replace(" ", "_")
    path = os.path.join(outdir, f"{safe}_{ch_id}.jsonl")
    after = last_msg_id(path) or "0"
    total = 0
    if after != "0":
        click.echo(f"{ch_name}: resuming after {after}", err=True)
    with open(path, "a") as f:
        while limit is None or total < limit:
            params = {"limit": 100, "after": after}
            url = f"https://discord.com/api/v9/channels/{ch_id}/messages"
            msgs = bot.s.get(url, params=params).json()
            if not isinstance(msgs, list) or not msgs:
                break
            msgs.sort(key=lambda m: m["id"])
            for m in msgs:
                f.write(json.dumps(m) + "\n")
            f.flush()
            total += len(msgs)
            after = msgs[-1]["id"]
            click.echo(f"{ch_name}: {total} messages", err=True)
            if len(msgs) < 100:
                break
            time.sleep(delay)
    click.echo(f"{ch_name}: done ({total} new)", err=True)
    return total


def fetch_threads(bot, guild_id, text_channels):
    threads = []
    r = bot.s.get(f"https://discord.com/api/v9/guilds/{guild_id}/threads/active")
    if r.status_code == 200:
        threads.extend(r.json().get("threads", []))
    ch_ids = {str(c["id"]) for c in text_channels}
    for i, ch_id in enumerate(ch_ids):
        click.echo(f"fetching archived threads {i+1}/{len(ch_ids)}...", err=True)
        before = None
        while True:
            url = f"https://discord.com/api/v9/channels/{ch_id}/threads/archived/public"
            r = bot.s.get(url, params={"before": before} if before else {})
            if r.status_code != 200:
                break
            data = r.json()
            batch = data.get("threads", [])
            threads.extend(batch)
            if not data.get("has_more") or not batch:
                break
            before = batch[-1].get("thread_metadata", {}).get("archive_timestamp")
            time.sleep(0.5)
    seen = {}
    for t in threads:
        seen.setdefault(t["id"], t)
    return list(seen.values())


@click.group()
def main():
    pass


@main.command()
@click.argument("channel_id")
@click.option("-o", "--output", default="./export/")
@click.option("-r", "--rate", type=float, default=2.0)
@click.option("-l", "--limit", type=int, default=None)
def channel(channel_id, output, rate, limit):
    """Dump a single channel."""
    bot = get_bot()
    dump_channel(bot, channel_id, channel_id, output, delay=1.0 / rate, limit=limit)


@main.command()
@click.argument("guild_id")
@click.option("-o", "--output", default="./export/")
@click.option("--list", "list_only", is_flag=True)
@click.option("-r", "--rate", type=float, default=2.0)
@click.option("-l", "--limit", type=int, default=None)
def guild(guild_id, output, list_only, rate, limit):
    """Dump all text channels in a guild."""
    bot = get_bot()
    channels = bot.getGuildChannels(guild_id).json()
    if not isinstance(channels, list):
        raise click.ClickException(f"failed to get channels: {channels}")
    text = sorted(
        [c for c in channels if c.get("type") in (0, 5)],
        key=lambda c: c.get("position", 0),
    )
    threads = fetch_threads(bot, guild_id, text)
    if list_only:
        for c in text:
            kind = "announcement" if c.get("type") == 5 else "text"
            click.echo(f"{c['id']}\t{c['name']}\t{kind}")
        for t in threads:
            click.echo(f"{t['id']}\t{t['name']}\tthread\tparent={t.get('parent_id')}")
        return
    delay = 1.0 / rate
    gdir = os.path.join(output, str(guild_id))
    remaining = limit
    for c in text:
        n = dump_channel(bot, c["id"], c["name"], gdir, delay=delay, limit=remaining)
        if remaining is not None:
            remaining -= n
            if remaining <= 0:
                break
        time.sleep(delay)
    if remaining is None or remaining > 0:
        for t in threads:
            name = f"{t.get('parent_id', 'unknown')}_{t['name']}"
            n = dump_channel(bot, t["id"], name, gdir, delay=delay, limit=remaining)
            if remaining is not None:
                remaining -= n
                if remaining <= 0:
                    break
            time.sleep(delay)


if __name__ == "__main__":
    main()
