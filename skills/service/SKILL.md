---
name: service
description: REST APIs and web services. NOT for CLI tools (use cli) or batch jobs (use data).
when_to_use: building a REST API, microservice, adding a /health endpoint
---

# Service/API

- Liveness: /health (process alive), Readiness: /ready (deps ready)
- Versioned paths: /v1/, /v2/ (not query params)
- Fail fast on missing data (404), use last available data when current unavailable

## Logging

- ALWAYS attach a request/correlation ID to every log line; propagate via X-Request-Id. NEVER log without it.

## API design

- ALWAYS accept Idempotency-Key on POST/PATCH that creates or mutates state; dedupe by key for 24h+. NEVER assume client retries safely.
- ALWAYS return errors as {code, message, details?} with a stable machine code. NEVER vary error shape across endpoints.
