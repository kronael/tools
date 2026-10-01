# Source patterns

Primary sources for the procedure. These are design references, not required
dependencies or additional skills to install. The workflow prose is original.

## Owner choices and continuous execution

[GSD discuss-phase](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/workflows/discuss-phase.md)
loads prior decisions and identifies specific ambiguities that change the
implementation. Its [batch overlay](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/workflows/discuss-phase/modes/batch.md)
groups related questions into one reply. Ship uses prefilled, concrete
owner choices and a bounded batch. It keeps those choices in the active
work record, not a separate planning hierarchy.

[GSD execute-phase](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/workflows/execute-phase.md)
provides dependency-aware execution and checkpoint continuation. Its auto
mode can supply approvals and select the first decision option. Ship keeps
real owner decisions pending; automated selection cannot supply consent.

[Superpowers subagent-driven-development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md)
uses fresh task workers, continuous execution, bounded repair and a final
whole-change review. Ship uses fresh bounded workers and final acceptance.
The toolkit's `worktree`, `refine`, `review` and `commit` retain ownership
of their contracts; no imported ledger, reviewer directory or branch policy
is required.

[Anthropic feature-dev](https://github.com/anthropics/claude-code/blob/main/plugins/feature-dev/commands/feature-dev.md)
groups clarification questions after exploration and checks the result
against the feature. It also adds separate confirmations for scope,
architecture, implementation and review fixes. Ship asks at the accepted
brief's material decision boundaries, with no routine approval per phase.

## Evidence, handoff and stopping

[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
uses incremental features, git and handoff records to preserve continuity.
It identifies premature completion and missing end-to-end checks as failure
modes. Ship records acceptance evidence and exercises the actual user path.
Its existing plan and diary supply continuity; no initializer script or
parallel feature database is required.

[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
separates planning, generation and skeptical evaluation, with an agreed
verification contract per chunk. Ship turns the owner's hammer focus into
concrete cases before implementation and uses existing independent lenses.
Ambitious scope growth and open-ended quality iteration do not define its
finish line; the accepted scope and effort limits do.

[Ralph](https://github.com/snarktank/ralph)
uses small tasks, fresh contexts, retained progress and a maximum iteration
count. Ship carries counters across resumes and requires evidence before
completion. Ralph's outer shell loop, feature JSON, automatic branch setup
and reset/archive behavior are not dependencies of this rule-only skill.

[kronael/ship](https://github.com/kronael/ship)
provides a planner-worker-judge CLI, task limits and final verification.
When explicitly selected, it supplies the implementation executor within
the same flow; its defaults, resets and bundled skill installation do not
override the owner brief or toolkit policies.

## Claude Code runtime

[Dynamic workflows](https://code.claude.com/docs/en/workflows)
move orchestration into runtime scripts, support background work and
resumption, and retain tool permission checks. Ship treats Workflow as an
opted-in native executor, with the same acceptance and ownership boundaries.
Large fan-out and saved scripts are not defaults.

[Session goals](https://code.claude.com/docs/en/goal)
continue turns toward a condition; their evaluator reads surfaced evidence
rather than independently inspecting files or running commands. Ship
supplies actual results and preserves pending decisions. A goal does not
change the permission mode or authorize a gated delivery action.

[Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)
distinguish fixed-interval loops from self-paced loops. Dynamic loops end
through `ScheduleWakeup` with `stop: true`; fixed tasks have IDs for
`CronDelete`. Session lifecycle limits remain relevant. Ship uses the
exposed tools for a requested wait and cancels only its own work.
