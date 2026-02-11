---
name: ops
description: Operations patterns. Use when working on Dockerfiles, deployment, Ansible, monitoring, logging, process management, CI/CD.
---

# Ops

## Docker Build Patterns

### Base Images

- ALWAYS pin version explicitly (ubuntu:22.04, rust:1.75, python:3.12)
- NEVER use :latest or unversioned tags
- ALWAYS use multi-stage if intermediate layers >100MB
- ALWAYS use ENTRYPOINT for production, CMD for development

### Layer Caching

ALWAYS optimize for cache reuse. Order:
1. Base image + system deps
2. Language deps (Cargo.toml, requirements.txt, package.json)
3. Install/fetch dependencies
4. Copy source
5. Build

```dockerfile
# CORRECT - deps before source
COPY Cargo.toml Cargo.lock ./
RUN cargo fetch
COPY src ./src
RUN cargo build --release

# WRONG - source changes invalidate deps
COPY . .
RUN cargo build --release
```

### Cross-Compilation

ALWAYS volume mount source, NEVER copy:
```bash
docker run -v $(pwd):/src builder make -C /src build
```

Image has tools, compilation uses mounted source. Build image once,
reuse across projects.

### Resource Limits

- ALWAYS set Docker memory limits (2GB typical)
- ALWAYS set build timeout (30m default)
- NEVER let builds run unbounded

## Configuration Management

- Three-level hierarchy: base TOML → env.toml → env vars
- Environment file: `${PREFIX:-/srv}/key/env.toml` overrides TOML
- Validation on load (fail fast at startup, not at runtime)

## Secrets Management

**TOML overrides** (preferred):
```
Base config: cfg/config.toml (committed)
Secrets: /srv/key/env.toml (NOT committed)
Precedence: env.toml > env vars > config.toml
```

**File paths**: chmod 600 for keypairs, service user owns certs

## Logging

**Structured format**:
```
Format: Mon DD HH:MM:SS.fff [LEVEL] message key=value
```

- error: Failures only
- warn: Recoverable issues
- info: Normal operations (RECOMMENDED for production)
- debug: Internal algorithm details
- Log rotation via logrotate (not in app)
- CRITICAL prefix for monitoring alerts

**RUST_LOG filtering**:
```bash
RUST_LOG=info                    # Production
RUST_LOG=debug                   # Development
RUST_LOG=module::path=debug,info # Selective
```

## Monitoring

- Heartbeat files in ./tmp/<service>.heartbeat
- Health check endpoints: /.well-known/live
- Metrics: Prometheus format on /metrics

### Prometheus Cardinality

**NEVER as labels:** unbounded values, client-controlled input
**Safe labels:** bounded enums, validated against fixed set
**High cardinality → logs** (use trace context)

## Error Handling

**Error hierarchy**:
```
ApplicationError    # Business logic
InfrastructureError # External services (gRPC, RPC, network)
DomainError         # Model validation
```

**Retry strategy**:
- Exponential backoff: 100ms, 200ms, 400ms, 800ms, 1600ms
- ONLY retry transient errors (connection, timeout, unavailable)
- NEVER retry validation or business logic errors
- Alert on persistent errors (>10 failures)
- Graceful degradation (cache fallback, read-only mode)

## Process Management

- PID file on startup: `${PREFIX:-/srv}/run/<service>.pid`
- Graceful shutdown: SIGTERM/SIGINT (30s timeout)
- Exit codes: 0=success, 1=config error, 2=runtime error
- NEVER killall, ALWAYS kill by PID

## Data Storage

- Configuration: `${PREFIX:-/srv}/key/`
- Runtime state: `${PREFIX:-/srv}/run/`
- Data: `${PREFIX:-/srv}/data/<project_name>/`
- Logs: ./log/ (local) or syslog (production)
- NEVER use global /tmp/ for state

## Concurrency Patterns

**Single goroutine (Go)**: one goroutine processes all state, direct
access (no locks), deterministic order, fails fast on conflicts.

**Async/await (Rust)**: tokio runtime, Semaphore for concurrency
control, Arc<Self> for spawned tasks needing self.

## Anti-Patterns

**Window-based calculations**:
```
WRONG: window = [last_100_values]; ewma = calculate(window)
RIGHT: ewma_new = alpha * value + (1 - alpha) * ewma_old
```

**Async cleanup**: NEVER manually .close() async context managers.
Trust context managers. Protocol errors = connection state corruption.

## Deployment

- Git-ops: config in git, changes via PRs, automated sync
- Blue-green or rolling updates (zero downtime)
- Rollback via git revert + redeploy

## CI/CD

ALWAYS use explicit make targets in CI:
```yaml
- run: make prepare
- run: make image
- run: make test
```

NEVER: run release builds locally, skip clean before CI, assume
cached state, mix debug and release artifacts.

## Deployment Checklist

1. **Config**: TOML schema, env overrides, secrets isolation, PREFIX
2. **Logging**: Structured format, levels, RUST_LOG, rotation
3. **Monitoring**: Prometheus metrics, health check, alerting
4. **Storage**: ${PREFIX}/data/, state persistence, backups
5. **Security**: Minimal permissions, no secrets in logs, TLS
6. **Operations**: Graceful shutdown, PID files, resource limits
