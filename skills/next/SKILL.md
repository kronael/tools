---
name: next
description: /next — park a discovered bug or TODO without stopping, then keep working in the same turn; defer an owner's follow-up to TODO.md. NOT for bugs found during a deliberate code audit (use /bugs), NOT for diary entries (use /diary).
when_to_use: "park this, log this and keep going, don't fix now, note this and continue, do this next, add to TODO, defer this, note for later, later"
user-invocable: true
---
# /next — park and continue

Record a discovered issue or idea without switching context. Log it, then keep
working in the same turn.

## When to use

- Found a side issue while fixing something else — park it, keep going.
- Noticed a missing feature — note it, finish the current task first.
- The owner defers a follow-up past this session — `TODO.md`, see § Later.
- NOT for bugs found during a deliberate code audit — use `/bugs` for that.

## What to record

If it looks like a bug: append an entry to `BUGS.md` at project root, in the
`bugs` skill's § Entry format (create the file if missing).

If it looks like a feature or general TODO for this session: add it via the
`TodoWrite` tool as a new pending task. NEVER write a session TODO to
`TODO.md` or any file — § Later is the one write.

When in doubt: use `TodoWrite`. When `TodoWrite` is unavailable the item lives
in this conversation only — ALWAYS state it verbatim in the report line so it
survives in context, and still NEVER write it to a file.

## Later — defer past the session

When the owner defers an item ("later", "add to TODO", "defer this", "come back
to this"), it outlives the session: append ONE bullet (`- <item>`, one line, no
trailing punctuation) to `<cwd>/TODO.md` under the section whose topic
matches, else under `## Later` (create the heading if absent). No `TODO.md` →
emit the bullet inline and say none was found. A recurring or timed item
(every, daily, weekly, scheduled, remind, cron) belongs in a scheduler — point
at `/schedule`, NEVER auto-schedule. With no text given, ask "What do you want
to defer?" and wait for one reply.

A decision the owner owes is not a deferral: record it in `BUGS.md` with status
`needs sign-off` or `owner decision`, per the `bugs` skill § Entry format.

## After recording

Say one line: what was logged and where (`BUGS.md`, `TODO.md`, the tasks list
via `TodoWrite`, or this conversation). Then continue immediately — no summary, no
context switch, no explanation of what was parked.

NEVER end the turn on that line. ALWAYS resume the work that was in flight.
When nothing is in flight, the parked item IS the work — ALWAYS start it in the
same turn, oldest parked item first when several are waiting, marking it
`in_progress` if it is in `TodoWrite`. A § Later item is exempt: NEVER start
it — the owner deferred it past this session.
