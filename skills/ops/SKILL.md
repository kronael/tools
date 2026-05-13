---
name: ops
description: DevOps and deployment. NOT for application code (use go, rs, py, ts, or tsx).
when_to_use: writing a Dockerfile, systemd unit, GitHub Actions workflow
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
- ALWAYS HEALTHCHECK matching liveness endpoint
- ALWAYS dumb-init (or --init) as PID 1; NEVER let app receive raw SIGTERM as PID 1

## Configuration

- Three-level: base TOML -> env.toml (`${PREFIX:-/srv}/key/env.toml`) -> env vars
- Secrets in /srv/key/env.toml (NOT committed), chmod 600 for keypairs

## Logging

- Format: `Mon DD HH:MM:SS.fff [LEVEL] message key=value`
- CRITICAL prefix for monitoring alerts
- Log rotation via logrotate (not in app)
- RUST_LOG: `info` (prod), `debug` (dev), `module::path=debug,info` (selective)

## Monitoring

- Heartbeat: ./tmp/<service>.heartbeat
- Health: /.well-known/live, Metrics: /metrics (Prometheus)
- Prometheus labels: NEVER unbounded values, ONLY bounded enums. High cardinality -> logs.

## SLO + alerting

- ALWAYS define SLO target + 30d window per service (availability, p95 latency)
- ALWAYS alert on burn-rate ratios (1h@14.4x critical, 6h@6x critical); NEVER on absolute error counts
- ALWAYS attach `runbook_url` annotation to every Prometheus alert; missing runbook = alert not ready

## Error Handling

- Hierarchy: ApplicationError, InfrastructureError, DomainError
- Exponential backoff: 100ms...1600ms, ONLY retry transient errors
- Alert on >10 persistent failures

## Storage

- Config: `${PREFIX:-/srv}/key/`, Runtime: `${PREFIX:-/srv}/run/`, Data: `${PREFIX:-/srv}/data/<project>/`

## Anti-Patterns

- Use EWMA (not sliding windows) for window calculations
- NEVER manually .close() async context managers

## Ansible docker-service Role

- Containers MUST have `./main` or `python -m main`
- Entrypoint: `[[ -x ./main ]] && exec ./main $args $cfg || exec python -m main $args $cfg`
- Service names: underscores (`funding_report`), image names: dashes (`funding-report`)
- `--network=host` (no port mapping), config: `/cfg/<server>/<service>.toml`
- Volumes: `/srv/spool/<name>` (persistent), `/srv/run/<name>` (runtime)

```yaml
service:
  - image: my-service              # Long-running
  - image: my-timer                # Cron timer
    minute: "*/5"
    timeout: 600
  - image: my-calendar             # Calendar timer
    oncalendar: "daily"
```

## CI/CD

- ALWAYS explicit make targets: `make prepare`, `make image`, `make test`
- NEVER run release builds locally, mix debug/release artifacts
