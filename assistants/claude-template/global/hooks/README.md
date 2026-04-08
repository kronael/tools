# Claude Code Hooks

Hooks that extend Claude Code with keyword routing, session rule injection,
and commit/diary nudges.

## Installation

Hooks are configured in `~/.claude/settings.json`. The hook scripts live in
`~/.claude/hooks/`.

## Features

### Keyword Routing (nudge.py)

Fires on `UserPromptSubmit`. Detects keywords in the prompt (with fuzzy
edit-distance matching) and emits a system message telling Claude to invoke
the matching command or agent.

| Keyword | Route |
|---------|-------|
| ship    | /ship |
| build   | /build |
| refine  | /refine |
| tweet   | /tweet |
| diary   | /diary |
| readme  | @readme |
| learn   | @learn |
| improve | @improve |
| visual  | @visual |
| distill | @distill |
| research | @research |

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

### Flow Reports (learn.py)

Fires on `PreCompact` and `SessionEnd`. Writes a markdown report to
`~/.claude/flow-reports/{timestamp}-{event}.md` with session metadata and
a pointer to `@learn` for pattern extraction.

### Commit + Diary Nudge (stop.py)

Fires on `Stop`. Blocks with a reason message if either:

- `git status --porcelain -uno` shows uncommitted changes → "consider /commit"
- `$cwd/.diary/` exists and today's `YYYYMMDD.md` is missing or >1h stale
  → "consider /diary"

Pure script, no LLM call. NEVER pushes. Commit and diary writes are
local-only and explicit.

## File Structure

```
~/.claude/hooks/
  nudge.py       # UserPromptSubmit: keyword → command/agent
  local.py       # UserPromptSubmit + PreCompact: LOCAL.md injection
  reclaude.py    # UserPromptSubmit + PreCompact: RECLAUDE.md injection
  learn.py       # PreCompact + SessionEnd: flow reports
  stop.py        # Stop: commit + diary nudge
  test_hooks.py  # Smoke tests
```

## Hook Configuration

In `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{"matcher": "", "hooks": [...]}],
    "Stop":             [{"matcher": "", "hooks": [...]}],
    "PreCompact":       [{"matcher": "", "hooks": [...]}],
    "SessionEnd":       [{"matcher": "", "hooks": [...]}]
  }
}
```

See ARCHITECTURE.md for per-hook data flow and TEST.md for the smoke tests.
