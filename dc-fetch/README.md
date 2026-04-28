# dc-fetch

Discord channel/guild archiver. Streams messages into JSONL files and
resumes from the last archived message id on the next run.

## Auth

```sh
export DISCORD_TOKEN="…"          # user token, NOT a bot token
```

Uses [discum](https://github.com/Merubokkusu/Discord-S.C.U.M) which
impersonates a user client (selfbot). Bot tokens won't work for most
endpoints used here.

How to get the token: F12 in a logged-in Discord web client →
Network → look for `Authorization` header on any API request.

## Commands

Single-file PEP 723 script. Both forms below auto-resolve `discum` + `click`.

```sh
uv run main.py channel <channel_id>            # one channel
uv run main.py guild   <guild_id>              # all text channels + threads
uv run main.py guild   <guild_id> --list       # enumerate, don't dump
```

Common flags:

| flag | default | meaning |
|---|---|---|
| `-o, --output` | `./export/` | output root |
| `-r, --rate`   | `2.0`       | requests per second |
| `-l, --limit`  | unlimited   | stop after N messages total |

## Output

```
./export/<guild_id>/<channel_name>_<id>.jsonl
./export/<channel_id>/<channel_id>_<id>.jsonl   # for `channel` mode
```

One raw Discord message JSON per line — no transformation, full API
shape. Threads land alongside their parent channel files, named
`<parent_id>_<thread_name>_<thread_id>.jsonl`.

## Resume

Reads the existing JSONL, takes the last line's `id`, passes it as
`after=<id>` to the API. Re-runs only fetch new messages.

## Discovery

`guild --list` prints `id<TAB>name<TAB>kind[<TAB>parent]` for every
text channel, announcement channel, and active/archived public thread —
useful for picking a subset before committing to a full guild dump.

## Rate limits

Discord's per-route limit is 50/s for most endpoints; the default
`--rate 2.0` (= 0.5s sleep between batches of 100 messages) stays well
under. Crank it up if you're patient and want to be polite, down if
you're impatient and willing to retry on 429.
