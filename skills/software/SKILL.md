---
name: software
description: Router for engineering knowledge — the language-agnostic code baseline (naming, style, boring-code, design) plus deep runbooks for tests, Docker images, CI Makefiles, deploys, observability, Python tool distribution, exact money arithmetic, refactor stacks. NOT for language-specific idioms (use go/rs/py/ts/sh/sql) or terse Docker/systemd rules (ops keeps those hot).
when_to_use: "writing or reviewing code in any language, naming, boring code, abstraction discipline, over-engineering, line width, file layout; writing tests, debugging test failures, testcontainers, smoke and e2e tests, test hangs; Python uv Dockerfile, .dockerignore, deploy a service, Ansible docker-service role, Makefile for uv, CI make targets; logging format, Prometheus metrics, SLO burn-rate alerts, error-handling hierarchy; distribute a Python tool, PEP 723 script, uvx; strict typing config, ban Any, basedpyright ruff eslint golangci-lint, un-circumventable types; race detector, sanitizers, fuzzing, Miri, goleak, property testing; money as float, currency, decimal vs integer, rounding, lamports, checked overflow; refactor stack, unreviewable branch, mutation-proven test, dead-code oracle, diffstat split"
---

# Software — runbook router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.

| If you need | Read |
|---|---|
| language-agnostic code baseline: naming, style, layout, design, boring-code, grug rules | `code.md` |
| Python+uv two-layer Dockerfile, m4 monorepo Dockerfiles, .dockerignore | `docker.md` |
| Makefile pattern for Python+uv (prepare/build/test/right/image/clean) | `ci.md` |
| test naming, test failure diagnosis, testcontainers, smoke/e2e boundaries, hangs | `testing.md` |
| Ansible docker-service role, per-deployable subdir layout | `deploy.md` |
| logging format, monitoring, SLO/burn-rate alerting, error handling | `observe.md` |
| distributing Python tools: PEP 723 single-file, uvx, package layout | `uvx-tools.md` |
| un-circumventable strict lint/type config — which linters to run + strict flags (py basedpyright+ruff, ts eslint, go golangci-lint) | `strict-typing.md` |
| runtime/dynamic checkers as test-CI targets: race detector, sanitizers (ASan/TSan/MSan/LSan), fuzzing, Miri, memory/leak, property testing (go, rust, py) | `dynamic-analysis.md` |
| exact arithmetic for money/token amounts: integer vs fixed-point vs arbitrary precision, deriving the overflow bound, round-once-at-the-edge, checked add | `money.md` |
| re-shipping an unreviewable branch as a reviewable stack: tests before the refactor, mutation-proven vs tautological tests, deletion oracles, byte-neutral and AST-proven moves, dead-parameter proofs, the freeze run, diffstat split | `refactor-stack.md` |

NEVER duplicate these runbooks into ops or language skills — link here instead.
