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
3. **Improve** - spawn improve agent via `Task(prompt, agent="improve")`
4. **Document** - spawn readme agent via `Task(prompt, agent="readme")`
5. **Verify** - final build/test
6. **Commit** - if changes, invoke `Skill(commit, "[refined]")`
7. **Summary** - what changed, main impact, no fluff, not marketing

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
- Run ALL 7 steps; skip commit only if no file changes
