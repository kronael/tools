# /// script
# requires-python = ">=3.14"
# dependencies = ["telethon"]
# ///

"""Snapshot Telegram group participants to JSONL. Rerun to refresh.

usage: uv run users.py <group> [group ...]

Credentials come from the environment, the same ones main.py reads:
  TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE or TELEGRAM_BOT_TOKEN
"""

import asyncio
import json
import sys
from pathlib import Path

from main import build_client
from main import resolve_group
from main import start_client
from telethon import TelegramClient
from telethon.tl.types import User


def out_path(group: str) -> Path:
    p = Path('./tmp')
    p.mkdir(exist_ok=True)
    return p / f'tg_{group}_users.jl'


def user_to_dict(u: User) -> dict:
    return {
        'id': u.id,
        'username': u.username,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'is_bot': bool(u.bot),
        'is_deleted': bool(u.deleted),
        'phone': u.phone,
    }


async def collect_group(client: TelegramClient, group: str) -> int:
    """Overwrite the group's snapshot. Membership is a state, not a log."""
    p = out_path(group)
    entity = await client.get_entity(resolve_group(group))

    n = 0
    with open(p, 'w') as f:  # noqa: ASYNC230
        async for u in client.iter_participants(entity):
            if not isinstance(u, User):
                continue
            f.write(json.dumps(user_to_dict(u)) + '\n')
            n += 1
            if n % 500 == 0:
                print(f'{group}: fetched {n}')

    print(f'{group}: {n} users -> {p}')
    return n


async def run(groups: list[str]) -> None:
    client = build_client()
    await start_client(client)

    total = 0
    async with client:
        for group in groups:
            total += await collect_group(client, group)

    print(f'done — {total} users across {len(groups)} groups')


def main() -> None:
    groups = sys.argv[1:]
    if not groups:
        print('usage: uv run users.py <group> [group ...]', file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(groups))


if __name__ == '__main__':
    main()
