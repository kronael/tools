---
name: dispatch
description: /dispatch — launch a background subagent at default model. NOT for tasks the main thread needs results from inline; NOT for model-specific work (use /haiku, /sonnet, /opus, /fable).
when_to_use: "sub, do this in a sub, spin up a sub, do this in the background, run this separately, do X while I do Y, dispatch this, background agent"
user-invocable: true
---

Launch the prompt after /dispatch as a background general-purpose agent (run_in_background: true).
Report what was launched. Continue immediately without waiting.

- Spawn 1-2 subagents typically, NEVER more than 4.
- ALWAYS brief by GOAL, not numbered steps (current models degrade on over-prescription): the goal (what + why), the context it needs, what's out of bounds, and what "done" looks like — then let it choose the path. Shape: "I'm working on [larger task] for [who]. They need [what the output enables]. With that in mind: [request]." KEEP the verify-the-diff and evidence-backed-report nudges — those are load-bearing, not over-prompting.
- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline; NEVER your own analysis, suspected cause, or pointers. A written plan's decisions are not analysis — ALWAYS pass them to an executor as constraints (`sonnet` § Plan, then execute).
- NEVER assume dispatch/`general-purpose` runs cheap — it has no effort pin, so it INHERITS the parent session's effort (often xhigh, when the parent is Fable/Opus). ALWAYS use a tier skill (`/haiku`, `/sonnet`, `/opus`, `/fable`) when a specific effort is required; only accept dispatch when the parent's inherited effort is acceptable.
- NEVER dispatch autonomous code generation here — a comprehensive or multi-file change written unattended goes to `/fable` (CLAUDE.md § Agents).
- For a specific model tier, use `/haiku` (fast/cheap), `/sonnet` (investigation and plan steps, high), `/opus` (design calls, xhigh), or `/fable` (max, xhigh) instead.
