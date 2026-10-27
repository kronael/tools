---
name: eval
description: Evaluation router — judge a product, codebase, UI or engineer from one fixed lens or every lens. NOT for code review (use review), logging bugs (use bugs), the case against building (use specs) or fixing findings (use refine).
when_to_use: "CEO evaluation, ROI, make vs buy, demo readiness; CTO evaluation, technical due diligence, production readiness; red eval, red-team review, adversarial code review, find what breaks, pentest; design review, design audit, is the UI good; UX walkthrough, novice walkthrough, test as a 13yo, usability pass; hiring eval, would you hire; CISO, investor, competitor perspective, assess this; run all evals, adversarial panel"
argument-hint: "[ceo|cto|red|design|novice|hiring|all] [target]"
user-invocable: true
---

# Eval — one lens, one file

Judge a target from one fixed expert perspective. Read the ONE matched file,
then follow it. Every lens is findings-only: NEVER fix during an eval — a
real defect goes to `BUGS.md` via `/bugs`, fixes go through `refine`.
ALWAYS select delegated evaluations as audit tasks through `dispatch`, including
CEO, CTO and red lenses. Its capacity limits and provider runbooks apply.
A worker assigned one lens runs it itself, without delegating it again.

## Dispatch

| Request | Read |
|---|---|
| business adoption — ROI, make vs buy, license and vendor risk, TCO; demo readiness, "would I show this?" | `ceo.md` |
| technical due diligence — build, tests, architecture, maintenance burden; "how do we run / observe this"; an SLA bet or source audit | `cto.md` |
| what breaks under a hostile expert, bad state or unlucky runtime — claim busting, durability, trust boundaries, pressure and abuse | `red.md` |
| visual and interaction craft of a UI — hierarchy, measured contrast, tokens, density, redundant channels; design-system audit | `design.md` |
| a novice's UX walkthrough of a web app — jargon, intimidation, first-click probes, consequence overlay, screen-by-screen reports | `novice.md` |
| would you hire this engineer — from a repo, demo, resume or interview notes; HFT / systems calibration | `hiring.md` |
| every applicable lens at once, one subagent each, persisted roll-up and diary pointer | `all.md` |

## Other roles

No file. Adopt the role with no softening, cite file, line, env var or spec
section for every claim, and write the memo to
`critique-<role>-<YYYYMMDD>.md` in the record dir (`ship` § Work record
names it): one-line verdict (pass / fail / conditional), top-3 strengths,
top-3 blockers, the kill shot, and the next action that would change the
verdict.

- **ciso** — threat-model gaps, compliance blockers (SOC2, HIPAA, GDPR),
  pen-test surface.
- **buyer** — enterprise procurement checklist, SLA and support gaps,
  integration story.
- **investor** — market size, moat, team signal, competitive risk.
- **competitor** — how to replicate and undercut it in six months.

## Rules

- ALWAYS keep one lens per report. A finding that belongs to another lens is
  named and routed there, never graded here.
- NEVER recycle a prior critique — re-read the target fresh each run.
- Findings are claims, not facts — the caller re-verifies load-bearing ones
  before acting (`sweep` § Verify a finding before you fix it). A hostile
  persona finds sharper defects but is not thereby more correct.
- A CEO and a CTO eval of one target stay two reports, then one synthesis
  pass: both lenses flagged it → top priority; one lens only → that domain's
  work; they disagree → escalate to the owner.
