---
name: fable
description: /fable — maximum reasoning, hardest architecture, long-horizon agentic work (fable-5, xhigh). NOT for tasks opus can handle (use /opus).
when_to_use: "do this in a fable sub", "spawn a fable sub", "use fable", "use claude fable", hardest problem, maximum intelligence, long-horizon, deep reasoning, most capable
user-invocable: true
---

Launch the prompt after /fable as a background agent (run_in_background: true, subagent_type: "fable").
Report what was launched. Continue immediately without waiting.

- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- ALWAYS use `subagent_type: "fable"` on the Agent tool (NOT `model: "fable"`). The `fable` agent definition in `~/.claude/agents/fable.md` sets `model: fable` AND `effort: xhigh` — this is the only way to actually set effort on the spawned agent. The Agent tool has no `effort` parameter; `model:` alone does not set effort.
- Do NOT add text prompts like "Think deeply / Effort: xhigh" — effort is set at the API level via the agent definition, not via prompt text.
- Fable is the most capable and most expensive model — prefer `/opus` for tasks that don't require maximum intelligence.
