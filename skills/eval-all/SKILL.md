---
name: eval-all
description: Run every applicable evaluation lens over one target and log a consolidated verdict for later context. NOT for a single lens (use that eval directly) or code correctness (use /code-review).
when_to_use: "run all evals, eval-all, full evaluation, evaluate from every angle, adversarial panel, all perspectives, ceo+cto+security+ux at once"
user-invocable: true
---

# eval-all — run every lens, log the results

Run all applicable evaluation lenses over one target and PERSIST a consolidated
verdict, so a later session has the context instead of re-deriving it.

## The panel
- `ceo-eval` — business adoption / ROI / demo-readiness
- `cto-eval` — technical adoption / production readiness
- `hacker-eval` — security / attack surface
- `hiring-eval` — engineer/candidate calibration (ONLY when the target is a person / portfolio / repo-as-signal)
- `eye-13yo` — novice UX walkthrough (ONLY when there's a UI to click)

## Run
1. Pick the applicable lenses. Skip `hiring-eval` / `eye-13yo` when they don't
   fit; SAY which you skipped and why (don't silently drop coverage).
2. Dispatch one subagent per lens — parallel is safe (all read-only). Each runs
   its own SKILL and returns: one-line verdict (pass / fail / conditional), top-3
   blockers, and the single kill-shot.
   Prompt shape: "Run the `<lens>` skill on `<target>`. Save your full memo to
   `.ship/critique-<lens>-<YYYYMMDD>.md`. Return verdict + top-3 blockers + kill-shot."
3. NEVER trust a sub's summary alone — READ each memo it wrote before rolling up
   (agent success reports are not evidence).

## Log (so it has context later) — ALWAYS persist, never just print
- Each lens's full memo → `.ship/critique-<lens>-<YYYYMMDD>.md` (the eval skills
  already write these).
- A consolidated roll-up → `.ship/eval-all-<YYYYMMDD>.md`: per-lens verdict +
  blockers, the cross-cutting kill-shot, and the one next action.
- A one-line pointer via `/diary`: "eval-all `<target>`: N lenses, worst verdict
  `<X>`, kill-shot `<Y>` — see `.ship/eval-all-<date>.md`" so `/recall-memories`
  finds it next session.
- Any concrete real defect a lens surfaces → log to `BUGS.md` via `/bugs`
  (record-only; NEVER fix here — Bug Triage Protocol).

## Report (≤ 20 lines)
Verdict table (lens → verdict → kill-shot), the single most important next
action, and the `.ship/eval-all-<date>.md` path.

## Rules
- ALWAYS run lenses as independent subagents, never inline — keeps each
  adversarial and uncontaminated by the others.
- ALWAYS read the memos before the roll-up; success reports are not evidence.
- ALWAYS persist to `.ship/` + a diary pointer. An eval with no log has no
  context later — that is the whole point of this skill.
- NEVER fix what a lens finds — record to `BUGS.md` and move on.
