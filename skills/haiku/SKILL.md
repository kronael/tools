---
name: haiku
description: /haiku — launch a cheap, fast background subagent for mechanical single-file work. NOT for multi-step reasoning, design calls, or cross-file refactors (use /sonnet or /dispatch).
when_to_use: find and replace, rename a field, rename a variable, update a constant, add a column to a table, fix a typo everywhere, grep and report, summarize one file, list all X in file, boilerplate generation, test stub, repetitive struct fields, apply a style rule, one-liner change, swap a class name, update an import path, change a string literal, mechanical task, quick lookup, single-file edit, cheap sub, fast sub, haiku sub
user-invocable: true
---

Launch the prompt after /haiku as a background agent (run_in_background: true, subagent_type: "haiku").
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /haiku without being asked when the task is:
- One file, clear spec, no design judgment needed
- Find-and-replace / rename across a bounded set of files
- Grep + summarize (read-only survey of one area)
- Boilerplate: test stub, repetitive struct, constant list

- ALWAYS use `subagent_type: "haiku"` on the Agent tool.
- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- NEVER accept multi-step reasoning, ambiguous design calls, or cross-file refactors — ALWAYS escalate to `/sonnet` or `/dispatch`.
