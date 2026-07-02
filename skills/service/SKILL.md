---
name: service
description: REST APIs and web services. NOT for CLI tools (use cli) or batch jobs (use data).
when_to_use: "building a REST API, microservice, adding a /health endpoint"
---

# Service/API

- Liveness: /health (process alive), Readiness: /ready (deps ready)
- Versioned paths: /v1/, /v2/ (not query params)
- Fail fast on missing data (404), use last available data when current unavailable

## Logging

- ALWAYS scope logs by a request ID propagated from the inbound request

## API design

- ALWAYS return errors with stable shape: machine code + human message
- ALWAYS accept idempotency key on POST/PATCH endpoints clients may retry
