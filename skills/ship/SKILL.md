---
name: ship
description: Drive a spec-sized change through verified delivery, mostly unattended. NOT for quick fixes (use improve) or preparing a versioned release alone (use release).
when_to_use: "ship this, ship it, ship the feature, spec this and build it, plan and implement, build this end to end, mostly unattended, what to hammer, drive this to done"
user-invocable: true
argument-hint: "<goal or spec>"
---

# Ship

The main agent owns delivery. Workers finish bounded steps, and the main
agent keeps going until the owner's acceptance checks pass or a decision
needs the owner. `fin` owns persistence within that scope.

ALWAYS carry the owner boundaries into every worker and called skill. When
a called skill's mandatory step conflicts with them, obey the owner and
record any proposed contract change with `bugs`. Surface a genuinely
blocked required gate through `intake.md`. NEVER silently skip it or report
the pass complete.

## Files

Read the ONE file matching the current stage, then return here.

| Current need | Read |
|---|---|
| owner questions on outcome, what to hammer, limits and destination, defaults for open preferences, decision points after intake | `intake.md` |
| planner and worker brief templates, the `.claude/ship/plan-NN-name.md` fields | `prompt.md` |
| resume after compaction, stalled workers, repair and review counters, cancellation, Workflow, /goal, /loop, ScheduleWakeup | `runtime.md` |
| owner asked for the `ship` CLI as executor | `cli.md` |

## Work record

Default: flat, gitignored scratch at `.claude/ship/plan-NN-name.md`, with
the next free zero-padded NN and a lowercase kebab name. Reuse the active
change's record where it is. Project layout overrides win. The plan holds
the owner brief, acceptance checks, decisions and progress. The `assess`,
`eval-all` and `specs` critiques share the directory.

ALWAYS keep the record in the MAIN tree's `.claude/ship/` — the first entry
of `git worktree list` — and address it by absolute path from every
worktree, as `diary` does for a gitignored diary. A controller worktree's
copy is invisible from the main tree, and `git worktree remove` deletes it.
ALWAYS confirm the path is ignored before the first write: when
`git check-ignore -q .claude/ship/x` fails, append the root-anchored line
`/.claude/ship/` to `.gitignore` and commit that line alone. A project that
ignores all of `.claude/` needs nothing.
ALWAYS keep one work record for the change. NEVER add a second progress
tree, saved review plans or a workflow-specific backlog.

## Workflow

### 1. Recover scope and inspect the starting state

ALWAYS reconcile the owner's messages, applicable CLAUDE.md, recent diary,
existing spec/plan, git history and active workers before dispatching work.
Use `recall-memories` for referenced decisions. An owner asking to resume
uses `continue`. Execution here stays within this change's accepted scope.

Record the starting HEAD, worktree, owned paths and relevant baseline
checks. Unrelated dirt or failures stay outside the change, and `bugs` owns
their record. With unrelated dirt, use `worktree` to select or create a
clean detached controller checkout before implementation. ALWAYS commit
this change's own uncommitted edits and untracked tests first, or carry
them into that checkout, so only unrelated dirt stays behind. Record the
checkout's identity and keep the pre-change HEAD as the review baseline.
An edit-in-place restriction needs a decision. A failure that blocks
acceptance becomes a decision if its repair exceeds the requested scope.
For recovery, read `runtime.md`.

Completion criterion: the active change, prior decisions and baseline are
known, and completed work is identified from the code and commits.

### 2. Batch the owner brief

ALWAYS read `intake.md` before asking anything. Fill answered fields from
the owner's words, ask only the answers the result depends on, and proceed
on stated defaults for the rest.

Completion criterion: scope, acceptance, hammer focus, limits and finish
line are explicit, with material owner decisions answered.

### 3. Plan against the current code

ALWAYS plan in a fresh subagent with no conversation fork. Use `fable` when
available, and `runtime.md` for supported role equivalents. The planner
researches the live code and writes or updates the work record. Existing
plans and specs are inputs to verify, not authority about code. Read
`prompt.md` for the brief and plan fields.

The main agent reads the plan and checks every requested acceptance item
has a step and an observable check. Hammer focus gets concrete failure
cases and a matching verification or review skill. Implementation details
stay with workers. Use `oracle` for a consequential unresolved plan flaw.

ALWAYS show the plan's scope, gates and finish line briefly. An approved
brief authorizes its implementation, so NEVER add a routine plan-approval
pause. Ask only when research exposes a material choice outside that brief.
The brief never authorizes a redesign — a new contract, changed control
flow or a cross-cutting change. ALWAYS record a concrete proposal through
`bugs` and get the owner's sign-off before any redesign edit, per WISDOM.

Completion criterion: current code supports the plan, every step has a real
gate, and no unresolved owner decision blocks the first step.

### 4. Implement and verify each step

ALWAYS dispatch each bounded step to `opus`, or to `sonnet` for a
single-file or template step. `runtime.md` names supported equivalents.
Follow `worktree` for isolation and reconciliation. Parallel work needs
independent owned paths and dependencies. Read-only investigations may
share the tree. If the owner explicitly chose the CLI, read `cli.md` at
this same stage.

ALWAYS inspect the returned diff and run the step's gate yourself before
accepting it. A worker's commit or success report is not gate evidence.
Use `commit` for logical verified changes. Record status, commit, gate
result and next action in the work record after each accepted step.

ALWAYS repair failures caused by this change within its accepted scope and
limits. NEVER weaken an acceptance check to get a green result. Replan the
affected remaining steps when code invalidates their premise. `runtime.md`
owns bounded recovery. `later` and `bugs` park adjacent work.

Completion criterion: each implemented step has an inspected diff, passing
gate evidence and a recorded disposition, and dependent steps never pass red.

### 5. Refine and hammer the selected risks

ALWAYS run `refine` on the change's touched paths and baseline-to-HEAD
range. With a release destination, this pass is `release` step 1.5: run it
once, at release depth over the release range, and NEVER refine the same
range twice. Pass the same range and owned paths to each hammer skill, so
committed work never becomes an empty uncommitted-diff review. `refine`
owns quality lenses, docs, local commits and PR-thread intake.

Run the owner-selected checks through the matching existing skills:
`review` for an independent review, `red-eval` for hostile failure cases,
`cto-eval` for operational risks, `design-eval` for UI craft and `13yo-eval`
for first use. Load only lenses justified by the brief or a concrete
unresolved concern. An explicit independent engine choice uses `astra` or
`oracle`.

ALWAYS re-verify findings against the code before acting. The brief covers
fixes to defects this change causes, scoped simplification and docs. A
redesign follows the Stage 3 sign-off rule, and an adjacent defect goes
through `bugs`. `review` owns taking a findings list, and `refine` owns its
refinement edits. Keep public replies behind `gh-comment`'s gates.

Completion criterion: refinement finishes, the selected risks have evidence,
and every finding is fixed, refuted, deferred or awaiting an owner decision.

### 6. Prove acceptance and prepare delivery

ALWAYS check the whole acceptance list against the final code, including
the user path where applicable. Build/test success alone cannot close a
behavior check. Run the project's required final checks. After a change,
rerun the affected check, not a broad review merely to fill a loop. `fin`
owns the final open-items pass within the accepted scope.

Local commits are the default destination. A requested release uses
`release`, and a requested PR uses `pr-draft`. Push, PR creation and merge,
publication and deployment follow WISDOM and their owning skills' gates. A
ship brief cannot waive them.

Completion criterion: every acceptance item has final evidence, local work
is committed, and the requested delivery is completed or concretely waiting
at a named external-action gate.

### 7. Close out or hand off

ALWAYS report the achieved destination, commit SHAs, check results, hammer
findings and remaining decisions. Distinguish verified local delivery,
waiting for approval, and a blocked acceptance item. NEVER call a blocked
or merely prepared destination shipped.

Use `diary` for decisions and open items, `specs` for durable architecture,
and `later` for owner-deferred follow-ups. Release notes belong to
`release`. Retain the plan while paused, blocked or waiting for delivery
approval. On completion, distill durable content, then prune only named
scratch files under the project's policy. Directory removal is the owner's.

Completion criterion: the owner can see what landed and what remains, and
unfinished work has an exact resume point.

## Anti-patterns

NEVER end on a plan, a worker dispatch, passing unit tests or a prepared PR.
