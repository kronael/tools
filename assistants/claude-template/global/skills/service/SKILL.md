---
name: service
description: REST APIs and web services. /health, /ready, versioned paths (/v1/), caching, validation before persistence, microservices.
---

# Service/API

## Health Checks
- Liveness: /health (process alive)
- Readiness: /ready (dependencies ready)

## API Design
- Versioned paths: /v1/, /v2/ (not query params)
- Validation BEFORE persistence

## Caching
- NEVER hit external APIs per request
- Continue from last state (don't re-download existing data)

## Error Recovery
- Fail fast on missing data (return 404)
- Use last available data when current unavailable
