---
name: merge-trivial
description: Resolve git merge conflicts. Identify branches, classify each conflict as trivial (1000% clear) or ambiguous, resolve trivials immediately, ask about the rest.
user-invocable: true
---

# Trivial Merge

Resolve all merge conflicts in the working tree. Run directly in main context (no subagent).

## Step 1: Orient

```bash
git log --oneline -5
# identify what is HEAD and what is incoming
# check MERGE_HEAD or stash if present for context
```

Identify:
- **HEAD branch**: what we had (usually the feature/balance branch — the more important one)
- **Incoming**: what we're merging in (often origin/main simplifications)

If unclear from log, state what you see and ask the user which branch takes priority.

## Step 2: Find All Conflicts

```bash
grep -rln "<<<<<<< HEAD" <project_dirs>/
```

For each file, show all conflict regions:
```bash
grep -n "<<<<<<\|=======\|>>>>>>>" <file>
```

## Step 3: Classify Each Conflict

For each conflict region, classify as:

**TRIVIAL** (resolve immediately, no question needed):
- One side adds something, other side removes it → keep the addition
- Both sides add different things that are complementary → keep both
- One side is a subset of the other → keep the superset
- Pure formatting / import ordering differences → take either, let fmt fix
- One side adds a parameter that the function body already uses → keep it

**ASK** (present to user before resolving):
- Semantic API changes (e.g. `bool` → `enum`, different type for same param)
- Deleted feature that may or may not be intentional
- Two incompatible implementations of the same logic
- Missing files (need to restore from git or confirm deletion)

## Step 4: Resolve Trivials

Apply all trivial resolutions immediately. For "keep both" resolutions, order:
- Params: maintain function signature order (check function body for usage order)
- Imports: alphabetical after `cargo fmt`

After each file: `cargo check 2>&1 | grep "^error"` to catch type mismatches early.

## Step 5: Present Ambiguous Conflicts

For each ambiguous conflict, show:
- File + approximate line
- HEAD version (what we had)
- Incoming version (what we're merging)
- Why it's ambiguous (semantic change, API difference, etc.)
- Your best guess at the right resolution

Ask the user to confirm or correct.

## Step 6: Fix Compilation Errors

After resolving all conflicts:
1. `cargo check` (or equivalent)
2. Fix any type mismatches introduced by conflict resolution
3. Check for missing module declarations in lib.rs
4. Check for files deleted by one branch that are needed by the other

## Step 7: Commit

```bash
git add -u
git commit -m "[merge] Resolve conflicts: <brief summary>"
```

If pre-commit reformats, retry once.

## Key Patterns from Rust/Cargo Projects

- **Missing module files**: If lib.rs references a module that doesn't exist on disk, restore from git: `git show <commit>:path/to/file.rs > path/to/file.rs`
- **Added Cargo.toml deps**: After adding a dep, `Cargo.lock` will have unstaged changes — stage it too
- **Type API changes**: If a type changed from one branch (e.g. `bool` → `enum`, `IntEnum` → `bitflags`), it's ambiguous — ask user which to keep, then update all call sites
- **Function signature conflicts**: When HEAD adds param A and incoming adds param B, and the function body uses both → keep both params

## Priority Rule (when user says "prioritize HEAD / feature branch")

- Keep HEAD's features and additions
- Only take incoming (origin/main) changes that are pure simplifications:
  - Removing dead code
  - Simplifying logic that doesn't change behavior
  - Bug fixes that don't conflict with HEAD features
- When in doubt about incoming change: keep HEAD

## Example Session

```
Found conflicts in 3 files:
- authority_crawler.rs: 2 conflicts
- main_loop.rs: 1 conflict
- cli.rs: 3 conflicts

TRIVIAL (resolving now):
- authority_crawler.rs:72 — HEAD adds cache_db param, incoming adds first_slot → keep both (function body uses both)
- main_loop.rs:153 — same pattern → keep both

AMBIGUOUS (need your input):
- cli.rs: HEAD has bitflags VerifyMode (BALANCES|ACCOUNTS|TRANSACTIONS), incoming has IntEnum (None/Relaxed/Strict). Which API to keep?
```
