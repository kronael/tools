# /// script
# requires-python = ">=3.14"
# dependencies = ["telethon"]
# ///

"""Archive Telegram group messages to JSONL. Rerun to collect what is new.

usage: uv run main.py <group> [group ...]

Credentials come from the environment:
  TELEGRAM_API_ID, TELEGRAM_API_HASH   https://my.telegram.org/apps
  TELEGRAM_PHONE                       user auth, asks for the code once
  TELEGRAM_BOT_TOKEN                   bot auth instead, cannot read history
"""

import asyncio
import contextlib
import json
import os
import sys
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import Message


def out_path(group: str) -> Path:
    p = Path('./tmp')
    p.mkdir(exist_ok=True)
    return p / f'tg_{group}.jl'


def last_id(p: Path) -> int:
    if not p.exists():
        return 0
    last = 0
    with open(p) as f:
        for line in f:
            with contextlib.suppress(json.JSONDecodeError, KeyError):
                last = max(last, json.loads(line.strip())['id'])
    return last


def resolve_group(group: str) -> str | int:
    """Telethon takes an int for a chat id and a string for a username.

    A supergroup id must already carry its -100 prefix; nothing is added here.
    """
    text = group.strip()
    if text.lstrip('-').isdigit():
        return int(text)
    return text.removeprefix('@')


def build_client() -> TelegramClient:
    """Read the credentials from the environment, or say what is missing."""
    api_id = os.environ.get('TELEGRAM_API_ID', '')
    api_hash = os.environ.get('TELEGRAM_API_HASH', '')
    if not api_id or not api_hash:
        print(
            'set TELEGRAM_API_ID and TELEGRAM_API_HASH from https://my.telegram.org/apps',
            file=sys.stderr,
        )
        sys.exit(1)
    Path('./tmp').mkdir(exist_ok=True)
    return TelegramClient('./tmp/session', int(api_id), api_hash)


async def start_client(client: TelegramClient) -> None:
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    phone = os.environ.get('TELEGRAM_PHONE', '')
    if token:
        await client.start(bot_token=token)
        return
    if not phone:
        print('set TELEGRAM_PHONE, or TELEGRAM_BOT_TOKEN for a bot', file=sys.stderr)
        sys.exit(1)
    await client.start(phone=lambda: phone)


def msg_to_dict(m: Message) -> dict:
    return {
        'id': m.id,
        'date': m.date.isoformat() if m.date else None,
        'sender_id': m.sender_id,
        'text': m.text,
        'reply_to_msg_id': m.reply_to_msg_id,
        'fwd_from': bool(m.fwd_from),
        'media': type(m.media).__name__ if m.media else None,
    }


async def collect_group(client: TelegramClient, group: str) -> int:
    """Append every message newer than the last one already on disk."""
    p = out_path(group)
    resume_id = last_id(p)

    entity = await client.get_entity(resolve_group(group))
    total = (await client.get_messages(entity, limit=1)).total
    print(f'{group}: total={total}, resuming after id={resume_id}')

    fetched = 0
    with open(p, 'a') as f:  # noqa: ASYNC230
        async for m in client.iter_messages(entity, reverse=True, min_id=resume_id):
            if not isinstance(m, Message):
                continue
            f.write(json.dumps(msg_to_dict(m)) + '\n')
            fetched += 1
            if fetched % 200 == 0:
                done = resume_id + fetched
                pct = round(100 * done / total) if total else '?'
                print(f'{group}: fetched {fetched} ({pct}%)')

    print(f'{group}: {fetched} new -> {p}')
    return fetched


async def run(groups: list[str]) -> None:
    client = build_client()
    await start_client(client)

    total = 0
    async with client:
        for group in groups:
            total += await collect_group(client, group)

    print(f'done — {total} new messages across {len(groups)} groups')


def main() -> None:
    groups = sys.argv[1:]
    if not groups:
        print('usage: uv run main.py <group> [group ...]', file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(groups))


if __name__ == '__main__':
    main()
