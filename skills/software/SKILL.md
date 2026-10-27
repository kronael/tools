---
name: software
description: Router for engineering knowledge — the language-agnostic code baseline plus engineering runbooks. NOT for language idioms (use go/rs/py/ts/sh/sql) or terse Docker/systemd rules (ops).
when_to_use: "writing or reviewing code in any language, naming, comments policy, file layout; writing tests, test failure diagnosis, testcontainers; Python uv Dockerfile, .dockerignore; Makefile for uv, CI targets; Ansible docker-service role; logging format, Prometheus metrics, SLO alerts; PEP 723 script, uvx; strict typing config; rename a symbol, language server not found, claude mcp add; race detector, sanitizers, fuzzing, Miri; fast JS for V8; money as float, checked overflow; refactor stack, stacked PR; NOTICE file, attribution"
---

# Software — runbook router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.

| If you need | Read |
|---|---|
| the language-agnostic baseline every language skill sits on: naming, layout, comments policy, design and abstraction limits, system-change discipline, boring-code and grug rules | `code.md` |
| a Dockerfile: Python+uv two-layer deps/source split, m4-generated monorepo images, what `.dockerignore` must exclude | `docker.md` |
| the Makefile every Python+uv repo gets — `prepare`/`build`/`test`/`right`/`image`/`clean` targets and what CI calls | `ci.md` |
| to write or fix tests: naming, reading a failure down to its cause, which tests to run per edit and what a focused run proves, testcontainers, the unit/smoke/e2e boundary, hangs, gates and check durations | `testing.md` |
| to deploy a service: the Ansible docker-service role, per-deployable subdir layout | `deploy.md` |
| to make a running service legible: log format, Prometheus metrics, SLO burn-rate alerts, the error-handling hierarchy | `observe.md` |
| to hand someone a Python tool: PEP 723 single-file scripts run by uvx, when a package layout is needed instead | `uvx-tools.md` |
| lint/type config a future edit cannot loosen — exact strict flags per language (py basedpyright+ruff, ts biome or eslint, go golangci-lint) and the holes config cannot close | `strict-typing.md` |
| which tool renames a symbol, finds callers or implementers, or replaces text across files (`LSP` tool vs the `serena` skill); a language server that will not start — install, the PATH failure that causes most of it, gopls MCP registration, sandbox caveats | `lsp.md` |
| to catch bugs no type checker sees, wired as make targets: race detector, ASan/TSan/MSan/LSan, Miri, fuzzing, leak and property testing (go, rust, py) | `dynamic-analysis.md` |
| JS/TS that must be fast under V8: hidden classes, inline caches, elements kinds, deopts, typed arrays, Wasm/N-API boundary cost, and how GraalVM/Truffle differs | `js-perf.md` |
| exact arithmetic for money/token amounts: integer vs fixed-point vs arbitrary precision, deriving the overflow bound, round-once-at-the-edge, checked add | `money.md` |
| re-shipping an unreviewable branch as a reviewable stack: tests before the refactor, mutation-proven vs tautological tests, deletion oracles, byte-neutral and AST-proven moves, dead-parameter proofs, the freeze run, diffstat split, long runs (one writer per output, verified PIDs), merging the base forward through pushed layers, the evidence each branch carries, landing a native GitHub stack (merge-async, refused retargets, missing merge ref) | `refactor-stack.md` |
| to port or adapt upstream code or a skill: the `NOTICE` file format, per-file header and LICENSE retention, the attribution chain through an intermediary, license compatibility without assuming the destination license | `credits.md` |

NEVER duplicate these runbooks into ops or language skills — link here instead.
