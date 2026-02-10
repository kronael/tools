# Hooks Architecture

## Overview

```
User Prompt ──> UserPromptSubmit hooks ──> Claude
                    │
                    ├── nudge.py (keyword → agent)
                    └── context.py (rule injection)

Claude ──> PreToolUse[Bash] ──> redirect.py ──> Execute
                                    │
                                    └── toolchain.py (detection)

Claude stops ──> Stop hook ──> Haiku prompt (commit nudge)

Session end ──> PreCompact/SessionEnd ──> learn.py ──> Flow report
```

## Components

### toolchain.py

Detects project toolchain and returns appropriate commands.

**Detection order (priority):**
1. Makefile - checks target exists in file
2. Cargo.toml - Rust project
3. go.mod - Go project
4. Lockfile - pnpm-lock.yaml, yarn.lock, package-lock.json
5. pyproject.toml - Python project (uv.lock for uv runner)

**Command mappings:**

| Action | Makefile | Cargo | Go | npm/yarn/pnpm | Python |
|--------|----------|-------|----|--------------:|--------|
| test | make test | cargo test | go test ./... | {pm} test | pytest |
| build | make build | cargo build | go build ./... | {pm} run build | - |
| lint | make lint | cargo clippy | go vet ./... | {pm} run lint | ruff check |
| e2e | make e2e | cargo test --test '*' | go test -tags=e2e | {pm} run e2e | pytest tests/ |
| smoke | make smoke | - | - | {pm} run smoke | pytest --smoke |

### redirect.py (PreToolUse)

**Input:** Bash tool_input from Claude
**Output:** Modified command or pass-through

**Flow:**
1. Check escape hatch (`!` prefix) - exit if present
2. Match command against DETECTORS regex list
3. If match, get redirect from toolchain.py
4. If redirect differs from original, return updated input
5. Otherwise pass-through

**Detectors:**
```python
DETECTORS = [
    (r"^pytest\b", "test"),
    (r"^cargo\s+test\b", "test"),
    (r"^npm\s+test\b", "test"),
    # ... more patterns
]
```

### nudge.py (UserPromptSubmit)

**Input:** User prompt
**Output:** System message with agent invocation

**Flow:**
1. Match prompt against AGENTS patterns
2. First match wins - emit system message
3. No match - pass-through

**Agent patterns:**
```python
AGENTS = [
    (r"\b(improve|enhance|fix|...)\b", "/improve"),
    (r"\b(refine|finalize|...)\b", "/refine"),
    # ... more patterns
]
```

### context.py (UserPromptSubmit)

**Input:** User prompt
**Output:** System message with rules (on trigger)

**Triggers:** continue, where were we, what's next, recap

Injects subset of CLAUDE.md rules to counteract context loss from compaction.

### learn.py (PreCompact/SessionEnd)

**Input:** Hook event data
**Output:** Markdown report file

**Report location:** `~/.claude/flow-reports/{timestamp}-{event}.md`

Contains:
- Event type and timestamp
- Session ID and working directory
- Prompts for pattern extraction
- Pointer to /learn agent

## Data Flow

### PreToolUse Hook

```
stdin (JSON):
{
  "tool_name": "Bash",
  "tool_input": {"command": "pytest"},
  "cwd": "/project"
}

stdout (JSON) - redirect:
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Redirected: test",
    "updatedInput": {"command": "make test"}
  }
}

stdout - pass-through:
(exit 0 with no output)
```

### UserPromptSubmit Hook

```
stdin (JSON):
{
  "prompt": "improve the error handling"
}

stdout (JSON):
{
  "systemMessage": "Invoke /improve agent."
}
```

### Stop Hook (Prompt Type)

```json
{
  "type": "prompt",
  "prompt": "Claude finished. Check git diff --stat. Is this a good commit point?"
}
```

Haiku model returns `{"nudge": "..."}` or `{"pass": true}`.

## Configuration

### Hook Types

1. **command** - Runs external script, reads stdout JSON
2. **prompt** - Sends prompt to Haiku, uses response

### Matchers

- Empty string `""` - matches all
- Tool name `"Bash"` - matches specific tool

### Timeouts

- redirect.py: 5000ms
- nudge.py: 3000ms
- context.py: 3000ms
- learn.py: 10000ms

## Error Handling

All hooks fail silently (exit 0) on errors to avoid breaking the session.
Exceptions are caught and ignored in learn.py file writing.

## Extension Points

Add new toolchains in `toolchain.py`:
1. Add detection function (e.g., `has_cmake`)
2. Add command mapping dict
3. Add priority check in `get_redirect_command`

Add new agents in `nudge.py`:
1. Add pattern and agent path to AGENTS list

Add new triggers in `context.py`:
1. Add keyword to triggers list
2. Optionally modify RULES content
