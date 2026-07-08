---
name: 13yo-eval
description: UX walkthrough of a web app from a 13-year-old novice's eyes (with manual access). NOT for functional/e2e testing (use testing) or visual polish (use visual).
when_to_use: "UX walkthrough, novice walkthrough, test as a 13yo, see this with fresh eyes, find what's confusing, evaluate-as-new-user, dashboard usability pass, screen-by-screen UX evaluation, find jargon and intimidation"
user-invocable: true
---

# 13yo-eval - fresh-eyes UX walkthrough

Solo UX evaluation through one persona: a bright 13-year-old novice
**who can read the manual**. Goal: find what's confusing, what only
the manual explains, what stays unclear even after the manual.
Methodology source: `<cwd>/docs/ux-13yo/research-uxtest.md`. Produced
by `scavenge`.

## When to invoke / NOT

INVOKE: UX walkthrough, fresh-eyes pass, novice walkthrough, "test as
a 13yo", post-feature usability check, periodic hygiene pass.

NOT for: functional/e2e tests (use `testing`), visual polish
(use `visual`), a11y conformance audit, performance/load testing,
apps with no users beyond the team.

## The persona

Bright, literate, will read the manual. Catches: undefined acronyms,
unexpanded jargon, screens that assume domain priors, intimidation by
density, moments where they can't predict what a click will do,
buttons whose verbs have specialised meaning.

Blind to: financial judgement, expert pain, performance, correctness.

## Consequence overlay — automatic, not optional

Run the six-prompt overlay on any screen showing:

- **numeric data the user is asked to evaluate or compare** (anything beyond decoration)
- **time-sensitive state** — data that ages, where "as of when?" matters
- **actions with external / persistent consequence** — sign, submit, commit, send, transfer, publish, deploy, schedule, delete
- **the same entity surfaced in multiple places** — cross-screen consistency only matters when entities recur
- **a distinction between preview / draft / staging and live / committed / real**

Finance is one specialisation; the same six prompts apply anywhere
state has weight outside the browser tab (admin panels, deploy tools,
schedulers, e-signing, healthcare records — anywhere the user acts
on quantified state with real-world consequence).

Six prompts, fixed order, each `pass / fail / NA` + one sentence:
1. **Units & denominators** — every number labelled?
2. **Freshness** — what timestamp / epoch?
3. **Comparability** — same metric, same name across sibling screens?
4. **Reconciliation** — number traceable to a source?
5. **Irreversibility** — real-money clearly distinguished from preview?
6. **Cross-screen consistency** — same formatting, same colour intent?

## Setup (do BEFORE running the protocol)

1. Start dev server. Note URL.
2. Identify every route and every inner panel (slide-overs, modals).
3. Create `<cwd>/docs/ux-13yo/` if missing. Drop methodology
   (`research-uxtest.md`), protocol (`protocol.md`), template
   (`report-template.md`). If they don't exist, scavenge them via
   `scavenge`.
4. **Scaffold every per-screen report file NOW**, before walking
   anything. Each file has these headings empty, ready to fill:
   - `## Cold findings (pre-manual)` — appended during steps 1–11
   - `## Post-manual findings` — appended ONLY in step 12
   - `## Glossary`, `## Consequence overlay`, `## Off-happy states`,
     `## Viewport`, `## Keyboard`, `## Delights`, `## Verdict`

   Appending as you go survives interruption. End-of-run writes do not.

## Per-screen protocol

ALWAYS in order. Append to the scaffolded file after each step.

1. **Land cold.** Fresh tab, no scroll, 5 sec. One sentence: what is
   this for, who? Skip for inner-only panels.
2. **Trunk test** (Krug). Site? Page? Main sections — without scrolling?
3. **Primary job(s).** Plural allowed for dashboards.
4. **Concrete user question.** Pick one. Answer using only the screen.
5. **First-click probe.** Two tasks. Note first click. Flag wrong
   first clicks (no statistic; label "first-click, single evaluator").
6. **Hover & inspect.** Timebox 5–8 min. Tooltips: present / missing /
   carrying essential content (essential content does not belong in
   a tooltip).
7. **Microcopy scan.** Glossary table: term → presentation → guess
   → real meaning.
8. **Consequence overlay** (mandatory if triggers above — six fixed lines).
9. **Off-happy states — ACTUALLY trigger.** Throttle, block API,
   empty filter. Imagined states are not evidence. If unreachable:
   "not observed, attempted: ___".
10. **Viewport sweep.** 1440 / 1024 / 768. Flag 375 only if mobile
    is claimed.
11. **Keyboard pass.** Tab order, focus ring, every interactive reachable.
12. **NOW read the manual.** Open `/docs` (or equivalent). Append
    every finding to `## Post-manual findings` — NEVER edit or merge
    earlier observations. Retroactive reclassification destroys the
    discoverability evidence the protocol exists to preserve.
13. **Delights.** What worked. End-of-screen.

## Classification

Each observation gets one:
- **CLEAR** — got it without help.
- **MANUAL** — manual closed the gap → discoverability bug (info
  exists, not where eye lands).
- **STILL UNCLEAR** — manual didn't close it. Sub: *docs-gap* /
  *prior-domain-knowledge* / *UI-ambiguous*.

## Finding format

```
**[cite|inference] [location]** — what happened. Persona narration
(verbatim if surfaced): "<quote>". Classification: CLEAR / MANUAL /
STILL UNCLEAR (sub). Evidence: <screenshot path or quote>.
```

Tags are **evidence types**, not severity:
- **cite** — direct evidence (screenshot, verbatim quote, click path)
- **inference** — persona reasoning without literal evidence

NEVER use severity adjectives: small, minor, major, critical, huge,
tiny, serious, important. Triage adds severity later — that's their job.

## Subagent fan-out

For ≥5 screens, fan out via subagents using the `browse` skill
(drives the `agent-browser` CLI via Bash — spell this out in the
subagent prompt).

- **Default 1–2 subagents.** 3+ only with explicit budget for
  contention (usage caps hit fast in parallel).
- Bucket related screens (Basic+Expert pair, detail panel with parent).
- Each subagent OWNS its bucket exclusively.
- **Subagents scaffold report files FIRST**, append per step.
  NEVER let a subagent write only at the end of its run — interruption
  loses everything.
- Main thread aggregates into `summary.md`.

### Salvage rule

If a subagent captured evidence (screenshots) but the report write
failed, spawn a writer-only follow-up subagent that uses the existing
evidence + a minimal re-walk. Do NOT re-run the full protocol.

## Rules

- ALWAYS scaffold per-screen report files BEFORE the walkthrough.
  Append per step. NEVER write only at the end.
- ALWAYS hard-separate `## Cold findings (pre-manual)` and
  `## Post-manual findings`. NEVER merge them.
- ALWAYS run the consequence overlay automatically on any consequential
  screen (see trigger list — quantified state + decisions, time-
  sensitive data, external-consequence actions, recurring entities,
  preview-vs-real distinctions).
- ALWAYS render the overlay as exactly six lines in the fixed order.
- ALWAYS cite evidence per finding. Findings without evidence get cut.
- ALWAYS use the `browse` skill for browser automation (spell out in
  subagent prompts).
- ALWAYS default to 1–2 subagents. 3+ only with explicit acceptance of
  contention risk.
- ALWAYS include the salvage rule above.
- NEVER use severity adjectives in findings. Tags are `cite` /
  `inference` — evidence type, not severity.
- NEVER use imagined error states as evidence — trigger them or mark
  not-observed.
- NEVER claim multi-persona coverage from one run.
- ALWAYS record methodology limits in `summary.md`: one evaluator,
  one persona, one moment in time.

## Anti-patterns

- Findings as census instead of sample.
- Importing Bailey & Wolfson 87/46 % as if it applied to solo
  screenshot tests — it doesn't; the ratio is the heuristic.
- Letting the manual influence cold observations — read it AFTER.
- Copy-editing instead of microcopy scanning — the question is
  "would a novice understand", not "is this the best wording".
- 5-second testing every inner panel — only useful on landing /
  overview screens.
- Hardcoding 375 px viewport flags on desktop-first tools.
- **Severity smuggling via adjectives.** "Major friction", "small
  issue" — replaced with `cite` / `inference` precisely to stop this.

## Reference

Full methodology: `<cwd>/docs/ux-13yo/research-uxtest.md`.
Oracle critiques (v1 + v2):
`<cwd>/docs/ux-13yo/oracle-critique.md`,
`<cwd>/docs/ux-13yo/oracle-skills-critique.md`.
Skill that produced this one: `scavenge`.
