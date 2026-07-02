---
name: ops
description: DevOps and deployment. Dockerfile, systemd, GitHub Actions, monitoring, Ansible. NOT for app code (use language skill).
when_to_use: "Dockerfile, docker-compose, systemd services, GitHub Actions CI, Ansible playbooks, monitoring setup, PID files"
---

# Ops

## Docker

- ALWAYS pin image versions (NEVER :latest)
- ALWAYS multi-stage if intermediate layers >100MB
- ENTRYPOINT for production, CMD for development
- Layer order: base+system deps -> lang deps (Cargo.toml, requirements.txt) -> fetch deps -> copy source -> build
- Cross-compilation: volume mount source, NEVER copy
- ALWAYS set memory limits (2GB typical) and build timeout (30m)

## Container hardening

- ALWAYS USER non-root in final stage
- ALWAYS HEALTHCHECK when the container exposes a liveness endpoint
- Use `--init` (or dumb-init) for app images that fork children — proper PID 1 signal/reaping semantics

## Configuration

- Three-level: base TOML -> env.toml (`${PREFIX:-/srv}/key/env.toml`) -> env vars
- Secrets in /srv/key/env.toml (NOT committed), chmod 600 for keypairs

## Storage

- Config: `${PREFIX:-/srv}/key/`, Runtime: `${PREFIX:-/srv}/run/`, Data: `${PREFIX:-/srv}/data/<project>/`

## Anti-Patterns

- Use EWMA (not sliding windows) for window calculations
- NEVER manually .close() async context managers

## CI/CD

- ALWAYS explicit make targets: `make prepare`, `make image`, `make test`
- NEVER run release builds locally, mix debug/release artifacts

## Runbooks (cold — read on demand)

Deep patterns live in `../software/`; read the one file you need:

| Need | File |
|---|---|
| Python+uv two-layer Dockerfile, m4 monorepo Dockerfiles | `../software/docker.md` |
| Makefile pattern for Python+uv (prepare/test/right/image) | `../software/ci.md` |
| Ansible docker-service role, per-deployable subdir layout | `../software/deploy.md` |
| Logging format, monitoring, SLO/burn-rate alerts, error handling | `../software/observe.md` |
| Distributing Python tools: PEP 723 single-file, uvx, packages | `../software/uvx-tools.md` |
