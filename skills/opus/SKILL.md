---
name: opus
description: /opus — complex reasoning, design decisions, multi-file architecture (opus, xhigh). NOT for mechanical tasks (use /sonnet or /haiku).
when_to_use: "do this in an opus sub", "spawn an opus sub", "use opus", complex reasoning, architecture review, design decision, deep analysis, cross-cutting, security audit, threat model, spec writing, new protocol, new daemon, hard debugging, ambiguous requirements, performance analysis, opus sub
user-invocable: true
---

Launch the prompt after /opus as a background agent (run_in_background: true, subagent_type: "opus").
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /opus without being asked when the task is:
- Architecture decision, new protocol design, new daemon spec
- Security review, threat modeling, cross-cutting concern
- Deep analysis with ambiguous requirements
- Cross-package refactor with no clear path forward

NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
ALWAYS use `subagent_type: "opus"` on the Agent tool — the `opus` agent definition pins model=opus + effort=xhigh.
For mechanical work or straightforward tasks, prefer `/sonnet` or `/haiku`. For maximum reasoning (hardest architecture, long-horizon agentic work), escalate to `/fable`.
