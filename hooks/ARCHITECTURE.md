# Hooks Architecture

## Overview

```
User Prompt ──> UserPromptSubmit ──> prompt_nudge.py (phrase → command/agent)
                                 ──> local.py        (LOCAL.md on first prompt)
                                 ──> reclaude.py     (RECLAUDE.md on first prompt)

Tool use ──────> PreToolUse ──> pretool_nudge.py (file info / unsafe block)

Claude stops ──> Stop ──> stop.py (commit + diary warnings)
                      ──> memory_nudge.py (session memory, throttled once/session)

Compaction ──> PreCompact ──> local.py         (LOCAL.md + RULES)
                          ──> reclaude.py      (RECLAUDE.md + preservation note)
                          ──> memory_nudge.py  (session memory, unconditional)
```

## Components

### prompt_nudge.py (UserPromptSubmit)

**Input:** JSON with `prompt`, `session_id`, and `cwd` fields.
**Output:** `{"ok": true, "systemMessage": "..."}` or silent exit.

**Flow:**
1. Skip meta prompts (hook/agent debugging) to avoid self-interference.
2. On the first non-empty prompt of a session, append `RESOLVE_NUDGE` (run
   `/resolve` to triage before acting), unless the prompt already invokes
   `/resolve`. Continuations stay silent.
3. If prompt mentions `todo|readme|changelog|spec|architecture|*.md`,
   append `DOCS_RULES`.
4. Match explicit Codex second-opinion phrases in Claude only: `ask codex`,
   `oracle`, and `second opinion`.
5. Match model escalation only when explicit: `/fable`, `use fable`,
   `spawn fable`, `/opus`, etc.
6. Tokenise prompt and exact-match words against `AGENT_KEYWORDS`. A trailing
   `s` singular/plural alias is allowed; edit-distance matching is not.
7. If prompt contains `commit`, append `COMMIT_RULES` and short-circuit;
   otherwise emit the first exact route as `info`.

**State:** `$cwd/.claude/tmp/resolve-nudge-{session_id}` marks that a session's
first prompt has been seen. An unwritable state dir falls back to silence, never
a per-prompt nudge.

**Keyword table:** see README.md.

### local.py (UserPromptSubmit + PreCompact)

**Input:** JSON with `prompt`, `hook_event`, `session_id`, `cwd`.
**Output:** `{"ok": true, "systemMessage": "<content>"}` or silent.

**Flow:**
1. First prompt per session (tracked via `$cwd/.claude/tmp/local-{sid}`)
   or `PreCompact` event → inject `~/.claude/LOCAL.md` and `$cwd/LOCAL.md`
   contents.
2. On continue/recap keywords (respecting negation), append `RULES`.
3. On `PreCompact`, always append `RULES`.

### reclaude.py (UserPromptSubmit + PreCompact)

**Input:** JSON with `prompt`, `hook_event`.
**Output:** `{"ok": true, "systemMessage": "<RECLAUDE.md>"}` or silent.

**Flow:**
1. Reads `~/.claude/RECLAUDE.md`; silent exit if missing.
2. Skip on negation (`don't continue`, etc).
3. Inject on `PreCompact` or continue/recap keywords.
4. On `PreCompact`, append a preservation note so the content survives
   compaction.

### pretool_nudge.py (PreToolUse)

**Input:** JSON with `tool_name` and `tool_input`.
**Output:** `{"decision": "block", "reason": "..."}`, file-skill context, or
silent.

**Flow:**
1. For shell tools (`Bash`, Codex `exec_command`), block true unsafe commands:
   push, amend, hard reset, broad add, `--no-verify`, `rm -rf`, and recursive
   Codex execution.
2. For file tools, extract `file_path`, `notebook_path`, or explicit
   `apply_patch` file headers.
3. Emit `info` language-skill context from the file extension, or from the
   basename for `Makefile`/`Dockerfile`/`docker-compose.yml`-style files and
   `SKILL.md`/`CLAUDE.md`/`AGENTS.md` (→ `/wisdom`). Unknown or unreliable
   paths stay silent.

### stop.py (Stop)

**Input:** JSON with `cwd`, `stop_hook_active`.
**Output:** `{"decision": "block", "reason": "..."}` on plain `Stop`, or
`hookSpecificOutput.additionalContext` when re-invoked via `post_tool_nudge.sh`
on `PostToolUse`; silent otherwise. On `Stop`, `decision: block` forces one
more turn so Claude can see `reason` and act on it — a hygiene nudge, not an
unsafe-action block like PreToolUse's.

**Flow:**
1. Bail early if `stop_hook_active` is set — prevents an infinite nudge loop,
   since step 4's block would otherwise re-trigger this same hook.
2. Check `git status --porcelain -uno`; if dirty, append a commit nudge
   with `git diff --stat`.
3. If the repo has a `.diary/`, check for today's `YYYYMMDD.md` (UTC).
   Missing or >1h stale → append a diary nudge.
4. Emit the combined message if any nudges accumulated.

No LLM call. NEVER pushes. The hook does not write diary headers.

### memory_nudge.py (PreCompact + Stop)

**Input:** JSON with `cwd`, `session_id`, `stop_hook_active`, and hook event
identity (`hook_event`/`hook_event_name`/`hookEventName`).
**Output:** `PreCompact` → `{"ok": true, "systemMessage": "..."}` (same idiom
as local.py/reclaude.py). `Stop` → `hookSpecificOutput.additionalContext`
(same idiom as stop.py's PostToolUse path).

**Flow:**
1. Bail early if `stop_hook_active` is set.
2. On `PreCompact`: always emit the memory-review nudge, then write a
   per-session `done` marker so the `Stop` fallback below doesn't also fire.
3. On `Stop`: if the `done` marker exists, stay silent. Otherwise, on first
   `Stop` of the session, write a `start` marker and stay silent (too early
   to judge). On later `Stop` calls, once `now - start >= 1800s` (30 min) OR
   at least 3 `Stop`s have occurred, emit the nudge once and write the `done`
   marker — the count path covers short but multi-turn sessions that never
   reach the 30-min mark.

Deliberately much lower frequency than `stop.py`'s diary/commit nudges: at
most once via `PreCompact` (rare) plus at most once via the `Stop` fallback
(gated to 30+ min sessions), vs. `stop.py`'s recurring hourly/10-min cadence.

## Data Flow

### UserPromptSubmit

```
stdin:
{
  "prompt": "improve the error handling",
  "hook_event": "UserPromptSubmit",
  "session_id": "abc123",
  "cwd": "/project"
}

stdout (prompt_nudge.py match):
{"ok": true, "systemMessage": "info: @improve matches this request."}
```

### Stop

```
stdin:
{
  "cwd": "/project",
  "stop_hook_active": false
}

stdout (dirty tree + stale diary):
{
  "decision": "block",
  "reason": "Uncommitted changes detected.\n<diff stat>\n...Run /commit...\nDiary not updated in over an hour (now <hhmm>). Run /diary deliberately if there is work to record."
}
```

See `stop.py`'s component section above for what this `decision: block` does.

## Error Handling

All hooks catch `json.JSONDecodeError`, `EOFError`, `ValueError` and bail
with `sys.exit(0)` so a broken payload never blocks the session. File I/O
errors in `local.py` are swallowed for the same reason.

## Extension Points

**Add a new keyword route** — edit `AGENT_KEYWORDS` in `prompt_nudge.py` and the
table in `README.md`.

**Add a new stop nudge** — append to the `parts` list in `stop.py`. Keep
checks cheap (no network, no LLM) and guard with a path/directory probe
so the hook stays silent in projects that don't use the feature.

**Add a new injected file** — model it on `local.py`/`reclaude.py`: read
on first prompt + `PreCompact`, respect negation, append rules on
compaction.
