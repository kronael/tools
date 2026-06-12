---
name: software
description: Router for deep engineering runbooks extracted from ops. Read the ONE data file the dispatch table matches; everything under software/ except this file is cold. NOT for terse Docker/systemd/config rules (ops keeps those hot) or app code (use language skills).
when_to_use: Python uv Dockerfile, two-layer image, m4 monorepo Dockerfile, .dockerignore, Ansible docker-service role, deploy a service, per-deployable subdir layout, Makefile for uv (prepare/test/right/image), CI make targets, logging format, Prometheus metrics, SLO burn-rate alerts, heartbeat, error-handling hierarchy, exponential backoff, distribute a Python tool, PEP 723 single-file script, uvx --from git
---

# Software — runbook router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.

| If you need | Read |
|---|---|
| Python+uv two-layer Dockerfile, m4 monorepo Dockerfiles, .dockerignore | `docker.md` |
| Makefile pattern for Python+uv (prepare/build/test/right/image/clean) | `ci.md` |
| Ansible docker-service role, per-deployable subdir layout | `deploy.md` |
| logging format, monitoring, SLO/burn-rate alerting, error handling | `observe.md` |
| distributing Python tools: PEP 723 single-file, uvx, package layout | `uvx-tools.md` |

NEVER duplicate these runbooks into ops or language skills — link here instead.
