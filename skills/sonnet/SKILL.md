---
name: sonnet
description: /sonnet — launch a background subagent forcing model=sonnet. NOT for routine mechanical tasks (use /haiku).
when_to_use: "do this in a sonnet sub", "spawn a sonnet sub", "use sonnet"
user-invocable: true
---

Launch the prompt after /sonnet as a background general-purpose agent (run_in_background: true, model: "sonnet").
Report what was launched. Continue immediately without waiting.

- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- ALWAYS set the Agent tool's `model: "sonnet"`.
- ALWAYS instruct the subagent to use high effort — add to the prompt: "Apply high effort reasoning for this task. Effort: high."
- For simple mechanical work (find-and-replace, renaming, single-file edits with no design calls), prefer `/haiku` instead — it's faster and cheaper.
- For hard tasks (multi-file reasoning, design decisions, cross-cutting analysis), escalate to `/opus` instead.
