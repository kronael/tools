---
name: commit
description: Git commits. NOT for PR descriptions (use pr-draft).
when_to_use: "commit this", "make a commit", committing changes
user-invocable: true
---

# Commit

## When

- `/commit`: ALWAYS proceed
- Auto (hook): the nudge is throttled to ~once per 10 min, so dirty work
  accumulates between nudges. When it fires, do the work of splitting — don't
  dump the whole tree into one commit (see Splitting).
- Not cohesive: name the logical groups and commit each separately — never a
  combined commit.

## Splitting into coherent chunks

One commit = one logical change. Read the diff and group by WHY, not by
directory, then commit each group with its own `[section]` message:

- fix vs refactor vs docs vs test → separate commits, even when touched together
- unrelated features → separate commits
- a fix + its test → one commit (single change)
- a doc/SCREENS/ARCHITECTURE update for a behavior change → same commit as the change
- if you can't state one reason for a group, it's two commits

Prefer 3 precise commits over 1 vague one. The throttle buys you time to
split correctly — use it. `git add -A` + one message defeats the split.

## Format

`[section] Message` — why not what, 1-2 sentences.
Sections: fix, feat, refactor, docs, test, chore, perf, style, release

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

## Orphaned worktrees

A worktree under `.claude/worktrees/` from a prior session may linger — locked
by a dead pid, stranded on a stale base. Before touching it:

1. `git worktree list` — note its base commit (often far behind HEAD).
2. `git -C <wt> diff` — is the work superseded by current HEAD, or unique?
3. Superseded / trivial / stale-base AND lock pid dead → safe to remove:
   `git worktree unlock <wt> && git worktree remove --force <wt> && git branch -D <branch>`
4. Holds unique, non-superseded work you did NOT create → surface to the user;
   do NOT force-remove (you'd destroy unsaved work).
