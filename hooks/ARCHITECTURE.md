# Hooks Architecture

## Overview

```
User Prompt ──> UserPromptSubmit ──> nudge.py    (keyword → command/agent)
                                 ──> local.py    (LOCAL.md on first prompt)
                                 ──> reclaude.py (RECLAUDE.md on first prompt)

Claude stops ──> Stop ──> stop.py (commit + diary nudge)

Compaction ──> PreCompact ──> local.py    (LOCAL.md + RULES)
                          ──> reclaude.py (RECLAUDE.md + preservation note)
                          ──> learn.py    (flow report)

Session end ──> SessionEnd ──> learn.py (flow report)
```

## Components

### nudge.py (UserPromptSubmit)

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

### learn.py (PreCompact + SessionEnd)

**Input:** JSON with `hook_event`, `session_id`, `cwd`.
**Output:** Markdown file at `~/.claude/flow-reports/{ts}-{event}.md`
plus a `systemMessage` confirming the write.

The report is a template with session metadata and a prompt for the
`@learn` agent to extract patterns into skills.

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

stdout (nudge.py match):
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

All hooks catch `json.JSONDecodeError`, `EOFError`, `ValueError` and bail
with `sys.exit(0)` so a broken payload never blocks the session. File I/O
errors in `learn.py` and `local.py` are swallowed for the same reason.

## Extension Points

**Add a new keyword route** — edit `AGENT_KEYWORDS` in `nudge.py` and the
table in `README.md`.

**Add a new stop nudge** — append to the `parts` list in `stop.py`. Keep
checks cheap (no network, no LLM) and guard with a path/directory probe
so the hook stays silent in projects that don't use the feature.

**Add a new injected file** — model it on `local.py`/`reclaude.py`: read
on first prompt + `PreCompact`, respect negation, append rules on
compaction.
