# Ship CLI executor

Read only when the owner explicitly chooses the `ship` command-line tool.
It executes Stage 4 of the same owner brief and plan. The main agent still
owns refinement, final acceptance, delivery approvals and close-out.

Upstream reference: [kronael/ship](https://github.com/kronael/ship).

## Check the available executor

ALWAYS inspect the installed `ship -h` and relevant source before choosing
flags. Match its worker, timeout, turn and override controls to the accepted
brief. The upstream CLI documents `-n` for worker count, `-t` for task
timeout, `-m` for turns and `-p` for instructions passed to its agents.
Installed help is the authority for the invocation.

ALWAYS check the driver's editing isolation, commits, repair behavior and
external actions against WISDOM and the owner limits before launch. Use one
worker for a shared tree. Parallel workers need detached isolation under
`worktree`. Driver defaults are not the owner's agreed limits. If the
executor cannot honor a required boundary, present that incompatibility
as a decision rather than launching it and hoping instructions suffice.

`ship` runs `claude -p` for every role, so the launching shell needs a
login of its own: `claude auth status` must print `"loggedIn": true`. A
Claude Code session does not pass its login to the commands it runs — a
session started with `CLAUDE_CODE_OAUTH_TOKEN` shows `"loggedIn": false`
in its Bash tool, and every role fails with "Not logged in". The default
fix is the owner running `claude auth login` once outside the session.
With the owner's explicit OK in this session, a scratchpad wrapper may
instead read the token from `/proc/$CLAUDE_PID/environ`, export it and
`exec "$@"`. NEVER echo, log or commit the token.

`ship` runs every role on `--model` (env `MODEL`, default `sonnet`) with
fixed role timeouts sized for sonnet. A fable sub writes and re-verifies
the specs; `ship` then runs on its default sonnet, and the orchestrator
reads each commit's diff as it lands. A slower model needs
`TIMEOUT_SCALE=3`, or its validator fails on the 180 s timeout.
`ship -k <spec>` runs only the spec validator, which proves the
login and the spec, but it is not read-only: the validator runs with
`bypassPermissions` and can commit, so ALWAYS run it on a worktree you can
reset and check `git log` afterwards.

If the CLI is absent, report the requirement. Installation is a separate
owner choice. NEVER install its bundled skill over the toolkit's `ship`.
ALWAYS keep this skill as the owner-facing controller.

## Supply the accepted work

ALWAYS pass exactly one `.md` path — the work record or its cited spec.
With none or several, the CLI keeps its state in `.ship/` itself and
deletes that directory at start, work record included. Ensure the file
carries concrete deliverables, owned paths, acceptance checks, gates,
exclusions and worker boundaries.

Pass the owner boundaries, including that public actions stay with the main
agent, through the supported instruction override.

ALWAYS preserve a matching run's state on resume. Read the task status and
code before selecting remaining work. NEVER pass a force-reset flag merely
to get a fresh run. A changed spec needs reconciliation with completed
commits and the accepted plan.

## Accept the result through the same gates

Run the driver with a captured process handle and output. Use runtime
notifications for its completion, and `runtime.md` for stalls and waits.
Inspect partial results before retrying a terminal failed run.

Accept its output through Stage 4's diff and gate checks in `SKILL.md`,
reconciling detached worker outputs through `worktree`. Its progress and
judge verdicts count as worker reports. Record the accepted steps and
evidence in the work record.

When Stage 4 passes, return to Stage 5 in `SKILL.md`. The CLI completing
never skips `refine`, selected hammer checks, final behavior verification,
or the requested delivery boundary.
