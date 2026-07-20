---
name: software
description: Router for engineering knowledge — the language-agnostic code baseline (naming, style, boring-code, design) plus deep runbooks (Docker images, CI Makefiles, deploys, observability, Python tool distribution). NOT for language-specific idioms (use go/rs/py/ts/sh/sql) or terse Docker/systemd rules (ops keeps those hot).
when_to_use: "writing or reviewing code in any language, naming a function or variable, boring code, abstraction discipline, explicit over clever, over-engineering, complected code, line width, file layout; Python uv Dockerfile, m4 monorepo image, .dockerignore, Ansible docker-service role, deploy a service, Makefile for uv, CI make targets, logging format, Prometheus metrics, SLO burn-rate alerts, error-handling hierarchy, distribute a Python tool, PEP 723 script, uvx; strict typing config, ban Any, basedpyright pyright ruff tsconfig eslint strict flags, no-explicit-any, ban type ignore, un-circumventable types, which linters to run/build, golangci-lint, go lint set, nolintlint, errcheck, staticcheck, govet; race detector, data race, sanitizer, ASan TSan MSan LSan, Miri, fuzzing, go test -race, cargo nextest, cargo careful, loom, cargo-fuzz cargo-mutants, memory checker, leak detector, goleak, hypothesis property testing, pytest-memray, python -X dev, ThreadSanitizer, valgrind alternative, dynamic analysis test targets"
---

# Software — runbook router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.

| If you need | Read |
|---|---|
| language-agnostic code baseline: naming, style, layout, design, boring-code, grug rules | `code.md` |
| Python+uv two-layer Dockerfile, m4 monorepo Dockerfiles, .dockerignore | `docker.md` |
| Makefile pattern for Python+uv (prepare/build/test/right/image/clean) | `ci.md` |
| Ansible docker-service role, per-deployable subdir layout | `deploy.md` |
| logging format, monitoring, SLO/burn-rate alerting, error handling | `observe.md` |
| distributing Python tools: PEP 723 single-file, uvx, package layout | `uvx-tools.md` |
| un-circumventable strict lint/type config — which linters to run + strict flags (py basedpyright+ruff, ts eslint, go golangci-lint) | `strict-typing.md` |
| runtime/dynamic checkers as test-CI targets: race detector, sanitizers (ASan/TSan/MSan/LSan), fuzzing, Miri, memory/leak, property testing (go, rust, py) | `dynamic-analysis.md` |

NEVER duplicate these runbooks into ops or language skills — link here instead.
