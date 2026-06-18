---
name: sonnet
description: /sonnet — launch a background subagent at sonnet+high effort. Investigation, bug hunting, simplification sweeps, pre-review, read-only analysis. NOT for implementing changes (use /opus) or mechanical single-file work (use /haiku).
when_to_use: "do this in a sonnet sub", "spawn a sonnet sub", "use sonnet", explore, pre-review, flagging, investigation, bug hunt, find bugs, find simplification, survey codebase, analyze codebase, code review, read-only analysis, find places to clean up, sonnet sub
user-invocable: true
---

Launch the prompt after /sonnet as a background general-purpose agent (run_in_background: true, subagent_type: "sonnet").
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /sonnet without being asked when the task is:
- Bug hunt, find simplification opportunities, pre-review sweep
- Read-only codebase analysis, survey, or audit
- Flag issues before implementing (scout, not executor)

NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- ALWAYS use `subagent_type: "sonnet"` on the Agent tool (NOT `model: "sonnet"`). The `sonnet` agent definition in `~/.claude/agents/sonnet.md` sets `model: sonnet` AND `effort: high` — the only way to set effort on a spawned agent. The Agent tool has no `effort` parameter; `model:` alone does not set effort.
- Do NOT add text prompts like "Effort: high" — effort is set at the API level via the agent definition, not via prompt text.
- For simple mechanical work (find-and-replace, renaming, single-file edits with no design calls), prefer `/haiku` instead — it's faster and cheaper.
- For hard tasks (multi-file reasoning, design decisions, cross-cutting analysis), escalate to `/opus` instead.
