# Plan, then execute

`SKILL.md` owns task selection and briefing. This file owns the execution loop
for a comprehensive or multi-file change. `ship` owns spec-sized delivery.

ALWAYS keep a change under roughly 200 lines or ten minutes in the parent
unless the owner asks for delegation or the change needs independent design
judgment. A mechanical pattern change is a codemod in the parent (`astgrep`
or the language's rename tool), not many worker runs.

## 1. Plan

ALWAYS dispatch a fresh planning worker with no conversation fork. It reads
the current source and names real paths and symbols. In a large or unfamiliar
tree, a bounded fact-gathering worker can first answer neutral source questions;
its output is facts with `file:line`, not a proposed design.

ALWAYS write the plan in `~/.claude/plans/`, or update the active work record
when one exists. NEVER create a second progress tree. ALWAYS apply WISDOM's
native checklist or work-record rule before the first step and at every status
change. Keep a status and snapshot SHA per step.

- ALWAYS plan top-down: the desired outcome, the design, then code steps.
  High-level product choices belong to the spec task. Detailed planning names
  exact files, symbols, code excerpts, changes, dependencies and gates.
- ALWAYS settle cross-cutting names, signatures, data shapes, error conventions
  and the existing mechanism to extend. NEVER leave competing design choices
  to separate executors.
- ALWAYS make each step one coherent change readable in one pass, normally
  no more than roughly 1,000 changed lines. A step that temporarily breaks a
  check names the break and its immediate repair dependency.
- ALWAYS give each step its files, exclusions, exact gate and expected result.
  Return an unresolved design choice to planning before assigning coding.
- ALWAYS show any material owner choice with its concrete consequences. An
  accepted scope authorizes routine execution; NEVER add a new approval pause
  without a decision outside that scope.

Completion criterion: source supports the plan, every step has explicit choices
and a gate, and no unresolved owner decision blocks its execution.

## 2. Module map

The planner's interface step. When the change has a spec (`specs` →
`spec-first.md`), ALWAYS write or complete its module map (`specs` →
`format.md` § Module map) before the first coding step, so every name § 1
settles stands in the spec beside its figure. The map is the scaffold:
NEVER write a stub module into the tree — a file exists once the step that
builds it lands the real module with its tests. A coding worker builds its
step's modules straight from their entries.

Completion criterion: every file a step owns has its entry, every
cross-cutting name § 1 settles appears in one, and the spec holds the block.

## 3. Brief

ALWAYS select a coding worker for an implementation step, a documentation
worker for a docs step, through `SKILL.md`.
Pass the step's accepted decisions verbatim as constraints, with the plan path,
owned files and gate. ALWAYS tell the worker to stop and report if source
contradicts the plan, rather than inventing a workaround. A mapped name is a
settled decision: ALWAYS brief the worker to build the module from its entry
(§ 2), and to stop and report when a mapped name must change — NEVER to
change it.

ALWAYS give it the goal and the relevant decisions, not the planner's reasoning.
ALWAYS ask for changed paths, each command and output, and every deviation.

Completion criterion: a reader without this conversation can execute the brief
without making a design choice the plan already settled.

## 4. Review each step

Before a step, ALWAYS record its snapshot SHA in the plan. `git stash create`
prints one without changing the tree or stash list; on a clean tree, use
`git rev-parse HEAD`. NEVER leave the only copy in a shell variable.

After the worker returns, ALWAYS read `git diff <snapshot>` and `git status`,
then run the gate yourself before the next dependent step. Delegated judgment
uses the review task; the parent still accepts its evidence.

- ALWAYS inspect deleted or skipped tests, loosened assertions, new lint
  suppressions, swallowed errors, stubs and TODOs, and a mapped name changed
  or missing (§ 2).
- ALWAYS search the whole repo for a renamed or removed name, including docs,
  configs and tests. NEVER rely on the worker's changed-file list alone.
- ALWAYS fix a small missed call site or name in the parent and report it.
- ALWAYS update the numbered plan and each task's status after the step.

Completion criterion: the parent's gate passes, the full diff is read, and the
plan records the accepted snapshot and evidence.

## 5. Recover

On failure, ALWAYS inspect the tree before retrying. Restore only the step's
owned changes from its snapshot, or revert its commit. Delete newly created
files by explicit name. NEVER overwrite unrelated work.

ALWAYS change the brief or implementation hypothesis and include the failed
gate output in one retry. NEVER repeat an unchanged brief or layer a retry on
an unexamined failed attempt. After the second failure, return the unresolved
design to planning or take the step over in the parent; do not silently change
the model of the same task. If the design is wrong, ALWAYS correct the plan
before executing its dependent steps. `ship` owns its own repair limits.

Completion criterion: the step passes its gate, or the plan records the revised
design, unresolved decision and next valid route.

## 6. Close

ALWAYS run the project's required full test and lint targets after the last
step, plus an end-to-end check of the goal. ALWAYS use `refine` for its scoped
whole-change audit and review/fix flow. NEVER treat green individual steps as
proof that the combined change meets acceptance.

Completion criterion: final gates have evidence, every acceptance item has a
verdict, and the report distinguishes what ran, what was read and what remains.
