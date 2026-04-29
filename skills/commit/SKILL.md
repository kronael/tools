---
name: commit
description: Git commits. USE to draft commit messages and stage/commit changes ([section] format). NOT for PR descriptions (use pr-draft).
user-invocable: true
---

# Commit

## When

- `/commit`: ALWAYS proceed
- Auto (hook): only if all dirty files form a single cohesive chunk AND no unrelated dirty files exist
- Not cohesive: name the logical groups, stop — do not suggest a combined commit

## Format

`[section] Message` — why not what.
Sections: fix, feat, refactor, docs, test, chore, perf, style

Subject ≤ 72 chars (includes `[section]`). Overflow goes in body via a
second `-m`: `git commit -m "subj" -m "body" -- files`.

Fixup: `fixup: <exact HEAD subject>` — use when the change is a correction to the immediately preceding commit.

Markers: `[checkpoint]` → `[checkpoint] Message`, `[refined]` → `[section] Message [refined]`

## Workflow

1. `git status` + `git diff` + `git log --oneline -5`
2. Decide commit or not; if correction to HEAD use `fixup:` format
3. Draft message
4. Commit directly: `git commit -m "msg" -- file1 file2`
5. If pre-commit reformats, retry once
6. If index.lock: `rm -f .git/index.lock`, retry once

## Rules

- ALWAYS `git commit -m "msg" -- file1 file2` (direct, no staging)
- ALWAYS commit whole files, list each explicitly
- NEVER `git add` (commit directly with -- pathspec)
- NEVER `git commit` without `-- file1 file2`
- NEVER `git commit --amend`
- NEVER `git commit -a`
- NEVER `git stash`
- NEVER Co-Authored-By
- NEVER skip pre-commit hooks
- NEVER suggest committing if unrelated dirty files exist alongside the cohesive chunk
- Ignore other agents' uncommitted changes
