---
name: service
description: API service patterns. Use when building REST APIs, web backends, microservices.
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
