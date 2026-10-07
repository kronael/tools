# Agent briefs and work record

`dispatch` owns briefing style, and `fable`, `sonnet` and `opus` own model
launch settings. Fill the brackets with real paths and the owner's words.
Do not send this file as a worker's task list.

## Planner brief

Plan [change] in [worktree]. The owner's request is [verbatim words].
Their accepted brief is [scope, acceptance, hammer cases, limits,
destination and authorizations]. Research the current code and relevant
prior decisions. Existing spec/plan [paths] is input to verify.

Write or update [absolute work-record path] using the fields below. Map
every acceptance item to a deliverable and an observable check. Keep steps
small enough for a worker to finish with its gate. Respect completed commits
after verifying their code, and research the remaining work. Return the plan
path, supporting code references and material decisions the owner must
settle. Planning only. Implementation and public actions are out of scope.

The planner gets the owner brief and source paths, never the orchestrator's
conclusions.

## Worker brief

Deliver Step [N] of [absolute work-record path] in [assigned worktree] from
[fork SHA]. The owner's intent is [verbatim words]. The accepted boundaries
are [scope, exclusions, hammer cases, limits and destination].

Read the plan for context, applicable CLAUDE.md and the matched domain
skills. Own [paths]. [Other paths] are read-only context. Deliver this
step's behavior and acceptance checks. Later steps are outside your task.
Gate: [exact command] → [expected result]. Return changed paths, gate
output, remaining issues, and any logical commits under the `commit` skill.
Public actions belong to the main agent and their approval gates.

## Plan fields

`specs` owns the project's spec format. Cite a durable spec rather than
copying it.

```markdown
# NN — Change name

## Owner brief
Request: <owner's words>
Scope / exclusions: <accepted change and what stays outside>
Acceptance: <IDs with observable behavior and required checks>
Hammer: <risk cases, thresholds, owning skills, depth and rounds>
Limits: <owner ceilings or stated defaults, used repair and review counts>
Destination: <local commits, or explicitly requested further actions>
Authorization: <owner requests, separate final approvals still needed>
Decisions: <question, options, ruling, source, unresolved dependencies>

## Starting state
Worktree / baseline HEAD / owned paths: <identity>
Baseline: <relevant commands and results, unrelated failures recorded>

## Design
<current-code references, chosen approach, material tradeoffs>
Spec: <path when one exists>

## Steps
### Step N — Deliverable
Depends on: <steps>
Owns: <paths>
Accepts: <acceptance IDs and concrete cases>
Gate: <exact command> → <expected result>
Status: <pending / running / verified / blocked / owner-deferred>
Evidence: <commit or diff, gate result, behavior check>
Attempts: <repair count, approach, evidence, review rounds>

## Final acceptance
<each acceptance ID, final evidence or exact unresolved blocker>
Delivery: <commit, tag, PR or deploy state, outstanding approvals>

## Resume
<next step, active worker handles, last verified commit, exact blocker>
```

The brief, limits and acceptance stay in this record through compaction.
