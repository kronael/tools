---
name: dispatch
description: /dispatch — launch a background subagent at default model; § Tiers is the one table of every model tier, Claude and Codex. NOT for results the main thread needs inline, nor model-specific work (use the tier skill § Tiers names).
when_to_use: "sub, do this in a sub, do this in the background, run this separately, dispatch this, background agent, which model, which tier, pick a tier, claude sub or codex worker"
user-invocable: true
---

Launch the prompt after /dispatch as a background general-purpose agent (run_in_background: true).
Report what was launched. Continue immediately without waiting.

## Brief

- ALWAYS brief by GOAL, not numbered steps (WISDOM § Agents): the goal (what + why), the context it needs, what's out of bounds, and what "done" looks like — then let it choose the path. Shape: "I'm working on [larger task] for [who]. They need [what the output enables]. With that in mind: [request]." KEEP the verify-the-diff and evidence-backed-report nudges — those are load-bearing, not over-prompting.
- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS open every Codex worker brief with "Start by invoking the solve skill on this request."
  This applies to Sol, Astra, Terra and Luna. The worker lets solve choose the
  domain skill, including refine for a refine pass. NEVER prescribe domain
  skill files in its brief — ALWAYS state the goal, scope and acceptance criteria.
- ALWAYS track the run before launching and mark it complete once its result is read, using WISDOM § Agents' native checklist or work record.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline; NEVER your own analysis, suspected cause, or pointers. A written plan's decisions are not analysis — ALWAYS pass them to an executor as constraints (`sonnet` § Plan, then execute). ALWAYS quote the owner's latest decision verbatim, and NEVER keep an example that contradicts it — a sub follows the example over the words.
- NEVER assume dispatch/`general-purpose` runs cheap — it has no effort pin, so it INHERITS the parent session's effort. ALWAYS use a tier skill (§ Tiers) when a specific effort is required; only accept dispatch when the parent's inherited effort is acceptable.
- NEVER dispatch autonomous code generation here (WISDOM § Agents) — it goes to an `/opus` plan and one `/sonnet` sub per code step.

## Tiers

One lane per tier, and this table is the one place every lane is written. WISDOM § Agents owns the caps, the routes between tiers and the effort per launch; `agents/<tier>.md` and the Codex skills own the pins this table quotes, kept in step by `skills/CLAUDE.md` § Subagent effort defaults. A Claude tier launches with `subagent_type: "<tier>"`, so `agents/<tier>.md` pins its model and effort; a Codex tier runs from its skill, through the codex CLI or a native Codex worker, and counts against the cap of the Claude tier in its row.

Terra and Sol select distinct models. ALWAYS report the worker name, model ID
and effort together. NEVER infer a model ID from a worker name; ALWAYS use its pin.
The table gives defaults; WISDOM § Agents owns explicit owner overrides.

| Lane | Claude tier | Codex worker — model ID, effort |
|---|---|---|
| Read-only fan-out — mapping, grep surveys, one-file lookups — and a bounded mechanical edit with a clear spec | `/haiku` — Haiku 5.5, high | `/luna` — `gpt-6-luna`, high |
| Code implementation, investigation, bug hunts, and review fact gathering | `/sonnet` — Sonnet 5.5, high | `/terra` — `gpt-5.6-terra`, high |
| Design calls, deep analysis, implementation plans, docs rounds, refines and reviews | `/opus` — Opus 5.5, high | Sol — `gpt-6.1-sol`, high; `astra` § Sol |
| Specs, architecture, WISDOM and skill writing, algorithmic solutions, red reviews and deep audits — NEVER implementation, except a change to a globally shared library, one other repositories or teams import; a project's own library takes the regular path | `/fable` — Fable 5.1, high | `astra` — `gpt-6-astra`, high; `oracle` → `astra`, or a correctness reviewer through `refine` |

- ALWAYS take the lowest lane whose description holds the whole task, and escalate one lane — `/haiku` → `/sonnet` → `/opus` → `/fable` — when the work asks for judgment the lane lacks or a step fails twice.
- Terra builds code. ALWAYS send docs rounds, refines and reviews to Sol or
  Opus. Terra may gather facts for a review; Sol or Opus judges them.
- NEVER launch a Claude tier with `model:` — ALWAYS its agent type so the pin applies and the cap counts it. Native Codex workers use their skill's explicit model and effort settings.
- A codemod — one pattern change across many files — is no lane: it stays in the parent (`sonnet` § Plan).
