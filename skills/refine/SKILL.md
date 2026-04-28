---
name: refine
description: Code refinement and finalization. Orchestrates improve + readme agents, validates, tests, commits [refined] changes, polishes code.
user-invocable: true
---

# Refine Skill

Orchestrates code refinement. Runs in main context for full conversation visibility.

## Workflow

1. **Checkpoint** - if uncommitted changes, invoke `Skill(commit, "[checkpoint]")`
2. **Validate** - run build/test, fix failures
3. **Bucket + lenses + skills** - group target files into ≤4 non-overlapping buckets. Per bucket: (a) list applicable skills by file extension and domain (e.g. .rs→rs, tests/→testing); (b) read a code sample and propose 3-5 orthogonal lenses.
4. **Review** - parallel read-only `Task(agent="improve")` per (bucket × lens). Prompt: "Lens: <X>. Skills: <list>. Files: <bucket>. Report findings only, NO edits."
5. **Apply** - serial `Task(agent="improve")` per bucket. Prompt: "Skills: <list>. Findings: <aggregated>. Apply only if simpler. Reject abstractions and cleverness."
6. **Document** - spawn `Task(agent="readme")`
7. **Verify** - final build/test
8. **Commit** - if changes, invoke `Skill(commit, "[refined]")`
9. **Cleanup** - remove stale agent worktrees:
   ```bash
   for d in .claude/worktrees/*/; do
     branch=$(git -C "$d" rev-parse --abbrev-ref HEAD 2>/dev/null)
     git worktree remove "$d" --force
     [ -n "$branch" ] && git branch -D "$branch" 2>/dev/null
   done
   ```
8. **Summary** - what changed, main impact, no fluff, not marketing

## Prompt Structure

```
Intent: [user's original request, not summary]
Primary: [files to modify]
Context: [read-only reference, if needed]
```

For readme agent: list what changed (file + one-line each).

## Rules

- NEVER do improvement work yourself - delegate to improve agent
- NEVER summarize user intent - pass original request
- Explicit scope > vague "review these files"
- Run ALL 9 steps; skip commit only if no file changes
