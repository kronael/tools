---
name: fin
description: /fin — finish mode, no confirmation stops. NOT for one-off commands.
when_to_use: "finish this", "keep going", "don't stop", authorizing multi-step autonomous execution, /fin
user-invocable: true
---

# /fin — finish mode

Execute until complete. Don't stop until all tasks are done.

## Behavior

1. **No stopping early** — Continue working through all pending tasks
2. **No unnecessary questions** — Only ask if results are clearly ambiguous or conflicting
3. **Verify completion** — Check all tasks are done before finishing
4. **Self-correct** — If something fails, try alternatives before asking

## When invoked

- Review current task list (if any)
- Execute all pending work
- Verify each task completed successfully
- Only stop when nothing remains or blocked by true ambiguity

## What counts as "ambiguous/conflicting"

- Two valid approaches with significant tradeoffs
- Contradictory requirements in the request
- Missing critical information that can't be inferred

## What doesn't count

- Implementation details (pick one and go)
- Minor style choices (use existing patterns)
- Uncertainty about best approach (try the obvious one first)
