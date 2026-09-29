---
name: demo-skill-stays-flat
description: "The demo skill is intentionally a flat top-level skill, not a software/ router file"
metadata:
  node_type: memory
  type: project
  originSessionId: 4738df0b-f556-435c-b85d-20cb9fb4a941
---

`skills/demo/SKILL.md` is deliberately kept as a FLAT top-level skill, not
folded into the `software/` router as `software/demo.md`.

**Why:** the user explicitly asked for a demo skill "directly" and confirmed
the flat placement. A discoverability review (2026-07-03) argued it *should*
be a router file — it's not user-invocable, it's a runbook sibling of
`ci.md`, and a flat skill burns a preloaded description entry. That argument
is sound but was overruled by the user's explicit decision.

**How to apply:** do NOT re-propose moving `demo` into `software/`. If a
future audit re-flags it, note this decision and move on. Related:
[[software-router-conventions]].
