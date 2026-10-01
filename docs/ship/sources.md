# Ship: design sources

Primary sources behind `skills/ship/`. None is a dependency, and the
skill's prose is original.

## Owner choices and continuous execution

[GSD discuss-phase](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/workflows/discuss-phase.md)
loads prior decisions and identifies the specific ambiguities that change
the implementation. Its [batch overlay](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/workflows/discuss-phase/modes/batch.md)
groups related questions into one reply. Ship takes prefilled, concrete
owner choices asked in one bounded batch and kept in the work record.

[GSD execute-phase](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/workflows/execute-phase.md)
provides dependency-aware execution and checkpoint continuation. Ship takes
dependency-ordered steps that continue from the last verified checkpoint.

[Superpowers subagent-driven-development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md)
uses fresh task workers, continuous execution, bounded repair and a final
whole-change review. Ship takes fresh bounded workers and a final acceptance
pass, run through the toolkit's `worktree`, `refine`, `review` and `commit`.

[Anthropic feature-dev](https://github.com/anthropics/claude-code/blob/main/plugins/feature-dev/commands/feature-dev.md)
groups clarification questions after exploration and checks the result
against the feature. Ship asks its questions after research starts, then
again only at a material decision boundary.

## Evidence, handoff and stopping

[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
uses incremental features, git and handoff records to preserve continuity.
It names premature completion and missing end-to-end checks as failure
modes. Ship records acceptance evidence, exercises the user path, and hands
off through its work record and diary.

[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
separates planning, generation and skeptical evaluation, with an agreed
verification contract per chunk. Ship turns the owner's hammer focus into
concrete cases before implementation and checks them with existing
independent lenses. The accepted scope and effort limits set its finish
line.

[Ralph](https://github.com/snarktank/ralph)
uses small tasks, fresh contexts, retained progress and a maximum iteration
count. Ship carries repair counters across resumes and requires evidence
before completion.

[kronael/ship](https://github.com/kronael/ship)
provides a planner-worker-judge CLI, task limits and final verification.
When the owner selects it, it executes Stage 4 under the same owner brief,
as `skills/ship/cli.md` describes.

## Claude Code runtime

[Dynamic workflows](https://code.claude.com/docs/en/workflows)
move orchestration into runtime scripts, support background work and
resumption, and retain tool permission checks. Ship runs Workflow only
after the owner opts in, inside the same acceptance and ownership
boundaries.

[Session goals](https://code.claude.com/docs/en/goal)
continue turns toward a condition. Their evaluator reads surfaced evidence
and runs no commands of its own. Ship surfaces its results to that
evaluator and keeps pending decisions pending.

[Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)
distinguish fixed-interval loops from self-paced loops. Dynamic loops end
through `ScheduleWakeup` with `stop: true`, and fixed tasks have IDs for
`CronDelete`. Session lifecycle limits apply. Ship uses the exposed tools
for a requested wait and cancels only its own loops.
