# AGENTS.md

Codex/non-Claude agent bridge for this repository.

## Startup

ALWAYS read before making changes:

1. Root `CLAUDE.md`
2. Nearest nested `CLAUDE.md` for the area being changed
3. If in `assistants/`: also `assistants/CLAUDE.md` and
   `assistants/claude-template/global/CLAUDE.md`

NEVER ignore a `CLAUDE.md` because it says "Claude". These are
project conventions, not product-specific behavior. Adopt the intent;
surface gaps when a feature cannot be executed as-is.

## Install

- Claude Code: open `assistants/claude-template/`, say "install"
- Codex: read and apply the `CLAUDE.md` hierarchy, keep this file current

## Conventions

- Boring linear code over clever code
- Files under 200 lines
- ALWAYS/NEVER statements in assistant guidance
- No secrets, no local paths, no org-specific references
- NEVER duplicate — point to authoritative `CLAUDE.md` files
