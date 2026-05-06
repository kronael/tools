---
name: service
description: REST APIs and web services. /health, /ready, versioned paths (/v1/), caching, validation before persistence, microservices. NOT for CLI tools (use cli) or batch jobs (use data).
when_to_use: building a REST API, microservice, /health endpoint, versioned API paths
---

# Service/API

- Liveness: /health (process alive), Readiness: /ready (deps ready)
- Versioned paths: /v1/, /v2/ (not query params)
- Fail fast on missing data (404), use last available data when current unavailable
