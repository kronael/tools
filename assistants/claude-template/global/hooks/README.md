# Claude Code Hooks

Hooks that extend Claude Code with smart command execution, keyword expansion,
and session management.

## Installation

Hooks are configured in `~/.claude/settings.json`. The hook scripts live in
`~/.claude/hooks/`.

## Features

### Smart Command Redirect (redirect.py)

Detects test/build/lint commands and redirects to project's toolchain.

**Detection priority:**
1. Makefile (if target exists)
2. Cargo (Rust)
3. Go
4. npm/yarn/pnpm (by lockfile)
5. Python (uv or pytest)

**Detected operations:**
- `test` - test suite commands (pytest, cargo test, npm test, etc.)
- `build` - build commands (cargo build, go build, npm run build, tsc)
- `lint` - linter commands (clippy, go vet, ruff, npm run lint)
- `e2e` - e2e/integration tests
- `smoke` - extended test suites

**Escape hatch:** Prefix command with `!` to bypass redirect.
```bash
# Redirected to make test (if Makefile exists)
pytest

# Runs pytest directly
!pytest
```

### Keyword Expansion (nudge.py)

Expands keywords in prompts to agent invocations.

| Keyword | Route |
|---------|-------|
| ship | /ship |
| build | /build |
| refine | /refine |
| tweet | /tweet |
| readme | @readme |
| learn | @learn |
| improve | @improve |
| visual | @visual |
| distill | @distill |
| research | @research |

Uses fuzzy matching (edit distance) for typo tolerance.

**Example:** "improve the error handling" triggers `@improve` agent.

### LOCAL.md Injection (local.py)

Injects LOCAL.md at session start (first prompt) and before compaction.
Re-injects key rules on continue/recap keywords.

**Fires on:** first prompt per session, PreCompact, continue/recap keywords

**State:** `.claude/tmp/local-{session_id}` tracks first prompt

### Flow Reports (learn.py)

Generates session reports on PreCompact and SessionEnd events.

Reports saved to `~/.claude/flow-reports/` with timestamp and event type.
Run @learn to analyze and extract patterns into skills.

### Commit Nudge (stop.py)

Runs on Stop event. Checks `git status --porcelain` — if uncommitted
changes exist, blocks with "consider /commit". No LLM call, pure script.

**Flow:** stop.py blocks → user/LLM sees nudge → /commit skill validates
→ only commits if changes form cohesive chunk (single feature/fix,
related files, complete work). See commit skill for validation rules.

NEVER pushes. Commit is local-only.

## File Structure

```
~/.claude/hooks/
  lib/
    toolchain.py    # Toolchain detection
  redirect.py       # PreToolUse: command redirect
  nudge.py          # UserPromptSubmit: keyword expansion
  local.py          # UserPromptSubmit: LOCAL.md injection
  learn.py          # PreCompact/SessionEnd: flow reports
  stop.py           # Stop: commit nudge if uncommitted changes
```

## Hook Configuration

In `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "Bash", "hooks": [...]}],
    "UserPromptSubmit": [{"matcher": "", "hooks": [...]}],
    "Stop": [{"matcher": "", "hooks": [...]}],
    "PreCompact": [{"matcher": "", "hooks": [...]}],
    "SessionEnd": [{"matcher": "", "hooks": [...]}]
  }
}
```

See ARCHITECTURE.md for technical details.
