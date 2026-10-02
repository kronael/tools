---
name: opus
description: "/opus — xhigh-effort subagent for design decisions, deep analysis, and plans that need a clean context. NOT for a plan step whose design is settled, or investigation (use /sonnet), or mechanical work (use /haiku)."
when_to_use: "do this in an opus sub, spawn an opus sub, use opus, opus sub, design decision, architecture review, deep analysis, cross-cutting analysis, complex reasoning, write the plan in a sub, plan step needs judgment, step failed twice, protocol design"
user-invocable: true
---

Launch the prompt after /opus as a background agent (`run_in_background: true`, `subagent_type: "opus"`).
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /opus without being asked when the task is:
- A design or architecture decision, or a deep cross-cutting analysis, that needs a clean context.
- The plan for bigger work when the session runs a smaller model (Sonnet, Haiku) — the plan then runs through `sonnet` § Plan, then execute.
- A plan step that leaves implementation judgment to the worker (a `ship` step by default), or that failed twice on sonnet.

- ALWAYS use `subagent_type: "opus"`, NEVER `model: "opus"`: `agents/opus.md` pins Opus at effort `xhigh`, and a sub without the agent type inherits the parent's effort.
- NEVER reach for `/opus` on a task `/sonnet` (high) can do — ALWAYS send it to `/sonnet`; xhigh thinks deeper and costs more on every call.
- NEVER set effort with prompt text — ALWAYS rely on the agent file's pin.
- ALWAYS brief per `dispatch`: a self-contained prompt with paths, errors, scope, out-of-bounds, and what to return.
- ALWAYS send autonomous code generation (WISDOM § Agents), a `ship` plan, and a security or deep audit to `/fable`.
