---
name: software
description: Router for engineering knowledge — the language-agnostic code baseline plus deep engineering runbooks. NOT for language-specific idioms (use go/rs/py/ts/sh/sql) or terse Docker/systemd rules (ops keeps those hot).
when_to_use: "writing or reviewing code in any language, naming, boring code, abstraction discipline, over-engineering, comments policy, line width, file layout; writing tests, test failure diagnosis, testcontainers, smoke and e2e tests, test hangs; Python uv Dockerfile, m4 monorepo image, .dockerignore; Makefile for uv, CI make targets; Ansible docker-service role, deploy a service; logging format, Prometheus metrics, SLO burn-rate alerts, error-handling hierarchy; distribute a Python tool, PEP 723 script, uvx; strict typing config, ban Any, basedpyright ruff biome eslint golangci-lint, un-circumventable types; install a language server, gopls rust-analyzer pyright not found, LSP tool returns nothing, claude mcp add; race detector, sanitizers, fuzzing, Miri, goleak, property testing; fast JS for V8, hidden classes, inline caches, megamorphic, deopt, typed arrays, Wasm N-API boundary cost; money as float, currency, decimal vs integer, rounding, lamports, checked overflow; refactor stack, unreviewable branch, mutation-proven test, dead-code oracle, diffstat split, keep a stack mergeable, evidence before merging a refactor, stacked PR merge-async, base change refused part of a stack, PR has no CI runs"
---

# Software — runbook router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.

| If you need | Read |
|---|---|
| the language-agnostic baseline every language skill sits on: naming, layout, comments policy, design and abstraction limits, system-change discipline, boring-code and grug rules | `code.md` |
| a Dockerfile: Python+uv two-layer deps/source split, m4-generated monorepo images, what `.dockerignore` must exclude | `docker.md` |
| the Makefile every Python+uv repo gets — `prepare`/`build`/`test`/`right`/`image`/`clean` targets and what CI calls | `ci.md` |
| to write or fix tests: naming, reading a failure down to its cause, testcontainers, the unit/smoke/e2e boundary, hangs and gates | `testing.md` |
| to deploy a service: the Ansible docker-service role, per-deployable subdir layout | `deploy.md` |
| to make a running service legible: log format, Prometheus metrics, SLO burn-rate alerts, the error-handling hierarchy | `observe.md` |
| to hand someone a Python tool: PEP 723 single-file scripts run by uvx, when a package layout is needed instead | `uvx-tools.md` |
| lint/type config a future edit cannot loosen — exact strict flags per language (py basedpyright+ruff, ts biome or eslint, go golangci-lint) and the holes config cannot close | `strict-typing.md` |
| a language server that will not start — install, the PATH failure that causes most of it, gopls MCP registration, sandbox caveats | `lsp.md` |
| to catch bugs no type checker sees, wired as make targets: race detector, ASan/TSan/MSan/LSan, Miri, fuzzing, leak and property testing (go, rust, py) | `dynamic-analysis.md` |
| JS/TS that must be fast under V8: hidden classes, inline caches, elements kinds, deopts, typed arrays, Wasm/N-API boundary cost, and how GraalVM/Truffle differs | `js-perf.md` |
| exact arithmetic for money/token amounts: integer vs fixed-point vs arbitrary precision, deriving the overflow bound, round-once-at-the-edge, checked add | `money.md` |
| re-shipping an unreviewable branch as a reviewable stack: tests before the refactor, mutation-proven vs tautological tests, deletion oracles, byte-neutral and AST-proven moves, dead-parameter proofs, the freeze run, diffstat split; keeping the stack mergeable, the evidence each branch needs before merge, landing a native GitHub stack (merge-async, refused retargets, missing merge ref) | `refactor-stack.md` |

NEVER duplicate these runbooks into ops or language skills — link here instead.
