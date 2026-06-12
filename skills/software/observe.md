# Observability

## Logging

- Format: `Mon DD HH:MM:SS.fff [LEVEL] message key=value`
- CRITICAL prefix for monitoring alerts
- Log rotation via logrotate (not in app)
- RUST_LOG: `info` (prod), `debug` (dev), `module::path=debug,info` (selective)

## Monitoring

- Heartbeat: ./tmp/<service>.heartbeat
- Health: /.well-known/live, Metrics: /metrics (Prometheus)
- Prometheus labels: NEVER unbounded values, ONLY bounded enums. High cardinality -> logs.

## Alerting

- ALWAYS SLO + burn-rate alerts over absolute error counts when the project has stated SLOs
- ALWAYS attach `runbook_url` annotation pointing at the playbook on Prometheus alerts

## Error Handling

- Hierarchy: ApplicationError, InfrastructureError, DomainError
- Exponential backoff: 100ms...1600ms, ONLY retry transient errors
- Alert on >10 persistent failures
