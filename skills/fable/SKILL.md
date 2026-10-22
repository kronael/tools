---
name: fable
description: /fable — most capable xhigh-effort subagent for specs, architecture, WISDOM and skill writing, algorithms, red reviews and deep audits. NOT for implementation (opus plans, sonnet steps) or tasks opus can handle (use /opus).
when_to_use: "do this in a fable sub, use fable, hardest problem, deep reasoning, write the spec, architecture, algorithm design, red review, adversarial review, security audit, deep audit"
user-invocable: true
---

Launch the prompt after /fable as a background agent (`run_in_background: true`, `subagent_type: "fable"`).
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /fable without being asked when the task is:
- A spec, an architecture, or WISDOM or skill text.
- An algorithmic solution.
- A red or adversarial review, a security or deep audit, or a user request for maximum effort.

NEVER send implementation to /fable — multi-file or autonomous code generation. ALWAYS plan it in an `opus` sub and run one `sonnet` sub per step (WISDOM § Agents).

- ALWAYS use `subagent_type: "fable"`, NEVER `model: "fable"`: `agents/fable.md` pins Fable at effort `xhigh`, and a sub without the agent type inherits the parent's effort.
- NEVER reach for `/fable` when `/opus` or the `sonnet` plan loop can do the work — ALWAYS use those first; fable is the most expensive tier.
- NEVER set effort with prompt text ("Think deeply") — ALWAYS rely on the agent file's pin.
- When fable refuses on a usage or spend limit, ALWAYS ask the user before switching: offer `astra`
  (the codex `gpt-6-astra` worker, `astra` skill) for the same brief, and launch it only on their yes —
  NEVER switch to astra or downgrade to opus silently.
- ALWAYS brief per `dispatch`: a self-contained prompt with paths, errors, scope, out-of-bounds, and what to return.
