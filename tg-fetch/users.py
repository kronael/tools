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


def load_cfg(config_path: str, keys_path: str) -> dict:
    """Config first, keys second. The two files stay apart on disk."""
    with open(config_path, 'rb') as f:
        cfg = tomllib.load(f)
    with open(keys_path, 'rb') as f:
        cfg.update(tomllib.load(f))
    return cfg


def out_path(group: str) -> Path:
    p = Path('./tmp')
    p.mkdir(exist_ok=True)
    return p / f'tg_{group}_users.jl'


def resolve_group(group: str | int) -> str | int:
    """Telethon takes an int for a chat id and a string for a username.

    A supergroup id must already carry its -100 prefix; nothing is added here.
    """
    if isinstance(group, int):
        return group
    text = group.strip()
    if text.lstrip('-').isdigit():
        return int(text)
    return text.removeprefix('@')


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
        entity = await client.get_entity(resolve_group(group))
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
    if len(sys.argv) < 3:
        print('usage: uv run users.py <config.toml> <keys.toml>', file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(load_cfg(sys.argv[1], sys.argv[2])))


if __name__ == '__main__':
    main()
