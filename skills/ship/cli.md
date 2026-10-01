# Ship CLI executor

Read only when the owner explicitly chooses the `ship` command-line tool.
It executes Stage 4 of the same owner brief and plan. The main agent still
owns refinement, final acceptance, delivery approvals and close-out.

Upstream reference: [kronael/ship](https://github.com/kronael/ship).

## Check the available executor

ALWAYS inspect the installed `ship -h` and relevant source before choosing
flags. Match its worker, timeout, turn and override controls to the accepted
brief. The upstream CLI documents `-n` for worker count, `-t` for task
timeout, `-m` for turns and `-p` for instructions passed to its agents;
installed help is the authority for the actual invocation.

ALWAYS check the driver's editing isolation, commits, repair behavior and
external actions against WISDOM and the owner limits before launch. Use one
worker for a shared tree; parallel workers need detached isolation under
`worktree`. Driver defaults are not the owner's agreed limits. If the
executor cannot honor a required boundary, present that incompatibility
as a decision rather than launching it and hoping instructions suffice.

If the CLI is absent, report the requirement. Installation is a separate
owner choice. NEVER install its bundled skill over the toolkit's `ship`;
ALWAYS keep this skill as the owner-facing controller.

## Supply the accepted work

Use the active plan or its cited spec as the input file. Ensure it carries
concrete deliverables, owned paths, acceptance checks, gates, exclusions
and worker boundaries. Do not create a second set of component plans.

ALWAYS pass the owner brief's constraints through the supported instruction
override. Workers deliver only their bounded items. Public actions stay
with the main agent and their owning approval gates.

ALWAYS preserve a matching run's state on resume. Read the actual task
status and code before selecting remaining work; NEVER pass a force-reset
flag merely to get a fresh run. A changed spec needs reconciliation with
completed commits and the accepted plan.

## Accept the result through the same gates

Run the driver with a captured process handle and output. Use runtime
notifications for its completion; `runtime.md` owns stalls and waits.
Inspect partial results before retrying a terminal failed run.

ALWAYS inspect the actual diff and commits, reconcile detached worker
outputs through `worktree`, and run the planned gates yourself. Update the
single work record with the accepted steps and evidence. Driver progress,
judge verdicts and internal state are evidence to inspect, not acceptance.

When Stage 4 passes, return to Stage 5 in `SKILL.md`. The CLI completing
never skips `refine`, selected hammer checks, final behavior verification,
or the requested delivery boundary.
