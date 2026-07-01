---
name: software
description: Router for deep engineering runbooks — Docker images, CI Makefiles, deploys, observability, Python tool distribution. NOT for terse Docker/systemd/config rules (ops keeps those hot) or app code (use language skills).
when_to_use: "Python uv Dockerfile, m4 monorepo image, .dockerignore, Ansible docker-service role, deploy a service, Makefile for uv, CI make targets, make demo target, logging format, Prometheus metrics, SLO burn-rate alerts, error-handling hierarchy, distribute a Python tool, PEP 723 script, uvx"
---

# Software — runbook router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.

| If you need | Read |
|---|---|
| Python+uv two-layer Dockerfile, m4 monorepo Dockerfiles, .dockerignore | `docker.md` |
| Makefile pattern for Python+uv (prepare/build/test/right/image/clean), `make demo` targets | `ci.md` |
| Ansible docker-service role, per-deployable subdir layout | `deploy.md` |
| logging format, monitoring, SLO/burn-rate alerting, error handling | `observe.md` |
| distributing Python tools: PEP 723 single-file, uvx, package layout | `uvx-tools.md` |

NEVER duplicate these runbooks into ops or language skills — link here instead.
