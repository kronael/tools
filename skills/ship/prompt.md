# Agent briefs and work record

`dispatch` owns briefing style; `fable`, `sonnet` and `opus` own model
launch settings. `worktree` owns detached isolation and reconciliation.
Substitute the actual paths and owner words below; do not send this file
as a worker's task list.

## Planner brief

Plan [change] in [worktree]. The owner's request is [verbatim words].
Their accepted brief is [scope, acceptance, hammer cases, limits,
destination and authorizations]. Research the current code and relevant
prior decisions. Existing spec/plan [paths] is input to verify.

Write or update [active plan path] using the fields below. Map every
acceptance item to a deliverable and an observable check. Keep steps small
enough for a worker to finish with its gate. Respect completed commits
after verifying their code; research the remaining work. Return the plan
path, supporting code references and material decisions the owner must
settle. Planning only; implementation and public actions are out of scope.

ALWAYS launch the planner with fresh context, not a fork. It gets the owner
brief and source paths, not the orchestrator's conclusions. If planning is
interrupted, inspect the partial file before commissioning remaining work.

## Worker brief

Deliver Step [N] of [plan path] in [assigned worktree] from [fork SHA].
The owner's intent is [verbatim words]; the accepted boundaries are
[scope, exclusions, hammer cases, limits and destination].

Read the plan for context, applicable CLAUDE.md and the matched domain
skills. Own [paths]; [other paths] are read-only context. Deliver this
step's behavior and acceptance checks; later steps are outside your task.
Gate: [exact command]. Return changed paths, actual gate output, remaining
issues, and any logical commits under the `commit` skill. Public actions
belong to the main agent and their approval gates.

ALWAYS give a worker a bounded deliverable and evidence to return, not an
algorithmic script. The main agent inspects the diff and reruns the gate
after reconciliation. A background dispatch is pending work until its
result is received and verified.

## Plan fields

Keep these sections in the single active work record. The project's
spec format is owned by `specs`; cite a durable spec rather than copying it.

```markdown
# NN — Change name

## Owner brief
Request: <owner's words>
Scope / exclusions: <accepted change and what stays outside>
Acceptance: <IDs with observable behavior and required checks>
Hammer: <risk cases, thresholds, owning skills, depth / rounds>
Limits: <owner ceilings or stated defaults; used repair/review counts>
Destination: <local commits, or explicitly requested further actions>
Authorization: <owner requests; separate final approvals still needed>
Decisions: <question, options, ruling and source; unresolved dependencies>

## Starting state
Worktree / base HEAD / owned paths: <identity>
Baseline: <relevant commands and results; unrelated failures recorded>

## Design
<current-code references, chosen approach, material tradeoffs>
Spec: <path when one exists>

## Steps
### Step N — Deliverable
Depends on: <steps>
Owns: <paths>
Accepts: <acceptance IDs and concrete cases>
Gate: <exact command>
Status: <pending / running / verified / blocked / owner-deferred>
Evidence: <commit or diff, gate result, behavior check>
Attempts: <repair count, approach, evidence; review rounds>

## Final acceptance
<each acceptance ID, final evidence or exact unresolved blocker>
Delivery: <actual commit/tag/PR/deploy state; outstanding approvals>

## Resume
<next step, active worker handles, last verified commit, exact blocker>
```

ALWAYS record actual results and verified commits, not a worker's claim.
The brief, limits and acceptance stay in this record through compaction.
Reconcile user steering here before dispatching the next step.
