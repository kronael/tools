# Continuity and native runtime tools

## Resume from evidence

ALWAYS inspect the work record, current HEAD and diff, relevant gate output
and worker handles after compaction or interruption. Verify recorded
commits exist and still deliver their acceptance items. Resume the first
incomplete dependency. NEVER dispatch all steps again merely because
context is fresh.

ALWAYS classify the last action as progress, a verified wait, or no progress:

- **Progress:** code, a verified step, or evidence changes the next action.
- **Verified wait:** a live worker/process/job handle is confirmed now.
- **No progress:** restated status, an unexecuted plan, or a repeated failed
  approach with no new evidence.

An observation timeout is not worker failure. Re-poll the same handle or
inspect its state. A stale lock, file or remembered dispatch does not prove
it still runs. For a terminal worker, inspect partial files and commits,
verify what landed, and commission only the unfinished work. The main agent
still owns the worker's unresolved acceptance items.

ALWAYS save the next action, active handles, last verified commit, counters
and exact blocking decision in the work record before a handoff. On a user
pause or cancellation, ALWAYS stop dispatching, stop this run's active
workers and background commands, then preserve their unique unfinished
work for the owner.

## Bound recovery and review

For a failing gate, capture its error and classify it: caused by this
change, a baseline defect, a transient external failure, or an owner choice.
Repair the change's defects. Record adjacent defects with `bugs`, and use
`intake.md` when their repair becomes a requirement outside the brief.

ALWAYS spend a repair attempt on a changed hypothesis or implementation,
not rerunning the same deterministic failure. Escalate a `sonnet` step to
`opus`, or consult `oracle`, when the current approach stalls. Retry only a
transient failure under the owning skill's rules. Count all attempts in the
work record.

When each repair reveals a new defect somewhere else, that is a wrong
architecture, not a failed hypothesis. ALWAYS stop at that signal, whatever
the attempt count, and route the redesign through the Stage 3 sign-off rule
instead of repairing again. Independent authorized steps continue while that
sign-off waits.

At an owner ceiling or the accepted repair or review limit, present
evidence and the choice to extend effort, change scope, or defer the
blocked item. NEVER reset a counter on resume or silently downgrade
acceptance. Complete independent authorized steps while the choice waits.
A blocker never counts as a passed acceptance item.

For hammer rounds, use the selected risks and confirmed findings. Stop when
their acceptance checks pass and no verified blocking finding remains.
Repeat an affected check after a fix. A clean round does not justify another
broad review. Keep required checks even when optional review effort ends.

## Native tools are conditional

ALWAYS inspect the current exposed tools and their instructions before
using a native runtime feature. Availability, permission and lifecycle
differ by client. When absent, execute the same plan with ordinary supported
tools and preserve a resume point. NEVER promise unattended work after the
session exits without a runtime that provides it.

When a named Claude agent tier is unavailable, use an exposed subagent of
appropriate capability for the same role: a fresh capable planner, a bounded
implementer, or a skeptical read-only reviewer. Use supported model and
effort controls, not invented model names or prompt text claiming an effort
setting. ALWAYS preserve fresh planner context and worker isolation. If no
suitable subagent exists, report that capability gap and complete
independent preparation. NEVER present an inline self-plan as fresh
independent research.

| Primitive | Place in this flow |
|---|---|
| Workflow | Only after the owner opts in to native workflows. Bounded orchestration of approved steps or read-only research and checks. Editing agents run one at a time or in detached worktrees created by hand per `worktree` — the runtime's isolated copies create branches. Load the native `workflow-authoring` reference before authoring a task script. The main agent accepts results and owns decisions. |
| Active session /goal | Continue toward the existing measurable acceptance condition. Surface evidence for its evaluator, which runs no checks itself. Request and acceptance of a goal follow the runtime's own rules. |
| /loop | Only for owner-requested repeated work or external state that needs polling. It repeats this plan's next safe action, not a general mandate to expand scope. |
| ScheduleWakeup | Self-paced /loop scheduling under the exposed tool's instructions. For harness-tracked background work, rely on completion notifications, with only a permitted long fallback for a hang. |

No native feature authorizes delivery. A Workflow launch, a goal Stop hook,
a continuation prompt or elapsed time never pushes, posts, publishes,
deploys or answers a pending question. When a Stop hook asks for more work,
ALWAYS report a pending owner decision as pending. NEVER fabricate consent,
mark blocked work achieved, or schedule repeated reminders for that answer.

NEVER add custom hooks, enforcement scripts, daemons or timer machinery to
make ship persist. ALWAYS use the existing skills and available native tools.

## Waits, completion and cancellation

ALWAYS use completion notifications for supported workers and builds.
External CI or deploy polling uses a delay matched to state changes and an
accepted deadline. Record what state is awaited. Stop polling on a terminal
result and return to its gate.

For a dynamic loop owned by this change, end it with
`ScheduleWakeup({stop: true})` on completion, cancellation or an owner-only
decision. A fixed loop uses `CronDelete` for its recorded task ID. Follow
the currently exposed API, and cancel or alter only loops and goals owned
by this run.

On unavailable credentials, tools or usage capacity, report the precise
limitation and leave the plan with a resume action. A rule-only skill can
coordinate an available runtime. It cannot keep a closed client running.
