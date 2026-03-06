---
name: commit
description: Git commits. git status, git diff, git add, staging files, commit messages, [section] format.
user-invocable: true
---

# Commit

## When to Commit

- User explicitly says /commit: ALWAYS proceed
- Auto-suggested (from hook): only if changes form a cohesive chunk
  - Single feature, fix, or refactor (not multiple unrelated changes)
  - Related files (not scattered across unrelated modules)
  - Complete work (not half-implemented or broken state)
- If NOT cohesive: report what you see and stop

## Format

`[section] Message` — focus on "why" not "what", 1-2 sentences.

Sections: fix, feat, refactor, docs, test, chore, perf, style

Markers (when passed as args):
- `[checkpoint]` → `[checkpoint] Message`
- `[refined]` → `[section] Message [refined]`

## Rules

- NEVER use git add -A (stage specific files)
- NEVER use git commit --amend
- NEVER add Co-Authored-By lines
- NEVER skip pre-commit hooks
- If pre-commit fails and reformats, retry once
