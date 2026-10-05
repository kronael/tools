---
name: improve
description: /improve — targeted fix via subagent. NOT for full cleanup (use refine), UI fixes (use visual), or explaining code (just answer).
when_to_use: "improve this function, clean up this file, refactor without changing behavior, reduce complexity in this file"
user-invocable: true
---

# Improve — iterative criticism

Systematic improvement of code, docs, tests, configs, data models or APIs
through one loop: DO → CRITICIZE → EVALUATE → IMPROVE → VERIFY → REPEAT.
Requires the `software` skill's `code.md` for naming, style, comments and
design — ALWAYS load it first.

## Where it runs

Invoked in the main thread, ALWAYS hand the work to a subagent and keep the
conversation here: `Agent(subagent_type: sonnet)` for simplification and
cleanup, `opus` for correctness and multi-file work — the split `refine` sets
by lens tag. Open the prompt with "Load the `improve` and `software` skills
(Skill tool)", then pass `Intent:` (the user's words), `Primary:` (files to
modify) and `Context:` (read-only reference) — NEVER a summary of the request.
A subagent that loaded this skill does the work itself.

## Protocol

1. **DO** — read or run the current state; note what exists.
2. **CRITICIZE** — specific and measured: what is broken, slow (measure it),
   duplicated, missing, or against the conventions in `code.md`.
3. **EVALUATE** — Critical: blocks functionality (errors, test failures,
   security holes). Important: degrades quality (performance, duplication,
   missing docs, comments `code.md` bans left standing). Minor: naming,
   style. Ignore: bikeshedding.
4. **IMPROVE** — one issue at a time, Critical first.
5. **VERIFY** — build, test, measure again.
6. **REPEAT** from 2 until every Critical is resolved, every Important is
   fixed or documented, and criticism turns subjective. 3-5 iterations is
   typical; track them ("Iteration 1: 5 critical, 3 important → Iteration 2:
   0 critical …").

## Minimality

ALWAYS remove dead code, unused imports, unnecessary abstractions,
over-engineered solutions, comments `code.md` bans (everything but a doc
comment on an exported item), unnecessary nesting and single-use helpers.
ALWAYS prefer three similar lines over a premature abstraction. NEVER add
features beyond scope, docstrings, comments or types to unchanged code,
abstractions for one-time operations, or error handling for impossible
scenarios.

## Anti-patterns

- Criticizing without measuring — "feels messy" is not a finding.
- Several changes before one verification.
- Minor fixes before Critical ones.
- No stopping criterion.
