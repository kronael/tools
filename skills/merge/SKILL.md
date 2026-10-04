---
name: merge
description: Resolve conflicts in a git merge, rebase, or cherry-pick and drive it to completion; merge origin — bring a detached line up to date with origin's default head (fetch, merge, resolve). NOT for ambiguous semantic conflicts (resolve manually), NOT for syncing ~/.claude with the bundle repo (use kronael/sync).
when_to_use: "git merge conflicts, resolve conflicts, fix merge conflicts, continue/finish the rebase, rebase conflict, cherry-pick conflict, continue cherry-pick, rebase onto squash-merged main, rebase --onto, diverged after squash merge, merge origin, update from origin, catch up with origin, merge origin/master into HEAD, pull origin, ahead and behind origin, bring the line up to date, update a pushed PR branch, merge the base forward into a pushed branch, PR diff ballooned after the base squash-merged"
user-invocable: true
---

# Merge

Resolve all merge conflicts in the working tree. Run directly in main context (no subagent).

## Merge origin — bring the detached line up to origin

This section is "merge origin", a git operation. "Sync" in this bundle means
only `kronael/sync`: files between `~/.claude/` and the bundle repo, no git
history. Vendoring skills into another project is `sync-tools-skills`.

1. `git fetch origin`, then size it against `origin/<default head>` (WISDOM
   § Git names the head):
   `git rev-list --left-right --count HEAD...origin/<default head>` and
   `git merge-base HEAD origin/<default head>`. ALWAYS fetch first — NEVER
   merge a stale tracking ref. Compare `git ls-remote --tags origin` with
   local tags: a tag name on a different commit than origin's is a
   collision — REPORT it, NEVER re-point it silently.
   Completion criterion: ahead/behind counts, the base, and any tag
   collisions are written down.
2. Preview without touching the tree:
   `git merge-tree --write-tree --name-only HEAD origin/<default head>`.
   Run § 0 on that list — a large or superseding merge gets a plan and a
   go-ahead first.
   Completion criterion: strategy chosen; every ambiguous path is named.
3. `git -c merge.conflictstyle=zdiff3 merge --no-commit --no-ff origin/<default head>`
   — zdiff3 shows the base inside every hunk. Resolve per §§ 2-6. Then trace
   deletions against BOTH parents
   (`git diff --name-status --diff-filter=DR <ours> HEAD` and the same for
   `origin/<default head>`) so an agreed deletion is not mistaken for lost
   work and a rename is not mistaken for a deletion.
   Completion criterion: `git diff --name-only --diff-filter=U` is empty and
   no tracked file matches `^<<<<<<<`.
4. Verify green (the repo's `make test` and lint), stage the resolved files
   by name, commit
   `merge: origin/<default head> <tag> into <what the local line is>` with a
   body naming each resolution decision.
   Completion criterion:
   `git rev-list --left-right --count HEAD...origin/<default head>` prints
   `N 0` — ahead only, 0 behind.

A merge origin ends at the local merge commit. What comes after (refine,
release, sync) is its own ask.

## 0. Safety gate — don't fuck it up

Before resolving ANYTHING, size the merge and decide whether to ask first.

- Count conflicted files and conflict markers; count commits each side has since
  the merge base (`git rev-list --count BASE..HEAD` vs `BASE..MERGE_HEAD`).
- If the merge is large or high-stakes (many files/markers, one side massively
  supersedes the other, or any semantic/API conflict): **write a one-paragraph
  resolution plan — strategy + rationale + anything genuinely ambiguous — and ASK
  for a go-ahead BEFORE touching files.** Cheap insurance; a bad merge silently
  drops work.
- Verify NOTHING is lost before proposing "take one side wholesale": confirm every
  conflicted path exists on the side you keep, and trace any file the other side
  added/deleted (`git cat-file -e BASE:f / OURS:f / THEIRS:f`) so an agreed
  deletion isn't mistaken for lost work.
- Only skip the ask for small, obviously-trivial merges (a handful of
  complementary/formatting conflicts). When in doubt, ask.

## 0b. Rebasing onto a squash-merged main

When your line was squash-merged to the default head and local has diverged,
`git rebase origin/<default head>` replays EVERY commit and conflicts on work
the head already holds.

- ALWAYS rebase only the post-merge commits: find the boundary (the local
  commit whose tree matches `origin/<default head>`), then
  `git rebase --onto origin/<default head> <boundary> HEAD`. Usually zero
  conflicts.
- Find the boundary by tree, not by eyeballing:
  `t=$(git rev-parse 'origin/<default head>^{tree}'); for c in $(git rev-list --first-parent
  HEAD); do [ "$(git rev-parse $c^{tree})" = "$t" ] && echo "$c" && break; done`
- ALWAYS prove nothing was lost: `git diff --quiet <old-tip> HEAD` (exit 0 =
  identical tree). The old tip stays in reflog — NEVER trust the replay blind.

## 0c. Updating a pushed branch — merge, never rebase

A line on the remote (an open PR, a layer of a stack) comes up to its base by
merging the base in: force-push is banned (WISDOM § Git), so a rebase of it
can never be pushed. § 0b is for a line that exists only locally.

1. `git ls-remote origin refs/heads/<b>` — the remote tip is the starting
   point, not the local one. Completion criterion: that SHA written down.
2. Detached at it, `git -c merge.conflictstyle=zdiff3 merge --no-ff <base>`;
   resolve per §§ 2-6 — the conflicts are the rebase's, with the same
   resolution. Completion criterion: no markers, gates green on HEAD.
3. ALWAYS prove the result is what was tested: `git diff <tested-commit>
   HEAD` empty — a green suite on a rebase or another resolution says nothing
   about this merge. Completion criterion: empty diff, or gates re-run on HEAD.
4. Push `git push origin <sha>:refs/heads/<b>`, a fast-forward, only when asked.

- A base squash-merged to trunk balloons the PR diff with conflicts though
  nothing new is in the branch. Merge trunk in; when the branch already
  carries every change the merge's tree equals the branch's (`git diff
  <branch> HEAD` empty) and the diff shrinks back — `-s ours` is honest only
  under that proof, NEVER on the assumption.
- ALWAYS budget a pass over every layer above a changed base: each merges it
  in, in order, and a test naming what a higher layer moves is re-aimed at
  the new structure there, NEVER weakened.

## 1. Orient — which operation is in flight

Detect the operation FIRST; it decides the finish command AND which side is "ours":

| `.git/` state | Operation | Finish command | `<<<<<<< HEAD` side is |
|---|---|---|---|
| `MERGE_HEAD` | merge | `git commit` | your current branch (ours) |
| `rebase-merge/` or `rebase-apply/` | rebase | `git rebase --continue` | rebased-ONTO base + already-replayed commits |
| `CHERRY_PICK_HEAD` | cherry-pick | `git cherry-pick --continue` | the branch you're picking ONTO |
| `REVERT_HEAD` | revert | `git revert --continue` | current branch |

`git status` also names it ("You are currently rebasing"). **In a rebase/cherry-pick the sides are REVERSED vs a merge**: `HEAD` is the target you're replaying onto, and the `>>>>>>>` label is the commit being applied — so "keep HEAD" means keep the base, NOT your feature work. Read the `>>>>>>>` commit subject to know what's being applied.

`git log --oneline -5`; note the merge base / rebased-onto commit. For a merge, identify HEAD (usually the feature branch) vs Incoming (often the default head's simplifications). If unclear, state what you see and ask which side takes priority.

## 2. Find all conflicts

```bash
grep -rln "<<<<<<< HEAD" <project_dirs>/
grep -n "<<<<<<\|=======\|>>>>>>>" <file>   # per-file
```

## 3. Classify each conflict

**TRIVIAL** (resolve immediately):
- One side adds, other removes → keep the addition
- Both sides add complementary things → keep both
- One side is a subset of the other → keep the superset
- Pure formatting / import ordering → take either, let fmt fix
- One side adds a parameter the function body already uses → keep it

**ASK** (present to user first):
- Semantic API changes (e.g. `bool` → `enum`, different type for same param)
- Deleted feature that may or may not be intentional
- Two incompatible implementations of the same logic
- Missing files (need to restore from git or confirm deletion)

## 4. Resolve trivials

For "keep both", order:
- Params: match function signature order (check body for usage order)
- Imports: alphabetical after `cargo fmt` / equivalent

After each file: `cargo check 2>&1 | grep "^error"` (or equivalent) to catch type mismatches early.

## 5. Present ambiguous conflicts

Per conflict, show:
- File + approximate line
- HEAD version
- Incoming version
- Why it's ambiguous (semantic change, API difference, etc.)
- Your best guess at the right resolution

Ask user to confirm or correct.

## 6. Fix compilation

After resolving all conflicts:
1. `cargo check` (or equivalent)
2. Fix type mismatches introduced by conflict resolution
3. Check for missing module declarations
4. Check for files deleted by one branch that the other needs

## 7. Finish — by operation type

Stage resolutions (`git add <resolved files>`), then finish per step 1's operation:

- **merge**: `git commit -m "merge: <summary>"` (the repo's `type(scope):` form; a merge has no scope).
- **rebase**: `GIT_EDITOR=true git rebase --continue` (GIT_EDITOR avoids the
  message editor; a `pick` reuses its original message). This is a **LOOP** — a
  rebase replays many commits, so the next may conflict immediately: re-run
  steps 2-6 and `--continue` again until `git status` shows no rebase in flight.
- **cherry-pick**: `git add`, then `GIT_EDITOR=true git cherry-pick --continue`;
  loops the same way for a multi-commit pick.

Escape hatches (per replayed patch):
- `git rebase --skip` (or `cherry-pick --skip`) when a replayed commit is
  **obsolete** — its change is already on the base, or its target no longer
  exists (an old refactor rebased onto a newer base). Confirm it adds nothing
  novel FIRST; skipping drops that commit.
- `git rebase --abort` / `cherry-pick --abort` / `git merge --abort` to bail
  entirely to the pre-op state. NEVER leave a half-finished rebase.

If pre-commit reformats (merge only), retry once. NEVER `--amend` / `--no-verify`.

## Priority rule (when user says "prioritize HEAD / feature branch")

In a **rebase/cherry-pick** your feature work is the `>>>>>>>` (replayed) side,
NOT HEAD — so "keep my work" means keep the incoming side, the reverse of a
merge. Map "feature branch" to the side that actually carries the user's commits.

- ALWAYS keep HEAD's features and additions
- ONLY take incoming changes that are pure simplifications:
  - Removing dead code
  - Simplifying logic without changing behavior
  - Bug fixes that don't conflict with HEAD features
- ALWAYS keep HEAD when in doubt about an incoming change
