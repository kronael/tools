#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["aiohttp"]
# ///
"""Fetch X posts through the FxTwitter mirror, as JSONL.

x.com answers 402 to a plain fetch. api.fxtwitter.com answers the same post
without a key, so every read here goes through the mirror.

The mirror resolves a post you can name. It exposes no timeline and no search,
so this tool takes post ids or urls; it cannot discover new posts by itself.
"""

import argparse
import asyncio
import dataclasses
import json
import logging
import re
import sys

import aiohttp

log = logging.getLogger(__name__)

MIRROR = "https://api.fxtwitter.com"
STATUS_PATH = re.compile(r"status(?:es)?/(\d+)")
BARE_ID = re.compile(r"^\d+$")


@dataclasses.dataclass(frozen=True, slots=True)
class Post:
    id: str
    author: str
    created_at: str
    text: str
    likes: int
    retweets: int
    replies: int
    views: int
    url: str


@dataclasses.dataclass(frozen=True, slots=True)
class Failure:
    ref: str
    reason: str


def parse_post_id(ref: str) -> str:
    """Pull the numeric post id out of a url or accept a bare id."""
    match = STATUS_PATH.search(ref)
    if match:
        return match.group(1)
    if BARE_ID.match(ref.strip()):
        return ref.strip()
    raise ValueError(f"no post id in {ref!r}")


def build_post(payload: dict) -> Post:
    tweet = payload["tweet"]
    return Post(
        id=str(tweet["id"]),
        author=tweet.get("author", {}).get("screen_name", ""),
        created_at=tweet.get("created_at", ""),
        text=tweet.get("text", ""),
        likes=tweet.get("likes", 0),
        retweets=tweet.get("retweets", 0),
        replies=tweet.get("replies", 0),
        views=tweet.get("views") or 0,
        url=tweet.get("url", ""),
    )


async def fetch_post(session: aiohttp.ClientSession, ref: str) -> Post | Failure:
    try:
        post_id = parse_post_id(ref)
    except ValueError as exc:
        return Failure(ref=ref, reason=str(exc))

    url = f"{MIRROR}/i/status/{post_id}"
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return Failure(ref=ref, reason=f"http {response.status}")
            payload = await response.json(content_type=None)
    except aiohttp.ClientError as exc:
        return Failure(ref=ref, reason=f"{type(exc).__name__}: {exc}")
    except asyncio.TimeoutError:
        return Failure(ref=ref, reason="timeout")

    if payload.get("code") != 200 or "tweet" not in payload:
        return Failure(ref=ref, reason=payload.get("message", "no post in reply"))
    return build_post(payload)


async def fetch_all(refs: list[str], timeout_s: float) -> list[Post | Failure]:
    timeout = aiohttp.ClientTimeout(total=timeout_s)
    # trust_env picks up HTTPS_PROXY; the sloth container reaches the mirror
    # only through its squid proxy.
    async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
        return list(await asyncio.gather(*(fetch_post(session, ref) for ref in refs)))


def read_refs(args: argparse.Namespace) -> list[str]:
    if args.refs:
        return args.refs
    return [line.strip() for line in sys.stdin if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("refs", nargs="*", help="post urls or ids; omit to read stdin")
    parser.add_argument("--timeout", type=float, default=20.0, help="seconds per request")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )

    refs = read_refs(args)
    if not refs:
        log.error("no post references given")
        return 2

    results = asyncio.run(fetch_all(refs, args.timeout))

    failures = 0
    for result in results:
        if isinstance(result, Failure):
            failures += 1
            log.error("%s: %s", result.ref, result.reason)
            continue
        print(json.dumps(dataclasses.asdict(result), ensure_ascii=False))

    if failures:
        log.error("%d of %d references failed", failures, len(results))
    return 1 if failures == len(results) else 0


if __name__ == "__main__":
    sys.exit(main())
