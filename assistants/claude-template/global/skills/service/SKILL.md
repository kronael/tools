---
name: service
description: REST APIs and web services. /health, /ready, versioned paths (/v1/), caching, validation before persistence, microservices.
---

# Service/API

- Liveness: /health (process alive), Readiness: /ready (deps ready)
- Versioned paths: /v1/, /v2/ (not query params)
- Fail fast on missing data (404), use last available data when current unavailable
