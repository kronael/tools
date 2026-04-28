# tg-fetch

Telegram channel/group archiver. Streams every message into a JSONL file
and resumes from the last archived `id` on the next run.

## Run

```sh
cp config.example.toml my-group.toml
$EDITOR my-group.toml          # fill api_id, api_hash, group, phone
uv run main.py my-group.toml
```

Single-file PEP 723 script — `uv run` resolves `telethon` automatically,
no venv to manage.

## Config

```toml
api_id    = 12345678                          # https://my.telegram.org/apps
api_hash  = "abcdef…"
group     = "some_group"                      # username (no @) or numeric id
phone     = "+1234567890"                     # user auth — OTP prompted on stdin
# bot_token = "123:AAF…"                      # OR bot auth (no read history)
```

Pick exactly one of `phone` or `bot_token`. **Bot auth cannot read group
history** — use a user account if you want to backfill old messages.

## Output

`./tmp/tg_<group>.jl` — one JSON message per line:

```json
{"id": 42, "date": "2026-01-15T12:34:56+00:00", "sender_id": 123, "text": "...", "reply_to_msg_id": null, "fwd_from": false, "media": null}
```

Telethon session: `./tmp/session_<group>.session` — keeps you logged in
across runs. Delete to force re-auth.

## Resume

Reads `./tmp/tg_<group>.jl`, picks the max `id`, fetches with
`min_id=<last>` in chronological order. Crash-safe: every message is
flushed before the next is fetched (append mode).

## Limits

Telegram throttles aggressive scrapers. The script doesn't rate-limit
explicitly — Telethon's flood-wait handler kicks in automatically. For a
fresh archive of a busy group, expect hours.
