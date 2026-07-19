---
name: later
description: "Defer an idea, task, or follow-up to TODO.md. NOT for bugs (use /bugs). NOT for diary entries (use /diary)."
when_to_use: "add to TODO, defer this, come back to this, note for later, later"
user-invocable: true
---

# Later

Record a deferred item in the project's `TODO.md`. Keeps the current
conversation moving without losing the idea.

## Behaviour

**With args** (`/later <text>`): use the args as the item description, no
questions asked.

**Without args** (`/later`): ask "What do you want to defer?" then wait for
one reply.

## Where to write

1. Look for `TODO.md` at `<cwd>/TODO.md`.
2. If it exists, append a bullet under the appropriate section heading
   (match by topic, or fall back to `## Later`; create the heading if absent).
3. If it doesn't exist, emit the item inline as a code block with a note
   that no `TODO.md` was found.

## Format

Single bullet. One line. No trailing punctuation.

```
- <item description>
```

If the deferred item clearly belongs to a named section already in `TODO.md`,
append there. Otherwise append or create `## Later`.

## Recurring or timed items

If the deferred item sounds recurring or timed (keywords: every, daily, weekly,
scheduled, remind, cron), note that it belongs in a scheduler rather than
`TODO.md`, and point at `/schedule`. Don't auto-schedule — the user decides.

## Reply format

One sentence confirming what was deferred and where:

> Deferred to `TODO.md` under `## Later`: <item>

Nothing else — no preamble, no trailing summary.
