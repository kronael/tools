# /// script
# requires-python = ">=3.14"
# dependencies = ["telethon"]
# ///

import asyncio
import json
import sys
import tomllib
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import User


def load_cfg(path: str) -> dict:
    with open(path, 'rb') as f:
        return tomllib.load(f)


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


async def run(cfg: dict) -> None:
    group = cfg['group']
    p = out_path(group)

    session = f'./tmp/session_{group}'
    client = TelegramClient(session, int(cfg['api_id']), cfg['api_hash'])

    if 'bot_token' in cfg:
        await client.start(bot_token=cfg['bot_token'])
    else:
        await client.start(phone=lambda: cfg['phone'])

    async with client:
        entity = await client.get_entity(group)
        n = 0
        with open(p, 'w') as f:  # noqa: ASYNC230
            async for u in client.iter_participants(entity):
                if not isinstance(u, User):
                    continue
                f.write(json.dumps(user_to_dict(u)) + '\n')
                n += 1
                if n % 500 == 0:
                    print(f'fetched {n}')

    print(f'done — {n} users -> {p}')


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: uv run users.py <config.toml>', file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(load_cfg(sys.argv[1])))


if __name__ == '__main__':
    main()
