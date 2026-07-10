---
name: hiring-eval
description: Hiring evaluation from artifacts, repos, demos, resumes, or interview evidence. Use for "would you hire this engineer?", "top notch?", senior/staff calibration, HFT/systems candidate assessment, and what evidence would change the decision. NOT for production adoption of a project (use cto-eval) or business/demo ROI (use ceo-eval).
when_to_use: "hiring eval, candidate evaluation, would you hire, top notch engineer, senior engineer, staff engineer, HFT role, systems engineer interview, portfolio review, repo as hiring signal, artifact evaluation"
user-invocable: true
---

# Hiring Eval

Evaluate the person, not the product. The output is a hiring recommendation
grounded in evidence, with explicit uncertainty and a concrete bar for changing
the decision.

## Dispatch

- Artifact only: evaluate signal quality and missing evidence.
- Artifact + repo: inspect the repo, run available checks, and sample core code.
- Interview notes: separate observed behavior from interviewer inference.
- HFT / low-latency / systems role: apply the HFT addendum below.

If the user asks for a "very critical" read, do not soften the conclusion.
Still distinguish "not proven" from "bad".

## Evidence Order

Use the strongest available evidence first:

1. Working code and tests you can run.
2. Core implementation files and failure-path tests.
3. Bench harnesses, raw data, and methodology.
4. Architecture docs, bug logs, design notes, and runbooks.
5. Demo videos, terminal casts, README claims, resumes, and prose.

Never treat a polished demo, README, or benchmark table as proof by itself.

## Required Checks

For a repo-backed evaluation:

```sh
git status --short
make test
make build
make lint
```

Adapt commands to the project if no Makefile exists. If a command fails because
of local tooling, say exactly why, make the smallest reversible environment
adjustment needed, and retry when reasonable.

Then inspect:

- repo shape, commit recency, and ownership burden
- test count and ignored/skipped test categories
- core domain code, not just CLI/UI wrappers
- benchmark harnesses and benchmark reports
- bug tracker / TODO / known gaps
- docs that distinguish aspiration from measured fact

## Judgment Dimensions

Score mentally; do not print a numeric score unless asked.

- **Technical depth:** understands the domain constraints, not just libraries.
- **Correctness rigor:** tests invariants, failure modes, replay/recovery,
  edge cases, concurrency, and invalid inputs.
- **Performance rigor:** uses credible baselines, p50/p99/p999/max where
  relevant, avoids coordinated omission, explains hardware and methodology.
- **Taste:** simple boundaries, few moving parts, no gratuitous abstraction,
  honest tradeoffs.
- **Operational maturity:** observability, health checks, deploy model,
  recovery runbooks, limits, backpressure, maintenance story.
- **Communication:** claims are precise, caveated, and falsifiable.
- **Self-criticism:** known gaps are named plainly and prioritized.
- **Team risk:** bus factor, maintainability, ability to work in a team,
  overfitting to personal tooling, tendency to grandstand.

## HFT / Low-Latency Addendum

For HFT, require evidence beyond "fast":

- tail latency: p99, p999, max, jitter, and saturation behavior
- benchmark setup: CPU model, kernel, governor, isolation, IRQ affinity,
  NIC/driver if applicable, warmup, sample size, raw data
- measurement integrity: no coordinated omission, realistic baselines,
  tuned competitors, repeatability
- hot-path discipline: allocation, syscalls, locks, atomics, cache layout,
  false sharing, backpressure
- failure semantics: packet loss, gaps, replay, duplicate messages,
  partial writes, crash recovery, clock issues, restart behavior
- exchange-domain correctness: price-time priority, order lifecycle,
  risk checks, position accounting, liquidation/funding, audit trail,
  exactly-once/at-most-once boundaries
- production constraints: kill switches, observability, deterministic replay,
  deploy/rollback, incident handling

An HFT "top notch" hire must show both mechanical sympathy and paranoia about
correctness. Low p50 without tail/failure evidence is not enough.

## Verdicts

Use one of these:

- **HIRE STRONG** — clear evidence of exceptional engineering for the target
  role; remaining gaps are normal onboarding/domain gaps.
- **HIRE** — strong evidence; some risks, but likely worth hiring.
- **ONSITE / DEEP INTERVIEW** — promising, but not enough evidence for a hire
  without targeted probing.
- **NO HIRE FOR THIS ROLE** — may be good, but evidence misses role-critical
  requirements.
- **NO HIRE** — evidence shows poor judgment, weak fundamentals, or high team
  risk.

Default to **ONSITE / DEEP INTERVIEW** when artifacts are impressive but the
role-critical proof is incomplete.

## Output Template

Keep the answer direct:

```md
**Verdict:** <verdict>

<1-3 sentence bottom line.>

Why:
- <evidence-backed point>
- <evidence-backed point>

Concerns:
- <role-critical gap or risk>
- <role-critical gap or risk>

What would change my mind:
1. <specific evidence>
2. <specific evidence>
3. <specific evidence>
```

If the user asked for a CTO-style hiring view, phrase the bar in business terms:
"Would I trust this person near the matching/risk path?" and "What interview
must de-risk before offer?"

## Interview Probes

When useful, include 3-6 probes:

- Ask them to explain the hardest bug or wrong assumption in the project.
- Ask for a raw benchmark run and have them defend methodology.
- Pick a failure scenario and make them walk through exact state transitions.
- Ask where they would delete code.
- Ask what they would not ship to production yet.
- Ask them to compare against a serious alternative and name where theirs loses.

## Rules

- NEVER infer "top notch" from polish alone.
- NEVER punish ambition by itself; punish unsupported claims.
- NEVER conflate product readiness with candidate ability.
- NEVER ignore maintenance burden or team-fit risk.
- ALWAYS say what evidence would change the verdict.
- ALWAYS separate observed facts from inference.
