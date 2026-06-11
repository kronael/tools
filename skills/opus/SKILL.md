---
name: opus
description: /opus — launch a background subagent forcing model=fable. Use for complex reasoning, design decisions, and multi-file architecture work.
when_to_use: "do this in an opus sub", "spawn an opus sub", "use opus"
user-invocable: true
---

Launch the prompt after /opus as a background general-purpose agent (run_in_background: true, model: "fable").
Report what was launched. Continue immediately without waiting.

- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- ALWAYS set the Agent tool's `model: "fable"`.
- ALWAYS instruct the subagent to use xhigh effort — add to the prompt: "Think deeply and use extended reasoning before acting. Effort: xhigh."
- For mechanical work or straightforward tasks, prefer `/sonnet` or `/haiku` — fable is for tasks requiring deep reasoning, complex architecture decisions, or synthesising across many files.
