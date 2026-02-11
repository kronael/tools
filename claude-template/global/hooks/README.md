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

Re-injects key CLAUDE.md rules on compaction triggers.

**Triggers:** "continue", "where were we", "what's next", "recap"

**Injected rules:**
- Use make for build/lint/test
- Build/test every ~50 lines
- Never improve beyond what's asked
- Never use `git add -A`
- Never use `git commit --amend`
- Never add Co-Authored-By

### Flow Reports (learn.py)

Generates session reports on PreCompact and SessionEnd events.

Reports saved to `~/.claude/flow-reports/` with timestamp and event type.
Run @learn to analyze and extract patterns into skills.

### Commit Nudge (Stop hook)

Haiku prompt at natural breakpoints suggests committing if changes are cohesive.

## File Structure

```
~/.claude/hooks/
  lib/
    toolchain.py    # Toolchain detection
  redirect.py       # PreToolUse: command redirect
  nudge.py          # UserPromptSubmit: keyword expansion
  local.py          # UserPromptSubmit: LOCAL.md injection
  learn.py          # PreCompact/SessionEnd: flow reports
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
