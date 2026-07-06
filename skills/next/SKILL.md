---
name: next
description: /next — park a discovered bug or TODO for later without stopping current work. NOT for filing bugs found during a code audit (use /bugs for that).
when_to_use: "park this, log this for later, don't fix now, note this and continue, do this next"
user-invocable: true
---
# /next — park and continue

Record a discovered issue or idea without switching context. Log it and
immediately resume whatever was in progress.

## When to use

- Found a side issue while fixing something else — park it, keep going.
- Noticed a missing feature — note it, finish the current task first.
- NOT for bugs found during a deliberate code audit — use `/bugs` for that.

## What to record

If it looks like a bug: append a one-liner to `BUGS.md` at project root.
Format: `- [ ] <description>` (create the file if missing).

If it looks like a feature or general TODO: append to `TODO.md` at project root.
Format: `- [ ] <description>` (create the file if missing).

When in doubt: `TODO.md`.

## After recording

Say one line: what was logged and where. Then continue immediately — no
summary, no context switch, no explanation of what was parked.
