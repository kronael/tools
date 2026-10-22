---
name: haiku
description: "/haiku — cheap, fast background subagent for read-only fan-out and a bounded mechanical edit with a clear spec. NOT for investigation or a plan step (use /sonnet), a design call (use /opus) or a codemod (stays in the parent)."
when_to_use: "do this in a haiku sub, use haiku, cheap sub, fast sub, survey the codebase, map files, grep and report, list every X, summarize one file, quick lookup, update a constant, fix a typo everywhere, single-file edit, mechanical task"
user-invocable: true
---

Launch the prompt after /haiku as a background agent (`run_in_background: true`, `subagent_type: "haiku"`).
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /haiku without being asked when the task is:
- Read-only fan-out: map files, routes or references, grep and report, summarize one file, list every X.
- A bounded mechanical edit with a clear spec and no design judgment — one file or a named set: a constant, a typo everywhere, a boilerplate stub.

- ALWAYS use `subagent_type: "haiku"`, NEVER `model: "haiku"`: `agents/haiku.md` pins Haiku 5.5 at effort `medium`, and a sub without the agent type inherits the parent's effort (xhigh under a Fable parent).
- NEVER set effort with prompt text ("Effort: low") — ALWAYS rely on the agent file's pin.
- ALWAYS brief per `dispatch`: a self-contained prompt with paths, errors, scope, out-of-bounds, and what to return.
- NEVER accept multi-step reasoning, an ambiguous spec or a cross-file refactor — ALWAYS escalate investigation and plan steps to `/sonnet`, a design call to `/opus`. A pattern change across many files is a codemod in the parent (`sonnet` § Plan), NEVER N haiku runs; a symbol rename is the language server's (`software` → `lsp.md`).
