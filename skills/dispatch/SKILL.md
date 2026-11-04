---
name: dispatch
description: Delegate work by task, with an explicit model and effort. NOT for a second-opinion workflow (use oracle) or end-to-end delivery (use ship).
when_to_use: "dispatch, do this in a sub, background agent, delegate a task, pick a model, model override, coding worker, planning worker, review worker, audit worker, spec worker, documentation worker, docs worker, algorithm worker, sweep, find every call site, effort"
user-invocable: true
---

# Dispatch

ALWAYS select the task below before launching a worker. This file owns task
definitions, model choices, effort and concurrency. Workflow skills name a
task and its scope; `claude` and `codex` own provider launch mechanics.

## Task routing

ALWAYS classify by the requested output, not the file extension or the word
“design.” A product contract is a spec; exact code edits form a plan; written
docs are documentation; a challenge to the contract or plan is a review or
audit. Skill text and shared library code follow the same distinction as other
artifacts.

| Task | Requested output and boundary | Claude model / effort | Codex model / effort | Group |
|---|---|---|---|---|
| Sweep | List every call site, reference or match, or collect text that only feeds another agent; no conclusion of its own | Haiku / medium, or Sonnet / low for a wide tree | `gpt-6-luna` / medium | Lightweight |
| Mechanical | Named-file inventories, searches, one-file summaries or bounded exact edits; no unresolved judgment | Haiku / medium | `gpt-6-luna` / medium | Lightweight |
| Coding | Implement a settled plan, investigate a bug or gather nontrivial facts | Sonnet / medium | `gpt-6.1-terra` / medium | Implementation |
| Algorithm | Find or solve an algorithm — a search, an optimization, a numeric or concurrency design — even when the output is code | Opus / high | `gpt-6.1-sol` / high | Judgment |
| Documentation | Write, restructure or sync docs — README, ARCHITECTURE, CHANGELOG, CLAUDE.md, skill text, docs pages, diagrams, a shipped spec folded into docs | Opus / medium | `gpt-6.1-sol` / medium | Judgment |
| Planning | Inspect current code; name files, symbols, code excerpts, edits, dependencies and verification gates; write or complete the spec's module map (`plan.md` § Module map) | Opus / high | `gpt-6.1-sol` / high | Judgment |
| Review | Judge code or a detailed plan; verify claims and reconcile documentation with the implementation | Opus / medium | `gpt-6.1-sol` / medium | Judgment |
| Audit | Challenge a whole change, release or plan; assess systemic assumptions, CEO/CTO concerns, security or red-team risks | Fable / high | `gpt-6-astra` / high | Judgment |
| Spec | Define high-level product purpose, users, behavior, contracts, scope and acceptance; leave code edits to planning | Opus / high | `gpt-6.1-sol` / high | Judgment |

Effort is medium unless the row says otherwise. The dispatching planner MAY
raise a review to high for a risky change, and MAY keep a repeated run of one
task at medium; it reports the changed effort with the launch. ONLY a Sonnet sweep
runs at low, because its list is input that the next agent checks; a sweep
errs toward including more.

ALWAYS keep Luna within the mechanical boundary; it is not the coding
workhorse. NEVER route documentation to Coding or Terra, a settled doc edit
included — ALWAYS select Documentation. Sol uses different efforts for
different tasks. A fix found by a review or audit is coding, or documentation
when it changes docs; an unresolved contract returns to spec or planning.

ALWAYS use the current harness's provider unless the owner selects another.
A provider-only request keeps the task's model and effort from that column.
ALWAYS apply an explicit model or effort override to the named field. An
override does not change the task or its concurrency group. ALWAYS report
the task, provider, exact selected model and effort before the launch, then
the returned worker or process handle. NEVER claim a launch without its handle.

When a model override belongs to the other provider, ALWAYS use that provider's
runbook. If explicit provider and model choices conflict, ALWAYS report the
conflict before launching. If any requested choice is unsupported or unavailable,
ALWAYS report the exact limitation; NEVER silently substitute a model or effort.
An owner-approved alternative applies only within its stated scope.

ALWAYS use `oracle` for a second opinion's framing and verification. An
isolated worker remains isolated even when it uses the parent's model.
For a request spanning several tasks, ALWAYS use the execution flow below;
NEVER run a spec, implementation and review on one inherited model setting.

## Capacity

ALWAYS count active workers by task group across providers and launch methods:
at most 2 Lightweight, 2 Implementation and 1 Judgment worker. Planning,
review, audit, spec and documentation share the Judgment slot. Native workers,
CLI processes and built-in agents all count; a stricter runtime limit also
applies.

Only the owner lifts a cap, explicitly for a named task after seeing the
proposed launches. ALWAYS end that lift with its task. NEVER change the task
label, lower effort, substitute a model or split work to avoid a full slot.
ALWAYS say which task waits behind which worker, then start it when the slot
is free. NEVER treat a provider switch as extra capacity.

## Execution flow

ALWAYS read exactly the matched file when the request needs this workflow.

| Need | Read |
|---|---|
| Source-grounded implementation plan, one worker per step, parent diff review, gates and bounded recovery | `plan.md` |

ALWAYS take spec-sized, mostly unattended delivery to `ship`. A routine lookup
stays in direct tools. A small unrequested delegation stays inline under
`plan.md`'s size gate unless its owning workflow requires context isolation.
An explicit request to dispatch still delegates it.

For a single bounded task, ALWAYS launch in the background when the runtime
supports it and continue independent work. When the result is needed next,
ALWAYS wait on the same handle. NEVER imply a synchronous call runs in the
background or that elapsed time proves completion.

## Brief

- ALWAYS brief by goal: what and why, context, owned files, exclusions,
  acceptance and the required return. NEVER send a bare task or numbered
  implementation instructions in place of a self-contained goal.
- ALWAYS quote the owner's latest relevant decision verbatim. Give an executor
  the accepted plan's decisions as constraints. NEVER seed an investigator or
  reviewer with your reasoning, suspected cause or preferred conclusion.
- ALWAYS open a Codex brief with “Start by invoking the solve skill on this
  request.” Let solve choose the domain skill. NEVER prescribe domain skill
  files in a Codex brief.
- ALWAYS track the run before launching, using WISDOM's exposed native
  checklist or existing work record. Mark it complete when its result is read.
- ALWAYS ask for changed paths, commands with output, findings and deviations.
  ALWAYS inspect the diff or evidence before accepting the worker's report.
- ALWAYS obey WISDOM's shared-tree rule and use `worktree` when isolation is
  required. A worker assigned one bounded step performs it itself; NEVER
  recursively delegate that same assignment.
