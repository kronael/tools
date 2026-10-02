---
name: audit-skill-boundaries
description: No standalone docs-audit skill — doc accuracy is the readme agent; deep audits are the persona eval-* family.
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3ae76b91-513b-4edc-9d1b-ba79473e1155
  modified: 2026-07-21T08:08:29.852Z
---

There must be NO standalone `docs-audit` skill. Documentation-vs-code accuracy
auditing is the `readme` agent's job (its step 5 "Verify claims against code").
Deep evaluative audits belong to the persona eval-* family — `ceo-eval`,
`cto-eval`, `hacker-eval`, `hiring-eval`, `eye-13yo`, orchestrated by
`eval-all`. The user's model: an audit works by impersonating a specific
user/assessor. The user also wants these eval skills to eventually impersonate
personas *more deeply* (richer first-person assessor simulation).

**Why:** During a 2026-07-21 install the user removed docs-audit, ruling a flat
doc-checker is redundant with @readme and doesn't fit the persona-audit model.

**How to apply:** Never re-propose a docs-audit skill. Route doc-accuracy work
to `@readme`; route "audit this" to the eval-* family / `eval-all`. Deepening
audits = refine eval-* via `/wisdom`, recorded in BUGS.md for sign-off first
(redesign). Related: [[demo-skill-stays-flat]].
