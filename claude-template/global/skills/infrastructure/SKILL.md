---
name: infrastructure
description: Infrastructure and ops patterns. Use when working on deployment, Ansible, monitoring, logging, process management.
---

# Infrastructure/Ops

## Configuration Management

- Environment file: `${PREFIX:-/srv}/key/env.toml` overrides TOML
- Environment variables override files
- Validation on load (fail fast at startup)
- Three-level hierarchy: base TOML → env.toml → env vars

**Validation patterns**:
```
validator crate (Rust): URL format, range checking, non-empty strings
Fail fast at startup, not at runtime
```

## Secrets Management

**Pattern 1: TOML overrides**:
```
Base config: cfg/config.toml (committed)
Secrets: /srv/key/env.toml (NOT committed)
Override precedence: env.toml > env vars > config.toml
```

**Pattern 2: Environment variables**:
```bash
export POSTGRES_URL=postgresql://...
export RPC_URL=https://...
```

**Pattern 3: File paths**:
```
Keypairs: ~/.config/service/id.json (chmod 600)
Certificates: /etc/pki/tls/certs/ (owned by service user)
```

## Logging

**Structured format**:
```
Format: Mon DD HH:MM:SS.fff [LEVEL] message key=value
Example: Nov 05 15:30:45.234 INFO Liquidating stake key=account value=balance
```

**Log levels** (production vs debug):
- error: Failures only
- warn: Recoverable issues
- info: Normal operations (RECOMMENDED for production)
- debug: Internal algorithm details

**RUST_LOG filtering**:
```bash
RUST_LOG=info                    # Production (30-50 lines/min)
RUST_LOG=debug                   # Development (verbose)
RUST_LOG=error                   # Quiet (errors/warnings only)
RUST_LOG=module::path=debug,info # Selective (one module debug, rest info)
```

**Rotation**:
- Log rotation via logrotate (not in app)
- CRITICAL prefix for monitoring alerts
- Structured logs to ./log/service.log

## Monitoring

- Heartbeat files in ./tmp/<service>.heartbeat
- Health check endpoints: /.well-known/live
- Metrics: Prometheus format on /metrics
- APM integration via OpenTelemetry (APM_URL env)

### Prometheus Metrics Cardinality

**NEVER as labels:** unbounded values (unique per request/user), client-controlled input, unvalidated user data

**Safe labels:** bounded enums, validated against fixed set, server-controlled values

**Validate before recording**:
```
valid = ['day', 'week', 'month']
val = input in valid ? input : 'unknown'
counter.inc({ period: val })
```

**High cardinality → logs** (use trace context)

## Error Handling

**Error hierarchy pattern**:
```
ApplicationError   # Business logic
InfrastructureError # External services (gRPC, RPC, network)
DomainError        # Model validation
```

**Retry strategy**:
- Exponential backoff for transient errors
- Base delay: 100ms, Max retries: 5
- Backoff sequence: 100ms, 200ms, 400ms, 800ms, 1600ms
- ONLY retry transient errors (connection, timeout, unavailable)
- NEVER retry validation or business logic errors

**Error classification**:
- Transient: connection, timeout, rate limit → RETRY
- Persistent: validation, auth, not found → ALERT
- Alert on persistent errors (>10 failures)
- Graceful degradation (cache fallback, read-only mode)

## Process Management

- Write PID to file on startup: `${PREFIX:-/srv}/run/<service>.pid`
- Graceful shutdown: Handle SIGTERM/SIGINT (30s timeout)
- Exit codes: 0=success, 1=config error, 2=runtime error
- NEVER killall, ALWAYS kill by PID

**PID file pattern**:
```bash
echo $! > ${PREFIX}/data/<project>/service.pid
# Later:
kill $(cat ${PREFIX}/data/<project>/service.pid)
```

## Data Storage

- Configuration: `${PREFIX:-/srv}/key/`
- Runtime state: `${PREFIX:-/srv}/run/`
- Data: `${PREFIX:-/srv}/data/<project_name>/`
- Logs: ./log/ (local) or syslog (production)

**Temporary data**:
- Development: ./tmp/ (project root)
- Production: /srv/tmp/ or /tmp/project/
- NEVER use global /tmp/ for state

## Concurrency Patterns

**Single goroutine (Go)**:
- One main goroutine processes state
- Direct state access (no locks)
- No copy overhead
- Deterministic order
- Fails fast on conflicts

**Async/await (Rust)**:
- tokio runtime for async I/O
- Semaphore for concurrency control
- tokio::spawn for parallel tasks
- Arc<Self> for spawned tasks needing self
- Manual Clone impl when needed

## Transaction Patterns

**Two-stage transaction**:
1. Prepare phase: Build transaction details (Ready or Unprepared)
2. Finalize phase: Add blockhash + signatures
3. Separate strategy logic from signing logic

## Anti-Patterns

**Window-based calculations**:
```
WRONG: window = [last_100_values]; ewma = calculate(window)
RIGHT: ewma_new = alpha * value + (1 - alpha) * ewma_old
```

**Async connection cleanup**:
```
NEVER manually call .close() on async context managers
Trust context managers for cleanup
Protocol errors indicate connection state corruption
```

## Deployment

- Git-ops pattern: Configuration in git repo
- Automated deployment via CI/CD (GitHub Actions, GitLab CI)
- Blue-green or rolling updates (zero downtime)
- Rollback via git revert + redeploy

**Infrastructure as code**:
- Version control all config
- Changes via pull requests
- Automated deployment (synced from git)
- Version history and rollback capability

## Deployment Checklist

1. **Configuration**: TOML schema, env overrides, secrets isolation, PREFIX expansion
2. **Logging**: Structured format, multiple levels, RUST_LOG filtering, rotation policy
3. **Monitoring**: Prometheus metrics, health check endpoint, error counters, alerting rules
4. **Storage**: ${PREFIX}/data/<project>/ directory, state persistence, cleanup/retention, backups
5. **Security**: Minimal permissions, secrets not in logs, TLS for network services, audit logging
6. **Operations**: Graceful shutdown, PID file management, restart policies, resource limits
