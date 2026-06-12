# Hooks Architecture

## Overview

```
User Prompt ──> UserPromptSubmit ──> prompt_nudge.py (keyword → command/agent)
                                 ──> local.py        (LOCAL.md on first prompt)

Tool call ──> PreToolUse  ──> pretool_nudge.py   (file → language-skill nudge)
          ──> PostToolUse ──> post_tool_nudge.sh (periodic commit/diary nudge)

Claude stops ──> Stop ──> stop.py (commit + diary nudge)

Compaction ──> PreCompact ──> local.py    (LOCAL.md + RULES)
                          ──> reclaude.py (RECLAUDE.md + preservation note)
```

Event/matcher wiring is owned by `../settings-recommended.json`.

## Components

### prompt_nudge.py (UserPromptSubmit)

**Input:** JSON with `prompt` field.
**Output:** `{"ok": true, "systemMessage": "..."}` or silent exit.

**Flow:**
1. Skip meta prompts (hook/agent debugging) to avoid self-interference.
2. If prompt mentions `todo|readme|changelog|spec|architecture|*.md`,
   append `DOCS_RULES`.
3. Tokenise prompt, fuzzy-match each word against `AGENT_KEYWORDS` by
   edit distance (allowance scales with keyword length).
4. If prompt contains `commit`, append `COMMIT_RULES` and short-circuit;
   otherwise emit the first fuzzy-matched agent route.

**Routes:** `AGENT_KEYWORDS` dict in the source.

### pretool_nudge.py (PreToolUse)

**Input:** JSON with `tool_name`, `tool_input` (`file_path` /
`notebook_path`), `session_id`.
**Output:** `hookSpecificOutput.additionalContext` nudge, or silent.

**Flow:**
1. Ignore tools outside Read/Edit/Write/MultiEdit/NotebookEdit.
2. Map path to a skill: special filenames first (`Makefile` → `/mk`,
   `Dockerfile`/compose/workflows → `/ops`), then extension via
   `EXT_SKILLS` (`.rs` → `/rs`, `.html` → `/htmx`, ...).
3. Dedupe per session+file via `$TMPDIR/claude-extnudge/{sid}.txt` so
   each nudge fires once.
4. Emit "Editing/reading <file> — follow <skill> conventions."

### post_tool_nudge.sh (PostToolUse)

**Input:** stdin unused; state in `/tmp/claude-commit-nudge` (ts + count).
**Output:** `stop.py`'s output every 100 tool calls or 10 minutes,
otherwise silent. Always exits 0 — never blocks a tool call.

**Flow:**
1. Increment the call counter.
2. At 100 calls or 600 s, reset state and run `stop.py` so the
   commit/diary nudge also fires mid-session, not only on Stop.

### local.py (UserPromptSubmit + PreCompact)

**Input:** JSON with `prompt`, `hook_event`, `session_id`, `cwd`.
**Output:** `{"ok": true, "systemMessage": "<content>"}` or silent.

**Flow:**
1. First prompt per session (tracked via `$cwd/.claude/tmp/local-{sid}`)
   or `PreCompact` event → inject `~/.claude/LOCAL.md` and `$cwd/LOCAL.md`
   contents.
2. On continue/recap keywords (respecting negation), append `RULES`.
3. On `PreCompact`, always append `RULES`.

### reclaude.py (PreCompact)

**Input:** JSON with `hook_event`.
**Output:** `{"ok": true, "systemMessage": "<RECLAUDE.md>"}` or silent.

**Flow:**
1. Reads `~/.claude/RECLAUDE.md`; silent exit if missing.
2. On `PreCompact`, injects the content with an appended preservation
   note so the wisdom survives compaction.

The script also has a continue/recap-keyword trigger path, but the
recommended wiring runs it on `PreCompact` only — the keyword path is
unwired.

### stop.py (Stop)

**Input:** JSON with `cwd`, `stop_hook_active`.
**Output:** `{"decision": "block", "reason": "..."}` or silent.

**Flow:**
1. Bail early if `stop_hook_active` is set (prevents recursion).
2. Check `git status --porcelain -uno`; if dirty, append a commit nudge
   with `git diff --stat`.
3. If `$cwd/.diary/` exists, check for today's `YYYYMMDD.md` (local time).
   Missing or >1h stale → append a diary nudge.
4. Block with the combined message if any nudges accumulated.

Pure script, no LLM call. NEVER pushes.

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
  "cwd": "/project",
  "stop_hook_active": false
}

stdout (dirty tree + stale diary):
{
  "decision": "block",
  "reason": "Uncommitted changes detected.\n <diff stat>\nConsider running /commit.\nDiary not updated in over an hour. Consider running /diary."
}
```

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
