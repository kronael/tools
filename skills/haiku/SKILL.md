---
name: haiku
description: /haiku — launch a background subagent forcing model=haiku. NOT for multi-step or cross-file work (use /sonnet or /sub).
when_to_use: "do this in a haiku sub", "spawn a haiku sub", "use haiku"
user-invocable: true
---

Launch the prompt after /haiku as a background general-purpose agent (run_in_background: true, model: "haiku").
Report what was launched. Continue immediately without waiting.

- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- ALWAYS set the Agent tool's `model: "haiku"`.
- REJECT multi-step reasoning, ambiguous design calls, or cross-file refactors — escalate to `/sonnet` or `/sub`.
