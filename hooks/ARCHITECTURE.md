# Hooks Architecture

## Overview

```
User Prompt ──> UserPromptSubmit ──> prompt_nudge.py (keyword → command/agent)
                                 ──> local.py        (LOCAL.md on first prompt)

Tool call ──> PreToolUse  ──> pretool_nudge.py   (file info / unsafe block)
          ──> PostToolUse ──> post_tool_nudge.sh (periodic commit/diary nudge)

Claude stops ──> Stop ──> stop.py       (commit + diary block)
                      ──> memory_nudge.py (session memory, once/session fallback)

Compaction ──> PreCompact ──> local.py        (LOCAL.md + RULES)
                          ──> reclaude.py     (RECLAUDE.md + preservation note)
                          ──> memory_nudge.py (session memory, unconditional)
```

Claude event/matcher wiring is owned by `../settings-recommended.json`.
Codex event/matcher wiring is owned by `../codex-hooks.json`; every Codex hook
first runs through `codex_hook.py`.

## Components

### codex_hook.py (Codex adapter)

**Input:** Codex hook JSON, which may use Codex field names.
**Output:** delegated hook stdout.

**Flow:**
1. Normalize payload fields to the Claude hook shape:
   `cwd`, `session_id`, `hook_event`, `prompt`, `tool_name`, `tool_input`.
2. Dispatch to one installed target hook under `~/.claude/hooks/`.
3. Translate Claude output for Codex: strip Claude-only `ok`, promote
   `systemMessage` to `hookSpecificOutput.additionalContext` for prompt/tool
   hooks, and rewrite Kronael nudge refs from `/skill` to `@skill`.
4. For Codex `PreCompact`, suppress context-only `systemMessage` output because
   Codex only accepts block decisions for that event; forward
   `decision:block` if a hook emits one.
5. Forward Stop `decision:block` output after the same nudge-ref rewrite, so
   commit/diary nudges work in both runtimes.

This keeps the business logic in one hook implementation while allowing Codex
and Claude to use different lifecycle wiring.

### prompt_nudge.py (UserPromptSubmit)

**Input:** JSON with `prompt` field.
**Output:** `{"ok": true, "systemMessage": "..."}` or silent exit.

**Flow:**
1. Skip meta prompts (hook/agent debugging) to avoid self-interference.
2. If prompt mentions `todo|readme|changelog|spec|architecture|*.md`,
   append `DOCS_RULES`.
3. Match explicit Codex second-opinion phrases in Claude only: `ask codex`,
   `oracle`, and `second opinion`.
4. Match model escalation only when explicit: `/fable`, `use fable`,
   `spawn fable`, `/opus`, etc.
5. Tokenise prompt and exact-match words against `AGENT_KEYWORDS`. A trailing
   `s` singular/plural alias is allowed; edit-distance matching is not.
6. If prompt contains `commit`, append `COMMIT_RULES`; otherwise emit the
   first exact route as `info`.

**Routes:** `AGENT_KEYWORDS` dict in the source.
Codex sees matched Kronael routes as `@skill` instead of `/skill`.

### pretool_nudge.py (PreToolUse)

**Input:** JSON with `tool_name`, `tool_input` (`file_path`, `notebook_path`,
`command`, `cmd`, or `apply_patch` patch text), `session_id`.
**Output:** `{"decision": "block", "reason": "..."}`,
`hookSpecificOutput.additionalContext`, or silent.

**Flow:**
1. For shell tools (`Bash`, Codex `exec_command`), block true unsafe commands:
   push, amend, hard reset, broad add, no-verify commits, `rm -rf`, and
   recursive Codex execution inside Codex.
2. For file tools, extract `file_path`, `notebook_path`, or explicit
   `apply_patch` file headers.
3. Map path to a skill: special filenames first (`Makefile` → `/mk`,
   `Dockerfile`/compose/workflows → `/ops`), then extension via
   `EXT_SKILLS` (`.rs` → `/rs`, `.html` → `/htmx`, ...).
4. Dedupe per session+file via `$TMPDIR/claude-extnudge/{sid}.txt` so
   each nudge fires once.
5. Emit "Editing/reading <file> — follow <skill> conventions."
Codex sees `<skill>` as `@py`, `@go`, etc.

### post_tool_nudge.sh (PostToolUse)

**Input:** original hook payload; state in the current repo's git dir
(`post_tool_nudge`, ts + count).
**Output:** `stop.py`'s advisory `hookSpecificOutput` every 100 tool calls or
10 minutes, otherwise silent. Always exits 0 — never blocks a tool call.

**Flow:**
1. Increment the call counter.
2. At 100 calls or 600 s, reset state and pipe the original payload to
   `stop.py` with `KRONAEL_HOOK_EVENT=PostToolUse`, so the commit/diary nudge
   also fires mid-session as advisory context.

### local.py (UserPromptSubmit + PreCompact)

**Input:** JSON with `prompt`, `hook_event`, `session_id`, `cwd`.
**Output:** `{"ok": true, "systemMessage": "<content>"}` or silent.
Codex runs this through `codex_hook.py`; PreCompact context output is
suppressed there to avoid invalid Codex hook JSON.

**Flow:**
1. First prompt per session (tracked via `$cwd/.claude/tmp/local-{sid}`)
   or `PreCompact` event → inject `~/.claude/LOCAL.md` and `$cwd/LOCAL.md`
   contents.
2. On continue/recap keywords (respecting negation), append `RULES`.
3. On `PreCompact`, always append `RULES`.

### reclaude.py (PreCompact)

**Input:** JSON with `hook_event`.
**Output:** `{"ok": true, "systemMessage": "<RECLAUDE.md>"}` or silent.
Codex runs this through `codex_hook.py`; PreCompact context output is
suppressed there to avoid invalid Codex hook JSON.

**Flow:**
1. Reads `~/.claude/RECLAUDE.md`; silent exit if missing.
2. On `PreCompact`, injects the content with an appended preservation
   note so the wisdom survives compaction.

The script also has a continue/recap-keyword trigger path, but the
recommended wiring runs it on `PreCompact` only — the keyword path is
unwired.

### stop.py (Stop)

**Input:** JSON with `cwd`, `stop_hook_active`.
**Output:** `{"decision": "block", "reason": "..."}` on real Stop,
advisory `hookSpecificOutput.additionalContext` on PostToolUse, or silent.

**Flow:**
1. Bail early if `stop_hook_active` is set (prevents recursion).
2. Check `git status --porcelain -uno`; if dirty, append a commit nudge
   with `git diff --stat`.
3. If the repo has a `.diary/`, check for today's `YYYYMMDD.md` (UTC).
   Missing or >1h stale → append a diary nudge.
4. If recent `/fin` usage is detected, append an open-items reminder.
5. Real Stop blocks with the combined message. Periodic PostToolUse emits the
   same message as advisory context only.

Pure script, no LLM call. NEVER pushes. The hook may append a blank diary
header when the diary is missing or stale.

### memory_nudge.py (PreCompact + Stop)

**Input:** JSON with `cwd`, `session_id`, `stop_hook_active`, and hook event
identity (`hook_event`/`hook_event_name`/`hookEventName`).
**Output:** `PreCompact` → `{"ok": true, "systemMessage": "..."}` (local.py /
reclaude.py idiom). `Stop` → `hookSpecificOutput.additionalContext` (stop.py
PostToolUse idiom). Silent otherwise.

**Flow:**
1. Bail if `stop_hook_active` is set.
2. On `PreCompact`: always emit the memory-review nudge, then write a
   per-session `done` marker so the Stop fallback stays silent.
3. On `Stop`: silent if the `done` marker exists. Otherwise read the `start`
   file (`started_ts count`); the first Stop just records `now 1` and waits.
   Each later Stop bumps the count; once `now - started >= SESSION_THRESHOLD`
   (30 min) OR `count >= STOP_COUNT_THRESHOLD` (3), emit once and mark `done`.
   The count gate is what reaches *short* sessions that never compact and
   never approach 30 min.

State: `$cwd/.claude/tmp/memory-nudge-{start,done}-{session_id}`. Much lower
frequency than stop.py's recurring diary/commit nudges — at most once via
PreCompact plus at most once via the Stop fallback. Pure script, no LLM call.

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
{"ok": true, "systemMessage": "Invoke @improve."}
```

### Stop

```
stdin:
{
  "cwd": "/project"
  // "stop_hook_active": true — field absent when inactive; Claude Code only sends it when true
}

stdout (dirty tree + stale diary):
{
  "decision": "block",
  "reason": "Uncommitted changes detected.\n <diff stat>\nRun /commit.\nDiary not updated in over an hour. Run /diary."
}
```

Codex rewrites known Kronael refs in nudge output, e.g. `Run @commit` and
`Run @diary`.

## Error Handling

All Python hooks catch `json.JSONDecodeError`, `EOFError`, `ValueError`
and bail with exit 0 so a broken payload never blocks the session. File
I/O errors are swallowed for the same reason. `post_tool_nudge.sh`
always exits 0.

## Extension Points

**Add a new keyword route** — edit `AGENT_KEYWORDS` in `prompt_nudge.py`.

**Add a new stop nudge** — append to the `parts` list in `stop.py`. Keep
checks cheap (no network, no LLM) and guard with a path/directory probe
so the hook stays silent in projects that don't use the feature.

**Add a new injected file** — model it on `local.py` (first prompt +
`PreCompact`, negation-aware) or `reclaude.py` (`PreCompact` only).
