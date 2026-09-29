# Codex sources

Read-only. Codex scope = absolute CWD. `CODEX_HOME` defaults to `~/.codex`;
use `$CODEX_HOME` only when it is set.

1. **Prompt history** — `${CODEX_HOME:-~/.codex}/history.jsonl`: JSONL with
   prompt text and session ids. Grep first, then parse the matching lines
   for `session_id`, `ts`, `text`.
2. **Session traces** — `${CODEX_HOME:-~/.codex}/sessions/**/*.jsonl`. Prefer
   traces whose `session_meta.payload.cwd` is the current CWD; when the
   topic spans projects, search all. Lines are JSON events: `session_meta`,
   `response_item` messages, `function_call` / `function_call_output`.
3. **State index** — read-only `SELECT` on
   `${CODEX_HOME:-~/.codex}/state_*.sqlite` (the file with a `threads`
   table) for recent thread titles and `rollout_path` before opening large
   traces. NEVER modify SQLite files.
4. **Generated memories** — `${CODEX_HOME:-~/.codex}/memories/`: helpful
   recall, not authoritative rules.

NEVER read credential or cache files (`auth.json`, logs, app caches,
keyrings) — only history, sessions, state indexes and memory files.

```bash
rg -n -i --fixed-strings '<query>' ~/.codex/history.jsonl
rg -n -i --fixed-strings '<query>' ~/.codex/sessions
sqlite3 ~/.codex/state_5.sqlite "select id,cwd,datetime(updated_at,'unixepoch'),substr(title,1,100),rollout_path from threads where cwd = '<cwd>' order by updated_at desc limit 10;"
jq -r 'select(.type=="session_meta") | .payload | {id,session_id,cwd,originator,cli_version,thread_source}' ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
```

If `jq` is unavailable, use `rg` plus targeted line reads. ALWAYS report
the trace path and `cwd` for each match.
