---
name: commit
description: Git commits. NOT for PR descriptions (use pr-draft).
when_to_use: "commit this, make a commit, committing changes"
user-invocable: true
---

# Commit

## When

- `/commit`: ALWAYS proceed
- Auto (hook): throttled ~once per 10 min — split accumulated work into coherent commits, don't dump it all in one.

## Splitting

One commit = one logical change. Group by WHY, not by directory:

- fix vs refa vs splx vs docs vs test → separate commits
- a fix + its test → one commit
- a doc/SCREENS/ARCHITECTURE update for a behavior change → same commit

## Format

Use `type(scope):` — scope is optional, omit only when the change is truly cross-cutting.

Format shapes:
- `fix(scope): Fix why it broke`
- `feat(scope): Add what`
- `refa(scope): Restructure what`
- `splx(scope): Simplify what`
- `chore: Maintain what`
- `docs(scope): Document what`
- `test(scope): Cover what`
- `perf(scope): Speed up what`
- `style: Format what`
- `build: Change what`
- `ci: Change what`
- `revert: <subject>`
- `release: vX.Y.Z`

Subject: ≤ 72 chars, imperative mood, capitalize first word after the colon. Test: "If applied, this commit will: _____"

Body (second `-m`): explain *why* — the diff shows what.
`git commit -m "subj" -m "why" -- files`

Breaking changes: `feat!:` / `fix!:` + footer `BREAKING CHANGE: what breaks and migration path`

Fixup: `fixup: <exact HEAD subject>` — correction to the immediately preceding commit.

## Workflow

1. `git status` + `git diff` + `git log --oneline -5`
2. Commit: `git commit -m "msg" -- file1 file2`
3. If pre-commit reformats, retry once
4. If index.lock: `rm -f .git/index.lock`, retry once

## Rules

- NEVER `git commit` without `-m "msg" -- file1 file2` (no staging, explicit files)
- NEVER `git commit --amend`
- NEVER Co-Authored-By
- NEVER skip pre-commit hooks
- NEVER commit if unrelated dirty files exist alongside the cohesive chunk
- Ignore other agents' uncommitted changes

## Orphaned worktrees

Only applies to Claude-managed worktrees under `.claude/worktrees/`. Never touch other worktrees.

1. `git worktree list` — note its base commit.
2. `git -C <wt> diff` — superseded by HEAD, or unique?
3. Superseded + lock pid dead → remove: `git worktree unlock <wt> && git worktree remove --force <wt> && git branch -D <branch>`
4. Holds unique work you did NOT create → surface to user, do NOT remove.
