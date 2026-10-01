---
name: ship
description: Drive a spec-sized change through verified delivery, mostly unattended. NOT for quick fixes (use improve) or preparing a versioned release alone (use release).
when_to_use: "ship this, ship it, let's ship, then ship, ship the feature, spec this and build it, plan and implement, build this end to end, mostly unattended, what to hammer, drive this to done"
user-invocable: true
argument-hint: "<goal or spec>"
---

# Ship

The main agent owns delivery: owner brief → fresh plan → gated changes →
refinement → acceptance → requested destination. Workers finish bounded
steps; the main agent keeps going until the owner's acceptance checks pass
or a decision needs the owner. `fin` owns persistence within that scope.

## Read on demand

Read the ONE file matching the current stage, then return here.

| Current need | Read |
|---|---|
| owner questions: outcome, what to hammer, limits, destination, decision choices | `intake.md` |
| fresh planner / worker briefs, plan fields, acceptance and progress record | `prompt.md` |
| compaction, resume, stalled work, Workflow, /goal, /loop, ScheduleWakeup | `runtime.md` |
| owner explicitly requests the `ship` CLI as executor | `cli.md` |
| primary sources behind question batching, verification and continuity | `sources.md` |

## Work record

Use the project's `.ship/` policy. Default: flat, gitignored scratch,
`.ship/plan-NN-name.md`, with the next free zero-padded NN and lowercase
kebab name. Reuse the active change's record; project layout overrides win.
The plan holds the owner brief, acceptance checks, decisions and progress.
Task-tool entries mirror it; git records the committed work.

ALWAYS keep one work record for the change; NEVER add a second progress
tree, saved review plans, or a workflow-specific backlog.

## Workflow

### 1. Recover scope and inspect the starting state

ALWAYS reconcile the owner's messages, applicable CLAUDE.md, recent diary,
existing spec/plan, git history and active workers before dispatching work.
Use `recall-memories` for referenced decisions. An owner asking to resume
uses `continue`; restrict execution here to this change's accepted scope.

Record the starting HEAD, worktree, owned paths and relevant baseline
checks. Unrelated dirt or failures stay outside the change; `bugs` owns
their record. With unrelated dirt, use `worktree` to select or create a
clean detached controller checkout before implementation. Record its identity
and preserve the original tree; an edit-in-place restriction needs a decision.
A failure that blocks acceptance becomes a decision if its
repair exceeds the requested scope. For recovery, read `runtime.md`.

Completion criterion: the active change, prior decisions and baseline are
known; completed work is identified from the code and commits.

### 2. Batch the owner brief

ALWAYS read `intake.md` and fill answered fields from the owner's words
before asking. Batch only missing owner choices, with concrete recommended
options: outcome, what to hammer, run limits, and delivery destination.
Do independent research while answers are pending.

ALWAYS distinguish an optional preference from an answer needed to build
the right result. An unanswered preference takes the stated default after
a reasonable reply window; a required answer remains pending.

Completion criterion: scope, acceptance, hammer focus, limits and finish
line are explicit, with material owner decisions answered.

### 3. Plan against the current code

ALWAYS plan in a fresh subagent with no conversation fork; use `fable` when
available. `runtime.md` covers supported role equivalents. Research the live
code and write or update the work record. Existing plans/specs are
inputs to verify, not authority about code. Read `prompt.md` for the brief
and plan fields. `dispatch` owns goal-shaped briefs and model launchers own
their effort settings; `worktree` owns editing isolation.

The main agent reads the plan and checks every requested acceptance item
has a step and an observable check. Hammer focus gets concrete failure
cases and a matching verification/review skill. Implementation details stay
with workers. Use `oracle` for a consequential unresolved plan flaw.

ALWAYS show the plan's scope, gates and finish line briefly. An approved
brief authorizes its implementation; NEVER add a routine plan-approval
pause. Ask only when research exposes a material choice outside that brief.

Completion criterion: current code supports the plan, every step has a real
gate, and no unresolved owner decision blocks the first step.

### 4. Implement and verify each step

ALWAYS dispatch one bounded step at a time through `sonnet`; use `opus`
for hard cross-file reasoning, or supported equivalents from `runtime.md`.
Follow `worktree`
for isolation and reconciliation. Parallel work needs independent owned
paths and dependencies; read-only investigations may share the tree.
If the owner explicitly chose the CLI, read `cli.md` at this same stage.

ALWAYS inspect the returned diff and run the step's gate yourself before
accepting it. A worker's commit or success report is not gate evidence.
Use `commit` for logical verified changes. Record status, commit, gate
result and next action in the same plan after each accepted step.

ALWAYS repair failures caused by this change within its accepted scope and
limits; NEVER weaken an acceptance check to get a green result. Replan the
affected remaining steps when code invalidates their premise. `runtime.md`
owns bounded recovery. `next`, `later` and `bugs` park adjacent work.

Completion criterion: each implemented step has an inspected diff, passing
gate evidence, and a recorded disposition; dependent steps never pass red.

### 5. Refine and hammer the selected risks

ALWAYS run `refine` on the change's touched paths and baseline-to-HEAD range.
Pass the current baseline-to-HEAD range and owned paths to each hammer skill;
committed work must not become an empty uncommitted-diff review.
It owns quality lenses, docs, local commits and PR-thread intake. Run the
owner-selected checks through the matching existing skills: `review` for
an independent review, `red-eval` for hostile failure cases, `cto-eval` for
operational risks, `design-eval` / `13yo-eval` for UI craft / first use.
Load only lenses justified by the brief or a concrete unresolved concern.
An explicit independent engine choice uses `codex` or `oracle`.

ALWAYS re-verify findings against the code before acting. The brief covers
fixes to defects this change causes, scoped simplification and docs. A new
product/design contract needs an owner decision; an adjacent defect goes
through `bugs`. `review` owns taking a findings list; `refine` owns its
refinement edits. Keep public replies behind `gh-comment`'s gates.

ALWAYS carry the owner boundaries into called skills. If a mandatory step
conflicts with them, obey the owner's constraints and record any proposed
contract change with `bugs`. Surface a genuinely blocked required gate
through `intake.md`; NEVER silently skip it or report the pass complete.

Completion criterion: refinement finishes, the selected risks have evidence,
and every finding is fixed, refuted, deferred or awaiting an owner decision.

### 6. Prove acceptance and prepare delivery

ALWAYS check the whole acceptance list against the final code, including
the actual user path where applicable. Build/test success alone cannot
close a behavior check. Run the project's required final checks; rerun an
affected check after a change, not a broad review merely to fill a loop.
`fin` owns the final open-items pass within the accepted scope.

ALWAYS carry the requested destination to its actual boundary. Local
commits are the default. A requested versioned release uses `release` and
its full gate. A requested PR uses `pr-draft` to prepare its exact title
and body. Push, PR creation/merge, publication and deployment follow WISDOM
and their owning skills' approval rules; a ship brief cannot waive them.
Finish all authorized preparation before presenting a gated action.

Completion criterion: every acceptance item has final evidence, local work
is committed, and the requested delivery is completed or concretely waiting
at a named external-action gate.

### 7. Close out or hand off

ALWAYS report the achieved destination, commit SHAs, check results, hammer
findings and remaining decisions. Distinguish verified local delivery,
waiting for approval, and a blocked acceptance item; NEVER call a blocked
or merely prepared destination shipped.

Use `diary` for decisions and open items, `specs` for durable architecture,
and `later` for owner-deferred follow-ups. Release notes belong to `release`.
Retain the plan while paused, blocked or waiting for delivery approval.
On completion, distill durable content, then prune only named scratch files
under the project's policy; leave directory removal to the owner.

Completion criterion: the owner can see what landed and what remains, and
unfinished work has an exact resume point.

## Review checklist

- Owner choices are batched; prior answers and approved scope are reused.
- Fresh research, worker diffs and gate output support each accepted step.
- Hammer checks target the selected risks and respect the run limits.
- Required behavior, docs, commits and destination match the acceptance list.
- Approval waits and blockers preserve the work record and remain visible.

## Anti-patterns

- Ending on a plan, worker dispatch, passing unit tests, or a prepared PR.
- Asking permission at every step or treating silence as an owner decision.
- Expanding a review into unrelated work or adding machinery to force progress.
