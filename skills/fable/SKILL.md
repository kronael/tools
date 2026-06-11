---
name: fable
description: /fable — launch a background subagent forcing model=fable (claude-fable-5). Use for the hardest reasoning, hardest design decisions, and multi-file architecture work.
when_to_use: "do this in a fable sub", "spawn a fable sub", "use fable", "use claude fable"
user-invocable: true
---

Launch the prompt after /fable as a background general-purpose agent (run_in_background: true, model: "fable").
Report what was launched. Continue immediately without waiting.

- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- ALWAYS set the Agent tool's `model: "fable"`.
- ALWAYS instruct the subagent to use xhigh effort — add to the prompt: "Think deeply and use extended reasoning before acting. Effort: xhigh."
- Fable is the most capable and most expensive model — prefer `/sonnet` or `/haiku` for tasks that don't require maximum intelligence.
