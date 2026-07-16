---
name: recall-memories
description: Search diary, memory, and session history. NOT for writing entries (use diary).
when_to_use: "what did we decide, recall, find context from a prior session"
user-invocable: true
arg: <question>
---

# Recall Memories

Read-only search across Claude diary, Claude memory/session transcripts, and
Codex local history, session traces, and generated memories.

## Protocol

### Step 1 — Scope

Slug = absolute CWD with `/` → `-`. Current-project slug is primary;
other slugs under `~/.claude/projects/` are siblings.

Codex scope = absolute CWD. Codex session traces carry `payload.cwd` in their
`session_meta` record and are stored under `~/.codex/sessions/`. `CODEX_HOME`
defaults to `~/.codex`; use `$CODEX_HOME` only when it is explicitly set.

### Step 2 — Search (spawn Explore subagent, parallel)

ALWAYS search the current project. ALWAYS ALSO search siblings in the
same pass when the topic plausibly spans projects (cross-cutting tool,
shared skill, vague "where did we discuss X") — NEVER make the user
re-ask to widen scope.

1. **Claude diary** — `Glob` `<cwd>/.diary/*.md`. Cross-project: ALSO `Glob`
   `~/wk/*/.diary/*.md`. Grep `summary:` and body.
2. **Claude memory** — Read `~/.claude/projects/<slug>/memory/MEMORY.md` and
   sibling `.md` files. Cross-project: ALSO `Glob`
   `~/.claude/projects/*/memory/*.md`.
3. **Claude sessions** — `Glob` `~/.claude/projects/<slug>/*.jsonl`, sort by
   mtime, read 2-3 newest. Cross-project: ALSO `Glob`
   `~/.claude/projects/*/*.jsonl`, sort by mtime, grep the newest
   handful. Lines are JSON messages; filter on `role` and content.
4. **Codex prompt history** — Search `${CODEX_HOME:-~/.codex}/history.jsonl`
   when present. It is JSONL with prompt text and session ids; grep first,
   then parse matching lines for `session_id`, `ts`, and `text`.
5. **Codex sessions** — Search `${CODEX_HOME:-~/.codex}/sessions/**/*.jsonl`
   when present. First prefer current-CWD traces by `session_meta.payload.cwd`;
   if the topic plausibly spans projects, also search all Codex session traces.
   Lines are JSON events; filter to `session_meta`, `response_item` messages,
   and relevant `function_call` / `function_call_output` records. Always report
   the trace path and `cwd` for matches.
6. **Codex state index** — If `sqlite3` is available, use read-only `SELECT`
   queries against `${CODEX_HOME:-~/.codex}/state_*.sqlite` to find recent
   thread titles and `rollout_path` values for the current CWD before opening
   large traces. Never modify SQLite files.
7. **Codex memories** — Search `${CODEX_HOME:-~/.codex}/memories/` when it
   contains files. These are generated memory summaries and evidence. Treat
   them as helpful recall, not authoritative rules.

Do not inspect Codex credential or cache files for recall (`auth.json`, logs,
app caches, keyrings). Only read history, sessions, state indexes, and memory
files needed for the user's question. Keep all Codex searches read-only.

ALWAYS name the originating project slug when reporting sibling matches.
For Codex matches, ALWAYS name the originating `cwd` and session/trace path.

### Step 3 — Deliberate

In `<think>`: list sources, state what each says, identify gaps, verdict
(use or research fresh).

ALWAYS verify matches against current repo state (git log, file
contents). ALWAYS mark stale findings explicitly — NEVER act on
outdated decisions.

### Useful Codex Commands

Use these as read-only starting points; narrow the query before reading large
JSONL traces.

```bash
rg -n -i --fixed-strings '<query>' ~/.codex/history.jsonl
rg -n -i --fixed-strings '<query>' ~/.codex/sessions
sqlite3 ~/.codex/state_5.sqlite "select id,cwd,datetime(updated_at,'unixepoch'),substr(title,1,100),rollout_path from threads where cwd = '<cwd>' order by updated_at desc limit 10;"
jq -r 'select(.type=="session_meta") | .payload | {id,session_id,cwd,originator,cli_version,thread_source}' ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
```

If multiple `state_*.sqlite` files exist, inspect schemas first and choose the
one with a `threads` table. If `jq` is unavailable, use `rg` plus targeted line
reads.

## Triggers

- "what did we decide about X?" — diary + sessions
- "what's the status of Y?" — diary summary
- "what was wrong with Z?" — diary + sessions
- Technical question about this project — diary + memory
- "what did Codex do/say about X?" — Codex history + sessions + memories
