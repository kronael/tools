---
name: ops
description: DevOps and deployment. Dockerfile, Docker multi-stage, Prometheus, RUST_LOG, systemd, PID files, env.toml, GitHub Actions, monitoring, Ansible. USE for Dockerfile/systemd/Prometheus/deployment. NOT for application code (use the matching language skill).
---

# Ops

## Docker

- ALWAYS pin image versions (NEVER :latest)
- ALWAYS multi-stage if intermediate layers >100MB
- ENTRYPOINT for production, CMD for development
- Layer order: base+system deps -> lang deps (Cargo.toml, requirements.txt) -> fetch deps -> copy source -> build
- Cross-compilation: volume mount source, NEVER copy
- ALWAYS set memory limits (2GB typical) and build timeout (30m)

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
