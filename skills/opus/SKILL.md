---
name: opus
description: /opus — launch a background subagent using the opus agent definition (opus model, xhigh effort). Use for complex reasoning, design decisions, and multi-file architecture work.
when_to_use: "do this in an opus sub", "spawn an opus sub", "use opus"
user-invocable: true
---

Launch the prompt after /opus as a background agent (run_in_background: true, subagent_type: "opus").
Report what was launched. Continue immediately without waiting.

- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- ALWAYS use `subagent_type: "opus"` on the Agent tool — the `opus` agent definition pins model=opus + effort=xhigh.
- For mechanical work or straightforward tasks, prefer `/sonnet` or `/haiku`. For maximum reasoning (hardest architecture, long-horizon agentic work), escalate to `/fable`.
