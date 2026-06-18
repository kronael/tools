---
name: haiku
description: /haiku — launch a cheap fast background subagent for mechanical single-file work. NOT for multi-file reasoning, design calls, or cross-file refactors (use /sonnet).
when_to_use: find and replace, rename a field, rename a variable, update a constant, add a column to a table, fix a typo everywhere, grep and report, summarize one file, list all X in file, boilerplate generation, test stub, repetitive struct fields, apply a style rule, title case fix, one-liner change, swap a class name, update an import path, change a string literal, mechanical, cheap sub, fast sub, haiku sub
user-invocable: true
---

Launch the prompt after /haiku as a background agent (`run_in_background: true`, `model: "haiku"`).
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /haiku without being asked when the task is:
- One file, clear spec, no design judgment needed
- Find-and-replace / rename across a bounded set of files
- Grep + summarize (read-only survey of one area)
- Boilerplate: test stub, repetitive struct, constant list

NEVER pass a bare task — ALWAYS include: exact file paths, what to change, what to return.
ALWAYS write the prompt as if the subagent has no memory of this session.
ALWAYS set `model: "haiku"` on the Agent tool call.
REJECT multi-step reasoning, cross-file design, or ambiguous calls — use `/sonnet` instead.
