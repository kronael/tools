---
name: infrastructure
description: Infrastructure and ops patterns. Use when working on deployment, Ansible, monitoring, logging, process management.
---

# Infrastructure/Ops

## Configuration Management

- Environment file: `${PREFIX:-/srv}/key/env.toml` overrides TOML
- Environment variables override files
- Validation on load (fail fast at startup)

## Ansible Patterns

- Roles for common services (docker, nginx, grafana, rsyslog)
- Host-specific variables in host_vars/
- Secrets in ansible-vault encrypted files
- Idempotent tasks (safe to re-run)
- Tags for selective deployment

## Process Management

- Write PID to file on startup: `${PREFIX:-/srv}/run/<service>.pid`
- Graceful shutdown: Handle SIGTERM/SIGINT (30s timeout)
- Exit codes: 0=success, 1=config error, 2=runtime error

## Logging

- Structured logs to ./log/service.log
- Log rotation via logrotate (not in app)
- CRITICAL prefix for monitoring alerts

## Monitoring

- Heartbeat files in ./tmp/<service>.heartbeat
- Health check endpoints: /.well-known/live
- Metrics: Prometheus format on /metrics
- APM integration via OpenTelemetry (APM_URL env)

### Prometheus Metrics Cardinality

**NEVER as labels:** unbounded values (unique per request/user), client-controlled input, unvalidated user data

**Safe labels:** bounded enums, validated against fixed set, server-controlled values

**Validate before recording:**
```
valid = ['day', 'week', 'month']
val = input in valid ? input : 'unknown'
counter.inc({ period: val })
```

**High cardinality → logs** (use trace context)

## Data Storage

- Configuration: `${PREFIX:-/srv}/key/`
- Runtime state: `${PREFIX:-/srv}/run/`
- Logs: ./log/ (local) or syslog (production)

## Deployment

- Git-ops pattern: Configuration in git repo
- Automated deployment via CI/CD (GitHub Actions, GitLab CI)
- Blue-green or rolling updates (zero downtime)
- Rollback via git revert + redeploy

## Error Handling

- Classify errors: Application/Infrastructure/Domain
- Retry transient errors (connection, timeout)
- Alert on persistent errors (>10 failures)
- Graceful degradation (cache fallback, read-only mode)
