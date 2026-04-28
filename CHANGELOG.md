# Changelog

## 2026-01-06

### Skills Migration

- Converted wisdom files to auto-activating skills
- Skills now in `global/skills/` with SKILL.md format
- Removed wisdom files from `local/` (kept only local.md template)
- Skills auto-activate based on semantic matching on descriptions

### New Agent: learn

- Added `/learn` command and learn agent
- Extracts patterns from conversation history (~/.claude/projects/)
- Creates/updates skills based on user corrections and patterns
- Three-phase workflow: identify → review with user → write

### Agent Updates

- Renamed refine → improve (DO-CRITICIZE-EVALUATE-IMPROVE loop)
- New refine orchestrates improve + readme
- Removed state-consistency-analyzer (merged into improve's code path tracing)

### Structure Changes

```
Before:
  local/*.md (13 wisdom files) → concatenated into project CLAUDE.md

After:
  global/skills/*/ (11 skills) → auto-activate by context
  local/local.md (1 template) → project-specific CLAUDE.md base
```

### Installation

- `make install` now copies skills to ~/.claude/skills/
- Skills auto-activate, no manual concatenation needed
- Run `/learn` to extract patterns from usage history
