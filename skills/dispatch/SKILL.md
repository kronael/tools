---
name: dispatch
description: /dispatch — launch a background subagent at default model. NOT for tasks the main thread needs results from inline; NOT for model-specific work (use /haiku, /sonnet, /opus, /fable).
when_to_use: "do this in the background, run this separately, do X while I do Y, dispatch this, background agent"
user-invocable: true
---

Launch the prompt after /dispatch as a background general-purpose agent (run_in_background: true).
Report what was launched. Continue immediately without waiting.

- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- For a specific model tier, use `/haiku` (fast/cheap), `/sonnet` (coding/medium), `/opus` (complex/xhigh), or `/fable` (max/xhigh) instead.
