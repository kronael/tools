---
name: fable
description: /fable — most capable xhigh-effort subagent for unattended multi-file code, ship plans, security or deep audits, and the hardest long-horizon work. NOT for tasks opus can handle (use /opus).
when_to_use: "do this in a fable sub, spawn a fable sub, use fable, use claude fable, hardest problem, maximum intelligence, long-horizon, deep reasoning, most capable, unattended implementation, autonomous code generation"
user-invocable: true
---

Launch the prompt after /fable as a background agent (`run_in_background: true`, `subagent_type: "fable"`).
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /fable without being asked when the task is:
- A comprehensive or multi-file change written unattended, with no review per step (global § Agents).
- The plan of a `ship` feature.
- A security or deep audit, or a user request for maximum effort.

- ALWAYS use `subagent_type: "fable"`, NEVER `model: "fable"`: `agents/fable.md` pins Fable at effort `xhigh`, and a sub without the agent type inherits the parent's effort.
- NEVER reach for `/fable` when `/opus` or the `sonnet` plan loop can do the work — fable is the most expensive tier.
- NEVER set effort with prompt text ("Think deeply") — only the agent file sets it.
- ALWAYS brief per `dispatch`: a self-contained prompt with paths, errors, scope, out-of-bounds, and what to return.
