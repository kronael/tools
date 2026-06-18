---
name: haiku
description: /haiku — launch a background subagent at haiku speed. Fast, cheap, mechanical tasks only. NOT for multi-step reasoning or cross-file work (use /sonnet or /dispatch).
when_to_use: "do this in a haiku sub, spawn a haiku sub, use haiku, mechanical task, simple rename, quick lookup, single-file edit"
user-invocable: true
---

Launch the prompt after /haiku as a background agent (run_in_background: true, subagent_type: "haiku").
Report what was launched. Continue immediately without waiting.

- ALWAYS use `subagent_type: "haiku"` on the Agent tool.
- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- NEVER accept multi-step reasoning, ambiguous design calls, or cross-file refactors — ALWAYS escalate to `/sonnet` or `/dispatch`.
