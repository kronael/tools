---
name: sweep-fix-verify
description: >
  Use when running a large multi-step code change, audit, or fix across
  multiple files or packages — especially when subagents are involved.
  Triggers on: "fix all bugs", "audit X", "close all gaps", "parity sweep",
  "fix everything in the split", sequential opus sub patterns.
user-invocable: true
---

# Sweep → Fix → Verify

Rigorous workflow for big multi-step code changes. Three phases, hard
sequencing, no shortcuts.

## Phase 1 — Sweep (read-only, parallel OK)

Spawn read-only subs (Sonnet/Explore) to FIND issues. Group by concern;
each sub owns one concern-bucket. Parallel is safe here — no shared writes.

Output: a bucketed issue list with file + line citations. Do NOT fix during
sweep — you'll miss scope and interleave reads with writes.

## Phase 2 — Fix (sequential, one concern per sub)

Spawn one opus sub per concern. Hard rules:

- **One concern per sub** — authz scope is not migrate enumeration is not
  dispatch lifecycle. If a "fix" spans concerns, split it.
- **Sequential on the shared tree** — NEVER run two code-editing subs in
  parallel on the same checkout. They interleave: one reverts the other's
  edits, mid-flight commits, half-edited files. Parallel is ONLY safe with
  isolated worktrees (Agent `isolation: "worktree"`).
- **Include tests** — every new param, response field, MCP tool, REST
  endpoint, or behavior change gets a test IN THE SAME SUB, not a
  follow-up. Security-sensitive changes (authz, scoping, secrets) need
  explicit isolation/cross-tenant tests. A sub that ships behavior without
  tests is not done.
- **Partial commits are broken commits** — a test file committed without
  its impl (or vice versa) leaves HEAD broken. Verify the sub committed both.

## Phase 3 — Verify the artifact, not the report

NEVER trust a sub's "all green" claim. After each sub:

```bash
make build 2>&1 | tee ./tmp/build.log && tail -5 ./tmp/build.log
make test  2>&1 | tee ./tmp/test.log  && tail -8 ./tmp/test.log && grep -E "FAIL|---" ./tmp/test.log
git diff --name-only HEAD~1
```

Check the diff yourself. If the sub claimed it added function `Foo` — grep
for it. Agent success reports are not evidence; the diff is.

## Commit discipline

After verifying each sub's output:

1. `git diff --name-only` — take the FULL list, no tail.
2. Stage an explicit file list — never `git add -A` or `git add -a`.
3. One commit per concern. Format: `[section] message`.
4. Never amend, never squash, never push.
5. Watch for parallel hazard: if another session is editing the shared
   tree (user mid-edit, another sub in flight), scope your `git add` to
   YOUR files only. Verify `git diff --cached` before committing.

## Worktree reconciliation

Full isolation + reconciliation rules: `Skill(worktree)`.

When a sub ran with `isolation: "worktree"`, bring its work back with:

```bash
git diff <fork-base> <sub-tip> -- <sub-owned-files> | git apply --3way
```

Do NOT `git cherry-pick` — on linked worktrees it silently empties and
slips HEAD. See `[[worktree_reconcile]]` memory for the full recipe.

## Hard rules (non-negotiable)

- NEVER trust a sub's "build passes" or "tests green" — run it yourself.
- NEVER run overlapping code-editing subs on the shared tree.
- NEVER commit a behavior change without its test.
- NEVER use `git add -A` or amend/squash.
- NEVER conflate multiple concerns in one sub or one commit.

## Failure modes this prevents

| Failure | Rule violated |
|---------|--------------|
| Sub commits test without impl → broken HEAD | partial-commit check |
| an auth guard committed without tests, security hole ships silently | ship-with-tests |
| cherry-pick on worktree branch empties commit, HEAD slips | worktree-reconcile |
| Two subs edit same file, one reverts the other | sequential-on-shared-tree |
| Sub says "green", build actually broken | verify-the-artifact |
| Parallel session's uncommitted edit captured by `git add -A` | explicit-file-list |

Real incidents (illustrative):
- An auth guard scaffolded but NEVER applied to routes — existed unwired for
  weeks; only caught by a full route audit, not by the original commit.
- cherry-pick on worktree branches dropped reconciled bucket work off HEAD
  twice in one session; required `git reflog` recovery both times.
- Rebuilding a service image without a required secret in `.env` crash-looped
  it; a "deployed successfully" sub report masked the actual state until the
  errors surfaced.
