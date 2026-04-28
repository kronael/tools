# /// script
# requires-python = ">=3.11"
# dependencies = ["telethon"]
# ///

import sys
import json
import tomllib
import asyncio
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.types import Message


def load_cfg(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def out_path(group: str) -> Path:
    p = Path("./tmp")
    p.mkdir(exist_ok=True)
    return p / f"tg_{group}.jl"


def last_id(p: Path) -> int:
    if not p.exists():
        return 0
    last = 0
    with open(p) as f:
        for line in f:
            try:
                last = max(last, json.loads(line.strip())["id"])
            except (json.JSONDecodeError, KeyError):
                pass
    return last


def msg_to_dict(m: Message) -> dict:
    return {
        "id": m.id,
        "date": m.date.isoformat() if m.date else None,
        "sender_id": m.sender_id,
        "text": m.text,
        "reply_to_msg_id": m.reply_to_msg_id,
        "fwd_from": bool(m.fwd_from),
        "media": type(m.media).__name__ if m.media else None,
    }


async def run(cfg: dict) -> None:
    group = cfg["group"]
    p = out_path(group)
    resume_id = last_id(p)

    session = f"./tmp/session_{group}"
    client = TelegramClient(session, int(cfg["api_id"]), cfg["api_hash"])

    if "bot_token" in cfg:
        await client.start(bot_token=cfg["bot_token"])
    else:
        await client.start(phone=lambda: cfg["phone"])

    async with client:
        entity = await client.get_entity(group)
        total = (await client.get_messages(entity, limit=1)).total
        print(f"group total={total}, resuming after id={resume_id}")

        fetched = 0
        with open(p, "a") as f:
            async for m in client.iter_messages(entity, reverse=True, min_id=resume_id):
                if not isinstance(m, Message):
                    continue
                f.write(json.dumps(msg_to_dict(m)) + "\n")
                fetched += 1
                if fetched % 200 == 0:
                    done = resume_id + fetched
                    pct = round(100 * done / total) if total else "?"
                    print(f"fetched {fetched} ({pct}%)")

    print(f"done — {fetched} new messages -> {p}")


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: uv run main.py <config.toml>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(load_cfg(sys.argv[1])))


if __name__ == "__main__":
    main()
