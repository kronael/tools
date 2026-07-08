---
name: cto-eval
description: CTO evaluation — technical adoption by default; SLA/code audit on request. NOT for exploit/attack-surface security audit (use hacker-eval).
when_to_use: "CTO evaluation, technical due diligence, production readiness, cto audit, code audit, SLA bet"
user-invocable: true
---

# CTO Eval

Dispatch:

- Technical adoption / due diligence: read `checklist.md`.
- SLA-bet / adversarial source audit: read `code-audit.md`.

Rules:

- ALWAYS run build + test first for adoption evaluations.
- ALWAYS produce a verdict using the selected mode's template.
- NEVER skip maintenance burden. Impressive code with one maintainer is still
  a liability.
- NEVER blur CTO and CEO outputs: CTO owns technical production readiness; CEO
  owns ROI and demo judgment.
- NEVER open a browser or run the UI for the code lens — read source, specs,
  tests, commit history. If judging correctness *requires* the running system,
  that gap IS a finding ("the code isn't auditable from source alone").
- When paired with a CEO eval, keep the two reports separate and run a synthesis
  pass after: both lenses flagged it → top priority; one lens only → that
  domain's work; they disagree → escalate to the owner.
