# tg-fetch

Telegram channel/group scrapers — single-file PEP 723 scripts, `uv run`
resolves `telethon` automatically.

- `main.py` — message archiver, resumable
- `users.py` — group participants snapshot

## Run

```sh
cp config.example.toml my-group.toml
$EDITOR my-group.toml          # fill api_id, api_hash, group, phone
uv run main.py my-group.toml    # messages
uv run users.py my-group.toml   # participants
```

Both share the same session file (`./tmp/session_<group>.session`) — no
re-auth between them.

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

`./tmp/tg_<group>.jl` (messages) — one JSON message per line:

```json
{"id": 42, "date": "2026-01-15T12:34:56+00:00", "sender_id": 123, "text": "...", "reply_to_msg_id": null, "fwd_from": false, "media": null}
```

`./tmp/tg_<group>_users.jl` (participants) — one user per line:

```json
{"id": 123, "username": "alice", "first_name": "Alice", "last_name": null, "is_bot": false, "is_deleted": false, "phone": null}
```

Telethon session: `./tmp/session_<group>.session` — keeps you logged in
across runs. Delete to force re-auth.

## Resume

`main.py` reads `./tmp/tg_<group>.jl`, picks the max `id`, fetches with
`min_id=<last>` in chronological order. Crash-safe: every message is
flushed before the next is fetched (append mode).

`users.py` overwrites — group membership is a snapshot, not append-only.

## Limits

Telegram throttles aggressive scrapers. The script doesn't rate-limit
explicitly — Telethon's flood-wait handler kicks in automatically. For a
fresh archive of a busy group, expect hours.
