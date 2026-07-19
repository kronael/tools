---
name: dispatch
description: /dispatch — launch a background subagent at default model. NOT for tasks the main thread needs results from inline; NOT for model-specific work (use /haiku, /sonnet, /opus, /fable).
when_to_use: "sub, do this in a sub, spin up a sub, do this in the background, run this separately, do X while I do Y, dispatch this, background agent"
user-invocable: true
---

Launch the prompt after /dispatch as a background general-purpose agent (run_in_background: true).
Report what was launched. Continue immediately without waiting.

- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- NEVER assume dispatch/`general-purpose` runs cheap — it has no effort pin, so it INHERITS the parent session's effort (often xhigh, when the parent is Fable/Opus). ALWAYS use a tier skill (`/haiku`, `/sonnet`, `/opus`, `/fable`) when a specific effort is required; only accept dispatch when the parent's inherited effort is acceptable.
- For a specific model tier, use `/haiku` (fast/cheap, low), `/sonnet` (coding, medium), `/opus` (complex, xhigh), or `/fable` (max, xhigh) instead.
