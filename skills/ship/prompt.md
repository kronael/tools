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

Produce a PLAN.md with: Goal, Architecture/tradeoffs (alternatives
considered and why this one), a Steps section broken into
independently-gated chunks (each step: files touched, concrete
changes, and a Gate — the exact build/test/lint command that must
pass before the next step starts), Acceptance (observable, testable
checks), and Out of scope.

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
path-scoped commit per logical change, message "[section] message".

When done, run this step's Gate command yourself and report the
actual output — not "should pass." If the gate fails, fix it before
reporting done.
```

Notes:
- Foreground (`run_in_background: false`) for the planning call — the
  orchestrator needs PLAN.md before step 2. Implementation subs can
  run in the background if the orchestrator has other steps queued,
  but steps are still applied to the tree one at a time.
- After each implementation sub returns, diff the changed files
  yourself before running the gate — a sub's "done" is a claim, not a
  verification.
