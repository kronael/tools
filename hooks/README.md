# Claude Code Hooks

Hooks that extend Claude Code and Codex with prompt routing, session rule
injection, and commit/diary nudges.

## Installation

Hooks are configured in `~/.claude/settings.json`. The hook scripts live in
`~/.claude/hooks/`.

## Features

### Nudge Taxonomy

- `info`: prompt/file-skill suggestions. Never blocks.
- `warn`: stop/post-tool hygiene reminders for commit and diary. Forces one
  more turn (`decision: block` on `Stop`) so Claude sees the reminder and
  can act on it — never prevents an action, unlike the `block` category.
- `block`: true unsafe actions only: push, amend, hard reset, broad
  `git add -A`/`--all`, `--no-verify`, `rm -rf`, and recursive Codex execution.

### Prompt Routing (prompt_nudge.py)

Fires on `UserPromptSubmit`. Detects exact phrases and explicit aliases in the
prompt and emits an informational system message telling Claude to invoke the
matching command or agent. There is no edit-distance matching.

On the first non-empty prompt of a session it also prepends a `/resolve` nudge
(triage + diary/memory load before acting), tracked via
`$cwd/.claude/tmp/resolve-nudge-{session_id}` so continuations stay silent. A
prompt that already invokes `/resolve` suppresses it.

| Keyword | Route |
|---------|-------|
| ship    | /ship |
| refine  | /refine |
| tweet   | /tweet |
| diary   | /diary |
| readme  | @readme |
| improve | @improve |
| visual  | @visual |
| distill | @distill |

`learn` is deliberately absent from this table — `/learn` is invoked only
explicitly (slash command) or by `memory_nudge.py`'s low-frequency nudge, never
because the word "learn" appeared in a prompt.

Codex second-opinion routing is Claude-only: `ask codex`, `oracle`, or
`second opinion` route to `/codex` in Claude, and are suppressed inside Codex
so Codex is never nudged to invoke itself. Model escalation routes such as
`/fable` and `/opus` require explicit phrasing (`/fable`, `use fable`,
`spawn fable`); incidental mentions do not route.

Also injects `COMMIT_RULES` on "commit" and `DOCS_RULES` on
`todo|readme|changelog|spec|architecture|*.md` mentions.

Meta prompts (hook/agent debugging) are detected and skipped so the hook
does not interfere with hook maintenance itself.

### LOCAL.md Injection (local.py)

Fires on `UserPromptSubmit` and `PreCompact`. Injects `~/.claude/LOCAL.md`
(and `$cwd/LOCAL.md` if present) on the first prompt of a session and on
pre-compaction. Also re-injects a short `RULES` block on continue/recap
keywords, respecting negation ("don't continue").

**State:** `$cwd/.claude/tmp/local-{session_id}` tracks the first prompt.

### RECLAUDE.md Injection (reclaude.py)

Fires on `UserPromptSubmit` and `PreCompact`. Mirrors `local.py` but sources
`~/.claude/RECLAUDE.md`. On `PreCompact`, appends a note instructing the
model to preserve the wisdom across compaction.

### Commit + Diary Nudge (stop.py)

Fires on `Stop`. Emits a `warn`-category nudge (never an unsafe-action
`block`) if either:

- `git status --porcelain -uno` shows uncommitted changes → "consider /commit"
- `$cwd/.diary/` exists and today's `YYYYMMDD.md` is missing or >1h stale
  → "consider /diary"

The stop hook does not write diary headers. Run `/diary` deliberately when a
session should be recorded. True unsafe actions are handled by explicit deny
rules in the settings and PreToolUse command blockers, not by hygiene nudges.

### Memory Nudge (memory_nudge.py)

Fires on `PreCompact` (unconditionally) and `Stop` (throttled, see below).
Reminds the assistant to evaluate the session for memory-worthy content
(corrections, confirmed decisions, project facts, reference pointers) and
save it via the auto-memory mechanism or `/learn` — much less often than the
diary nudge, and tied to the moment context would otherwise be lost:

- **PreCompact**: always nudges (manual or auto trigger). Rare per session —
  the natural point to capture what's about to be summarized away.
- **Stop**: fires **at most once per session**, and only after the session
  has run at least `SESSION_THRESHOLD` (30 min) — not on every turn like
  `stop.py`. This is the fallback for sessions that never compact. A
  `PreCompact` firing suppresses the later `Stop` fallback for that session.

**State:** `$cwd/.claude/tmp/memory-nudge-{start,done}-{session_id}`.

### File and Command Preflight (pretool_nudge.py)

Fires on file tools and shell command tools. File tools emit informational
language-skill context based on the file extension or basename (`Makefile`,
`Dockerfile`, `SKILL.md`/`CLAUDE.md`/`AGENTS.md` → `/wisdom`, etc.), including
Codex `apply_patch` patches with explicit file headers. Shell command tools
block only the unsafe command forms listed in the taxonomy above.

## File Structure

```
~/.claude/hooks/
  prompt_nudge.py    # UserPromptSubmit: exact phrase → command/agent
  local.py           # UserPromptSubmit + PreCompact: LOCAL.md injection
  reclaude.py        # UserPromptSubmit + PreCompact: RECLAUDE.md injection
  pretool_nudge.py   # PreToolUse: file-skill info + unsafe command block
  post_tool_nudge.sh # PostToolUse: throttled re-invoke of stop.py
  stop.py            # Stop (+ PostToolUse via post_tool_nudge.sh): commit + diary warnings
  memory_nudge.py    # PreCompact + Stop (throttled): session memory nudge
```

## Hook Configuration

In `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{"matcher": "", "hooks": [...]}],
    "Stop":             [{"matcher": "", "hooks": [...]}],
    "PreCompact":       [{"matcher": "", "hooks": [...]}]
  }
}
```

See ARCHITECTURE.md for per-hook data flow.
