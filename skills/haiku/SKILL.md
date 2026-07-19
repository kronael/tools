---
name: haiku
description: /haiku — launch a cheap, fast background subagent for exploration, research, mapping, grep-style surveys, and bounded mechanical edits. NOT for multi-step reasoning, design calls, or cross-file refactors (use /sonnet or /dispatch).
when_to_use: explore cheaply, research quickly, map files, map routes, map references, grep and report, summarize one file, list all X in file, find and replace, rename a field, rename a variable, update a constant, add a column to a table, fix a typo everywhere, boilerplate generation, test stub, repetitive struct fields, apply a style rule, one-liner change, swap a class name, update an import path, change a string literal, mechanical task, quick lookup, single-file edit, cheap sub, fast sub, haiku sub
user-invocable: true
---

Launch the prompt after /haiku as a background agent (run_in_background: true, subagent_type: "haiku").
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /haiku without being asked when the task is:
- One file, clear spec, no design judgment needed
- Cheap exploration, research, mapping, and grep-style surveys
- Find-and-replace / rename across a bounded set of files
- Grep + summarize (read-only survey of one area)
- Boilerplate: test stub, repetitive struct, constant list

- ALWAYS use `subagent_type: "haiku"` on the Agent tool (NOT `model: "haiku"`). The `haiku` agent definition sets `model: haiku` AND `effort: low` — effort is INHERITED from the parent session when not set explicitly, so without this the sub could silently run at the parent's (possibly high/xhigh) effort.
- NEVER add text prompts like "Effort: low" — effort is set at the API level via the agent definition, not via prompt text.
- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- NEVER accept multi-step reasoning, ambiguous design calls, or cross-file refactors — ALWAYS escalate to `/sonnet` or `/dispatch`.
