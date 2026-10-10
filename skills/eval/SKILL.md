---
name: eval
description: Evaluation router — judge a product, codebase, UI or engineer from one fixed lens (CEO, CTO, red team, design craft, novice UX, hiring, CISO/buyer/investor/competitor) or from every lens at once. NOT for code review (use review), logging bugs (use bugs), the case against building (use specs) or fixing what a lens finds (use refine).
when_to_use: "CEO evaluation, ROI, make vs buy, TCO, license risk, demo readiness; CTO evaluation, technical due diligence, production readiness, SLA bet, code audit, how do we run this; red eval, red-team review, adversarial code review, no bullshit review, find what breaks, failure-mode audit, exploitability, pentest, security-minded code audit; design review, design audit, visual design critique, contrast audit, design-system audit, is the UI good; UX walkthrough, novice walkthrough, test as a 13yo, fresh eyes, find what's confusing, usability pass, jargon; hiring eval, would you hire, top notch engineer, candidate evaluation, portfolio review, repo as hiring signal, HFT role; CISO, enterprise buyer, investor, competitor perspective, critique memo, assess this; run all evals, full evaluation, adversarial panel, evaluate from every angle"
argument-hint: "[ceo|cto|red|design|novice|hiring|all] [target]"
user-invocable: true
---

# Eval — one lens, one file

Judge a target from one fixed expert perspective. Read the ONE matched file,
then follow it. Every lens is findings-only: NEVER fix during an eval — a
real defect goes to `BUGS.md` via `/bugs`, fixes go through `refine`.

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
