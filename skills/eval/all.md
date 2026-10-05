# All lenses — run every one, log the results

Run all applicable evaluation lenses over one target and PERSIST a consolidated
verdict, so a later session has the context instead of re-deriving it.

## The panel
- `ceo.md` — business adoption / ROI / demo-readiness
- `cto.md` — technical adoption / production readiness
- `red.md` — failure modes / attack surface
- `design.md` — design craft (ONLY when there's a rendered UI)
- `novice.md` — novice UX walkthrough (ONLY when there's a UI to click)
- `hiring.md` — engineer/candidate calibration (ONLY when the target is a person / portfolio / repo-as-signal)

## Run
1. Pick the applicable lenses. Skip `design.md` / `novice.md` / `hiring.md`
   when they don't fit; SAY which you skipped and why (don't silently drop
   coverage).
2. Dispatch one subagent per lens — parallel is safe (all read-only). Each
   loads the `eval` skill, reads its ONE lens file and returns: one-line
   verdict (pass / fail / conditional), top-3 blockers, and the single
   kill-shot.
   Prompt shape: "Load the `eval` skill, read `<lens>.md` and run that lens on
   `<target>`. Save your full memo to
   `.claude/plans/critique-<lens>-<YYYYMMDD>.md`. Return verdict + top-3
   blockers + kill-shot."
3. NEVER trust a sub's summary alone — READ each memo it wrote before rolling up
   (agent success reports are not evidence).

## Log (so it has context later) — ALWAYS persist, never just print
- Each lens's full memo → `.claude/plans/critique-<lens>-<YYYYMMDD>.md`. The
  individual eval skills don't all persist by default, so the RUN prompt above
  tells each subagent to write its memo there — verify the file landed.
- A consolidated roll-up → `.claude/plans/eval-all-<YYYYMMDD>.md`: per-lens
  verdict + blockers, the cross-cutting kill-shot, and the one next action.
- A one-line pointer via `/diary`: "eval-all `<target>`: N lenses, worst verdict
  `<X>`, kill-shot `<Y>` — see `.claude/plans/eval-all-<date>.md`" so
  `/recall-memories` finds it next session.
- Any concrete real defect a lens surfaces → log to `BUGS.md` via `/bugs`
  (record-only; NEVER fix here — Bug Triage Protocol).

## Report (≤ 20 lines)
Verdict table (lens → verdict → kill-shot), the single most important next
action, and the `.claude/plans/eval-all-<date>.md` path.

## Rules
- ALWAYS run lenses as independent subagents, never inline — keeps each
  adversarial and uncontaminated by the others.
- ALWAYS read the memos before the roll-up; success reports are not evidence.
- ALWAYS persist to `.claude/plans/` (`ship` § Work record owns the directory
  and its ignore rule) + a diary pointer. An eval with no log has no context
  later — that is the whole point of this skill.
- NEVER fix what a lens finds — record to `BUGS.md` and move on.
