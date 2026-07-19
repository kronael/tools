---
name: refine
description: Code refinement orchestrator. NOT for targeted fixes (use improve).
when_to_use: "finalizing a finished feature, refine this, polish this"
user-invocable: true
---

# Refine Skill

Orchestrates code refinement. Runs in main context for full conversation visibility.

## Workflow

1. **Checkpoint** - if uncommitted changes, invoke `Skill(commit, "[checkpoint]")`
2. **Validate** - run build/test, fix failures
3. **Bucket + lenses + skills** - group target files into ≤4 non-overlapping buckets. Per bucket: (a) list applicable skills by file extension and domain (e.g. .rs→rs, tests/→testing); (b) derive lenses from two sources — **code-quality lenses** from the file types AND **WISDOM lenses**: read the live WISDOM (global + project `CLAUDE.md` plus the loaded `SKILL.md` files), split it into thematic chunks (whatever the current WISDOM holds — minimality, orthogonality, fail-loud/error-handling, one-renderer-many-sinks, strict-not-magical, naming, testing, docs …), one chunk = one lens; derive from the live text, NEVER a frozen checklist. Tag each lens `simplify` (reuse / dead-code / minimization) or `correctness` (bugs, logic errors, edge cases), and scale the lens count to the diff (see Rules).
4. **Review** - parallel read-only `Task(agent="improve", model=<by tag>)`, **1-3 lenses per sub, never more** (a focused rubric beats a groupthink dump). Prompt: "Lenses: <1-3, each with the exact WISDOM excerpt or code-quality rule it checks>. Skills: <list>. Files: <bucket>. Report violations only, NO edits."
4b. **Triage findings as they return** - drop findings that (a) add abstractions, (b) target unused code (grep first), (c) conflict with the original Intent, (d) can't be verified against the codebase. A survivor that needs a redesign (new contract, changed control flow, cross-cutting) → record in `BUGS.md` as `proposed` (CLAUDE.md System-change discipline), NOT applied without sign-off. Only inline-simple survivors go to Apply.
5. **Apply** - serial Task(agent="improve") per bucket. Run build/test between buckets — abort bucket on failure. Prompt: "Skills: <list>. Findings: <aggregated>. Apply only if simpler. Reject abstractions and cleverness."
6. **Document** - spawn `Task(agent="readme")`
7. **Verify** - final build/test
8. **Commit** - if changes, invoke `Skill(commit, "[refined]")`
9. **Cleanup** - remove stale agent worktrees (detached — no branch to delete):
   ```bash
   for d in .claude/worktrees/*/; do
     git worktree remove "$d" --force
   done
   ```
10. **Summary** - what changed, main impact, no fluff, not marketing

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
- ALWAYS scale the review to the diff: a few files / tens of lines / one logical change → 1-2 lenses or an inline review in main context; NEVER fan out 3-5 agents over a ~40-line diff. Full bucket × lens fan-out is for large or risky work only.
- ALWAYS set the review `model=` by lens tag: `simplify` → sonnet, `correctness` → opus. NEVER hunt bugs on sonnet; NEVER burn opus on candidate-finding. (improve pins no model — the call site controls it.)
- ALWAYS run all steps; NEVER skip commit unless no file changes
