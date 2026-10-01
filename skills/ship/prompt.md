# Ship — agent briefs

Templates for the two subagent calls in `SKILL.md`. Fill the
bracketed parts from the actual task; don't paste this file verbatim.

## Planning brief (fable, step 1)

```
Plan [feature] for [repo path]. Write the plan to
.ship/NN-NAME/PLAN.md (pick NN = next sequential number under .ship/).

Read first: project CLAUDE.md, relevant specs/ files, 2-3 most recent
.diary/*.md entries, and the code paths [feature] touches. Cite specs
by path; don't restate what's already documented, extend it.

If a plan or spec for this already exists ([path, if any]), it is
input, not truth: re-verify each claim against the code as it is now,
keep what still holds, rewrite what drifted, and name the drift in
your report.

Produce a PLAN.md matching the shape in `SKILL.md` § PLAN.md shape.
Every step carries a Gate: the exact build/test/lint command that
must pass before the next step starts. Settle every cross-cutting
choice in the plan — names, signatures, data shapes, which existing
mechanism to extend — so no implementer re-decides it. Each step is
one coherent change that leaves the tree green.

Do not implement anything — plan only. Flag any genuine ambiguity or
irreversible decision as an open question rather than guessing.
```

## Implementation brief (sonnet, step 3, one per PLAN.md step)

```
Implement Step [N] of .ship/NN-NAME/PLAN.md in [repo path]. Read the
full PLAN.md first for context, but only deliver Step [N] — later
steps are out of scope for you.

Follow the project's CLAUDE.md conventions exactly (naming, commit
format, detached-HEAD-only, no git add -A / --amend / push). Make a
path-scoped commit per logical change, message "type(scope): message".

If the code contradicts the plan, stop and report the mismatch — do
not work around it.

When done, run this step's Gate command yourself and report the
actual output — not "should pass." If the gate fails, fix it before
reporting done. Report the files changed, each command run with its
output, and every deviation from the step.
```

Notes:
- Foreground (`run_in_background: false`) for the planning call — the
  orchestrator needs PLAN.md before step 2. Implementation subs can
  run in the background if the orchestrator has other steps queued,
  but steps are still applied to the tree one at a time.
- After each implementation sub returns, diff the changed files
  yourself before running the gate — a sub's "done" is a claim, not a
  verification.
