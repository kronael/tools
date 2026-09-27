# tg-fetch

Telegram collectors — single-file PEP 723 scripts, `uv run` resolves
`telethon` automatically. Rerun either one to collect what is new.

- `main.py` — message archiver, resumable
- `users.py` — group participants snapshot

## Run

Credentials live in the environment. Groups are arguments. There is no config
file.

```sh
export TELEGRAM_API_ID=12345678        # https://my.telegram.org/apps
export TELEGRAM_API_HASH=abcdef…
export TELEGRAM_PHONE=+1234567890      # asks for the code on the first run

uv run main.py some_group -1005125571890
uv run users.py some_group
```

`TELEGRAM_BOT_TOKEN` replaces `TELEGRAM_PHONE` for bot auth. **A bot cannot
read group history** — use a user account to backfill old messages.

A group is a username or a numeric id. A digits-only argument reaches Telegram
as an integer; a name reaches it as a string, with a leading `@` stripped. A
supergroup id must already carry its `-100` prefix, because a guessed prefix
resolves the wrong chat.

Both scripts share one session file (`./tmp/session.session`), so the code is
asked for once per account, not once per group.

## Output

`./tmp/tg_<group>.jl` (messages) — one JSON message per line:

```json
{"id": 42, "date": "2026-01-15T12:34:56+00:00", "sender_id": 123, "text": "...", "reply_to_msg_id": null, "fwd_from": false, "media": null}
```

`./tmp/tg_<group>_users.jl` (participants) — one user per line:

```json
{"id": 123, "username": "alice", "first_name": "Alice", "last_name": null, "is_bot": false, "is_deleted": false, "phone": null}
```

Delete `./tmp/session.session` to force re-auth.

## Rerun

`main.py` reads `./tmp/tg_<group>.jl`, picks the max `id`, and fetches with
`min_id=<last>` in chronological order. Every message is flushed before the
next is fetched, so a crash costs nothing already written.

`users.py` overwrites — group membership is a snapshot, not a log.

## Limits

Telegram throttles aggressive collectors. The scripts do not rate-limit
explicitly; Telethon's flood-wait handler does it. For a fresh archive of a
busy group, expect hours.
