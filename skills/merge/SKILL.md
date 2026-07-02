---
name: merge
description: Resolve git merge conflicts. NOT for ambiguous semantic conflicts (resolve manually).
when_to_use: "git merge conflicts, resolve conflicts, fix merge conflicts"
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

## 1. Orient

`git log --oneline -5`, check `MERGE_HEAD` / stash if present.

Identify:
- **HEAD branch**: what we had (usually the feature branch — the more important one)
- **Incoming**: what we're merging in (often origin/main simplifications)

If unclear, state what you see and ask which branch takes priority.

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

## 7. Commit

```bash
git add -u
git commit -m "[merge] Resolve conflicts: <brief summary>"
```

If pre-commit reformats, retry once.

## Priority rule (when user says "prioritize HEAD / feature branch")

- ALWAYS keep HEAD's features and additions
- ONLY take incoming changes that are pure simplifications:
  - Removing dead code
  - Simplifying logic without changing behavior
  - Bug fixes that don't conflict with HEAD features
- ALWAYS keep HEAD when in doubt about an incoming change
