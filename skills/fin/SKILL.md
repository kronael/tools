---
name: fin
description: /fin — finish mode, no confirmation stops. NOT for a single command (just run it), NOT for resuming interrupted/paused agents or tasks from earlier in the session (use con).
when_to_use: "finish this, keep going, don't stop, just do it"
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

## Stopping discipline (the hard part)

Before declaring done, run an **open-items pass**:

1. **Re-read the most recent diary entry's open-items list.**
   Anything tagged `[open <date>]` or in a "open items for
   next session" list is a candidate.
2. **Scan your last 5 outputs in this conversation for**
   any of: "I'll … next", "still TBD", "pending", "next:",
   "next sprint", "queued", "leftover", "deferred". If you
   said it, it counts.
3. **List in-flight subagents** you spawned and haven't
   received completion for. They are pending work.

For each candidate item, classify:

- **Active (this session)** — finish it now. The user
  asked you to /fin; that means resolve.
- **Deferred (next session, with reason)** — explicit log:
  "deferred because <X>". Diary entry must reflect it.
- **Blocked (waiting on user)** — ask the user a focused
  question; do NOT silently stop.

**Never declare done with active items unresolved.**
"Tree clean + no in-flight subs" is NOT a stopping
criterion. The criterion is: every item from the open-items
pass is in Deferred or Blocked, none in Active.

### Cascade guard

If resolving an open item creates more than 3 new open items,
stop and report the cascade to the user before going deeper.
Otherwise /fin can spiral.

### Common anti-patterns

- "Natural stopping point" — no such thing in /fin. Either
  done or deferred-with-reason.
- "I have nothing in flight" — irrelevant; check the
  open-items list.
- "I'll come back to that" — fine if logged as Deferred
  with a reason. Not fine as a silent assumption.
