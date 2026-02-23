---
name: infrastructure
description: Infrastructure and ops patterns. Use when working on deployment, Ansible, monitoring, logging, process management.
---

# Infrastructure

For: /srv/-based Linux services, Ansible deployment, Prometheus monitoring

## Paths
- Config: `${PREFIX:-/srv}/key/env.toml`
- Runtime state: `${PREFIX:-/srv}/run/`
- PID files: `${PREFIX:-/srv}/run/<service>.pid`

## Process
- Exit codes: 0=success, 1=config error, 2=runtime error

## Monitoring
- Heartbeat files: ./tmp/<service>.heartbeat

## Ansible
- Roles for services, host_vars/ for host-specific

## Docker Patterns

### Dockerfile Structure (m4 template)
Multi-stage build with dependency caching:

```dockerfile
# Stage 1: Dependencies (cached unless lockfiles change)
FROM base:version AS builder
COPY package.json bun.lock* Pipfile* pyproject.toml* uv.lock* /app/
RUN make prepare  # Install deps only

# Stage 2: Build (invalidated on source changes)
COPY . /app/
RUN make build

# Stage 3: Runtime (minimal image)
FROM base:version
COPY --from=builder /app/dist /app/
WORKDIR /app
```

Key rules:
- NEVER copy source in deps layer (breaks cache on every change)
- Copy lockfiles first, install deps, then copy source
- `make prepare` for deps, `make build` for compilation
- Working directory: `/srv/app/core/<name>` or `/app`

### Ansible docker-service Integration
The docker-service role expects containers to follow these conventions:

**Entrypoint (automatic detection)**:
```bash
# Ansible runs this command - container must support it:
[[ -x ./main ]] && exec ./main $args $config || exec python -m main $args $config
```

Container MUST have either:
- Executable `./main` script in WORKDIR
- Python module `main` runnable via `python -m main`

**Config path**: `/cfg/<server>/<service_name>.toml`
- Ansible passes config path as last argument
- Container should accept: `./main [args] /cfg/hel1v5/my_service.toml`

**Volume mounts** (automatic):
```
/srv/spool/<name>  → persistent queue/data
/srv/run/<name>    → runtime state, PID files
```

**Environment variables** (injected by ansible):
```
SERVICE_NAME     - Service name (underscores)
SERVICE_IMAGE    - Docker image (dashes)
SERVICE_FLAVOR   - Optional flavor suffix
SERVICE_ARGS     - Extra arguments
SERVICE_SERVER   - Server hostname
SERVICE_CONFIG   - Full config path
```

**Network**: `--network=host` (no port mapping needed)
- EXPOSE statements for documentation only
- Services bind directly to host network

### Naming Conventions
- Service names: underscores (`funding_report`)
- Image names: dashes (`funding-report`)
- Ansible converts: `image.replace('-', '_')` for systemd unit names

### host_vars Service Definition
```yaml
service:
  - image: my-service           # Docker image (dashes)
    params: -v /srv/log:/srv/log:ro
    # No timer fields = long-running service

  - image: my-timer             # Docker image
    minute: "*/5"               # Cron-style → timer mode
    timeout: 600                # Seconds before kill

  - image: my-calendar          # Docker image
    oncalendar: "daily"         # Systemd calendar → timer mode
```

### Dockerfile for Ansible Deployment
Minimal requirements for ansible docker-service:

```dockerfile
FROM base:version

WORKDIR /app
COPY . /app/

# MUST have executable main script
COPY main /app/main
RUN chmod +x /app/main

# OR for Python: ensure main module exists
# python -m main must work

# EXPOSE for documentation (network=host ignores these)
EXPOSE 8080
```

### Common Pitfalls
- Missing `./main` or `python -m main` entry point
- Hardcoding config paths (must accept as argument)
- Using port mapping (ansible uses --network=host)
- Using dashes in service names (breaks systemd)
- Copying source before deps (breaks layer cache)
