---
name: worktree
description: Isolate a code-editing subagent when its change gets a separate PR, the user requests a worktree, or an applicable skill explicitly opts in. NOT for routine serial edits or read-only agents.
when_to_use: change gets its own PR, user requests a worktree, applicable skill explicitly opts in, reconcile worktree commits
---

# Worktree selection

Use a worktree only when a subagent's change will get its own PR, the user
explicitly requests one, or an applicable skill explicitly opts in.
Otherwise, use the shared tree with one writer at a time.

- NEVER use `isolation: "worktree"` — it creates a local branch; ALWAYS create
  a detached worktree by hand and brief the sub with its absolute path.
- NEVER isolate a change only because a subagent writes it or it spans multiple
  files — ALWAYS use the delivery boundary, the user's request or an applicable
  skill's explicit opt-in.
- NEVER run concurrent writers on the shared tree — ALWAYS include the parent
  agent, code-editing subagents and write-producing tools in the one-writer rule.
- NEVER worktree-isolate a READ-ONLY sub (review / verify / research) — ALWAYS
  let those share a stable tree.
- NEVER treat a worktree as full isolation — ALWAYS coordinate shared services,
  ports, caches and external resources.

## Reconciling a worktree sub's commits into main

- NEVER `git cherry-pick` a worktree sub's commits — on linked worktrees it
  silently empties the commit and slips HEAD.
- ALWAYS record the fork SHA when the worktree is created and apply the sub's
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

## Creating a worktree by hand

ALWAYS resolve the base to a commit SHA, then create the sub's checkout:

```bash
git worktree add --detach <repo-root>/.<name> <sha>
```

ALWAYS give the sub that path, the fork SHA and its owned files; require all
edits there and verify `git -C <path> branch --show-current` prints nothing.
ALWAYS reconcile and verify the diff before removing that specific worktree;
NEVER remove another task's worktree.
