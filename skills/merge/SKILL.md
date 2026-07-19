---
name: merge
description: Resolve conflicts in a git merge, rebase, or cherry-pick and drive it to completion. NOT for ambiguous semantic conflicts (resolve manually).
when_to_use: "git merge conflicts, resolve conflicts, fix merge conflicts, continue/finish the rebase, rebase conflict, cherry-pick conflict, continue cherry-pick"
user-invocable: true
---

# Merge

Resolve all merge conflicts in the working tree. Run directly in main context (no subagent).

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

## 1. Orient — which operation is in flight

Detect the operation FIRST; it decides the finish command AND which side is "ours":

| `.git/` state | Operation | Finish command | `<<<<<<< HEAD` side is |
|---|---|---|---|
| `MERGE_HEAD` | merge | `git commit` | your current branch (ours) |
| `rebase-merge/` or `rebase-apply/` | rebase | `git rebase --continue` | rebased-ONTO base + already-replayed commits |
| `CHERRY_PICK_HEAD` | cherry-pick | `git cherry-pick --continue` | the branch you're picking ONTO |
| `REVERT_HEAD` | revert | `git revert --continue` | current branch |

`git status` also names it ("You are currently rebasing"). **In a rebase/cherry-pick the sides are REVERSED vs a merge**: `HEAD` is the target you're replaying onto, and the `>>>>>>>` label is the commit being applied — so "keep HEAD" means keep the base, NOT your feature work. Read the `>>>>>>>` commit subject to know what's being applied.

`git log --oneline -5`; note the merge base / rebased-onto commit. For a merge, identify HEAD (usually the feature branch) vs Incoming (often origin/main simplifications). If unclear, state what you see and ask which side takes priority.

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

- **merge**: `git commit -m "[merge] Resolve conflicts: <summary>"`.
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

If pre-commit reformats (merge only), retry once. NEVER `--amend` / `--no-verify` / `push`.

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
