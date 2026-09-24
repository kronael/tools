---
name: squash
description: Reorganize the UNPUSHED commits on a detached tip into a clean, logical, PR-review-friendly history. NOT for resolving conflicts (use merge), a single commit (use commit), or rewriting anything already pushed to origin.
when_to_use: "squash commits, clean up commit history, tidy the stack before a PR, reorganize commits, group related commits into one, collapse churn, drop an add-then-revert pair, combine incremental dependency bumps, rebase -i alternative, prepare branch for review, non-interactive rebase, rewrite local history"
user-invocable: true
---

# Squash

The SANCTIONED exception to WISDOM's "NEVER squash commits" — like `/refine` and
`/ship` committing by design. It applies ONLY to a **local, UNPUSHED** tip being
prepared for PR review, on explicit user invocation. Nothing already on `origin/*`
is ever rewritten. Method is a NON-INTERACTIVE rewrite via `reset --soft` — simpler
and safer than `git rebase -i` (which needs a scripted `GIT_SEQUENCE_EDITOR`, per-commit
message editors, and mid-rebase conflict handling): one reset, then re-commit in groups.

Goal: a reviewer-friendly stack — related changes grouped one-commit-each, churn
gone, each commit conventional-committed. NOT fewer commits for their own sake.

## 1. Bind the range — unpushed only

```bash
BASE=$(git merge-base origin/main HEAD)   # fork point from published main
OLD=$(git rev-parse HEAD)                 # old tip — the recovery anchor, record FIRST
```

- `BASE` is the floor: ONLY commits in `BASE..HEAD` may be rewritten. NEVER touch
  anything at or below `BASE` — it is published. Confirm with `git log --oneline "$BASE"..HEAD`.
- If the branch tracks a different upstream, use `git merge-base @{upstream} HEAD`.
- If `BASE..HEAD` is empty, or every commit is already on `origin/*`, STOP — nothing to squash.
- Print `OLD` to the user so the pre-squash state is recoverable by SHA (also in `git reflog`).

## 2. Plan the mapping

Read `git log --stat "$BASE"..HEAD` and the diffs. Group into logical commits:

- One coherent change per commit; group related edits (a fix + files it spans).
- **Cancel churn**: an add-then-revert pair over the range nets to nothing — drop both.
- **Collapse bumps**: incremental bumps of the SAME dependency become one commit at the final version.
- Put a test WITH the change it covers, not in a separate commit.
- Give each new commit a conventional-commit message (`type(scope): subject`, imperative — see the `commit` skill).

## 3. Approval gate — show, then confirm

History rewrite is destructive. BEFORE running any reset, print the proposed mapping
and WAIT for an explicit go-ahead:

```
OLD tip: <OLD>   BASE: <BASE>
old: abc111 wip parser      ┐
old: abc222 fix parser typo ┼→ new: fix(parser): Handle empty input
old: abc333 test parser     ┘
old: def444 bump serde 1.1  ┐
old: def555 bump serde 1.2  ┼→ new: chore(deps): Bump serde to 1.3
old: def666 bump serde 1.3  ┘
old: aaa777 add debug print ┐
old: aaa888 remove it       ┴→ (dropped — churn cancels)
```

ALWAYS get the go-ahead here. NEVER reset before the user approves the mapping.

## 4. Rebuild — non-interactive `reset --soft` (primary)

```bash
git reset --soft "$BASE"    # HEAD → BASE; whole old stack now staged, tree untouched
git restore --staged .      # unstage all; every change sits in the working tree
```

Then re-commit group by group, in a sensible order (foundational change first):

- **By path**: `git add <paths of the group>` then commit the staged index.
- **By hunk** (when one file spans two logical groups): `git add -p` to stage only that group's hunks.
- Commit the STAGED INDEX: `git commit -m "type(scope): subject" -m "why"`. Do NOT append `-- <files>`
  here — with hunk-level staging that would commit the whole file and defeat the split. (This is the
  one deliberate deviation from the `commit` skill's explicit-path rule, forced by hunk splitting.)
- Repeat until `git status` is clean (working tree empty) — every change must land in exactly one commit.

## 5. Alternative — cherry-pick onto a fresh worktree

When the working-tree collapse is awkward (e.g. reordering across many files), rebuild by replay:

```bash
git worktree add --detach "$(git rev-parse --show-toplevel)/.squash" origin/main
```

Cherry-pick only the keep-commits (`git cherry-pick <sha>…`), dropping churn commits, squashing a
run with `git cherry-pick -n <sha> <sha> && git commit`. Detached, inside the repo as a hidden dir.
The step-6 gate applies identically; remove the worktree after: `git worktree remove --force .squash`.

## 6. Verify — the byte-identical gate (NON-NEGOTIABLE)

Reorganizing commits must NEVER change the resulting code. The new tree must equal the old tree:

```bash
git diff "$OLD" HEAD    # MUST print nothing
```

- Empty → the rewrite is content-preserving. Proceed.
- NON-EMPTY → the squash is WRONG. Recover and retry: `git reset --hard "$OLD"`, then redo from step 4.
- Recovery any time: `git reset --hard "$OLD"` (or `git reset --hard <SHA from git reflog>`).

Then the build/test gate — run this repo's `cargo build` + `cargo test` (or project equivalent) on the
new tip; it must still pass. Ideally each new commit builds: spot-check with
`git stash` off / `git checkout <new-sha> -- .` on a scratch worktree, or at minimum verify the tip.

## Rules

- ALWAYS record `OLD` and print the mapping for approval BEFORE the first reset. NEVER reset unasked.
- ALWAYS treat `git diff "$OLD" HEAD` being empty as the correctness gate; on any diff, `reset --hard "$OLD"` and retry.
- NEVER rewrite a commit that exists on `origin/*` — the `BASE = merge-base origin/main HEAD` floor enforces this.
- NEVER `git push`, NEVER `git commit --amend`, NEVER `git add -A`, NEVER add `Co-Authored-By`.
- ALWAYS stay in detached HEAD; NEVER create or attach a branch (the cherry-pick worktree uses `--detach`).
- NEVER skip pre-commit hooks. Hooks do NOT fire in a worktree — run fmt/clippy/lint by hand there before committing.
- NEVER squash to hit a commit count; group by WHY. A three-commit stack that is already logical is left alone.
