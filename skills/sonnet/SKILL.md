---
name: sonnet
description: "/sonnet — launch a medium-effort background subagent for investigation, bug hunting, pre-review, exploration, and template-heavy coding. NOT for cheap mapping/mechanical work (use /haiku); escalate hard multi-file implementation to /opus."
when_to_use: "do this in a sonnet sub, spawn a sonnet sub, use sonnet, explore, pre-review, flagging, investigation, bug hunt, find bugs, find simplification, survey codebase, analyze codebase, read-only analysis, find places to clean up, coding, exploration, template, sonnet sub"
user-invocable: true
---

Launch the prompt after /sonnet as a background agent (run_in_background: true, subagent_type: "sonnet").
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /sonnet without being asked when the task is:
- Bug hunt, find simplification opportunities, pre-review sweep
- Read-only codebase analysis, survey, or audit
- Flag issues before implementing (scout, not executor)

- ALWAYS use `subagent_type: "sonnet"` on the Agent tool (NOT `model: "sonnet"`). The `sonnet` agent definition pins `model: sonnet` AND `effort: medium` — effort is INHERITED from the parent session when not pinned, so `model: "sonnet"` alone (no `subagent_type`) lets a Fable/Opus parent's xhigh effort leak through and run sonnet at xhigh.
- NEVER expect sonnet to run cheap just because it's not opus/fable — it is pinned at medium, not low. For lighter work, use `/haiku` instead of assuming sonnet will scale down.
- NEVER add text prompts like "Effort: high" — effort is set at the API level via the agent definition, not via prompt text.
- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- For cheap exploration, mapping, and mechanical work, prefer `/haiku`. For hard tasks (multi-file reasoning, design decisions), escalate to `/opus`.
