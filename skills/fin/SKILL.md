---
name: fin
description: /fin — finish mode, no confirmation stops. NOT for a single command (just run it).
when_to_use: "finish this", "keep going", "don't stop", "just do it"
user-invocable: true
---

# /fin — finish mode

Execute until complete. Don't stop until all tasks are done.

## Behavior

1. **No stopping early** — Continue working through all pending tasks
2. **No unnecessary questions** — Only ask if results are clearly ambiguous or conflicting
3. **Verify completion** — Check all tasks are done before finishing
4. **Self-correct on blockers** — If something fails, find new ways. Grind harder before asking. Verification fails twice → try a third angle, not "should pass".

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
