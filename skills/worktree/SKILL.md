---
name: worktree
description: Isolate every code-editing subagent in its own git worktree. NOT for read-only subs (review/verify/research share the tree) or trivial single-file edits.
when_to_use: spawn a code-editing subagent, parallel subagents, run subs in parallel, isolation worktree, subwork on code, avoid conflicts between subs, reconcile a sub's commits, "fix all" with multiple agents, sequential opus subs, agent edits files
---

# Worktree isolation for code-editing subagents

Two writers on one tree interleave: mid-flight commits, one sub reverting
another's edits, reviewers reading half-edited files.

- NEVER spawn a code/file-EDITING subagent without `isolation: "worktree"` —
  ALWAYS pass it so the sub writes its own checkout.
- NEVER run more than one code-editing subagent on the shared main tree at
  once — ALWAYS run them sequentially, or give each its own worktree.
- NEVER worktree-isolate a READ-ONLY sub (review / verify / research) — ALWAYS
  let those share the tree, and parallelize them freely.
- A worktree-isolated sub shares nothing — ALWAYS parallelize those too; the
  one-writer rule binds only the SHARED tree.
- A trivial single-file edit MAY stay on the shared tree — ALWAYS first confirm
  no other writer is in flight.

## Reconciling a worktree sub's commits into main

- NEVER `git cherry-pick` a worktree sub's commits — on linked worktrees it
  silently empties the commit and slips HEAD.
- ALWAYS record the fork point when the worktree is created and apply the sub's
  diff against it, scoped to the sub's own files so out-of-scope edits don't
  leak in:

```bash
git diff <fork-base> <sub-tip> -- <sub-owned-files> | git apply --3way
```

- NEVER proceed past a `git apply --3way` that reports conflicts — ALWAYS stop,
  resolve the rejects by hand, then continue.

## Trust the diff, not the report

- NEVER act on a sub's "done / green / committed" claim — ALWAYS read its diff
  (`git diff --name-only <fork-base> <sub-tip>`) and confirm the claimed change
  is actually there.
