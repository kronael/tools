---
name: sonnet
description: /sonnet — launch a background subagent forcing model=sonnet. NOT for routine mechanical tasks (use /haiku).
when_to_use: "do this in a sonnet sub", "spawn a sonnet sub", "use sonnet"
user-invocable: true
---

Launch the prompt after /sonnet as a background general-purpose agent (run_in_background: true, subagent_type: "sonnet").
Report what was launched. Continue immediately without waiting.

- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- ALWAYS use `subagent_type: "sonnet"` on the Agent tool (NOT `model: "sonnet"`). The `sonnet` agent definition in `~/.claude/agents/sonnet.md` sets `model: sonnet` AND `effort: high` — the only way to set effort on a spawned agent. The Agent tool has no `effort` parameter; `model:` alone does not set effort.
- Do NOT add text prompts like "Effort: medium" — effort is set at the API level via the agent definition, not via prompt text.
- For simple mechanical work (find-and-replace, renaming, single-file edits with no design calls), prefer `/haiku` instead — it's faster and cheaper.
- For hard tasks (multi-file reasoning, design decisions, cross-cutting analysis), escalate to `/opus` instead.
