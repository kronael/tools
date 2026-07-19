# CTO Eval Checklist

Engineering-quality evaluation of a project. Assess fitness for adoption, production readiness, and long-term maintenance burden.

**Dimensions:** architecture · code quality · test coverage · operational readiness · scalability · dependency health · maintainability · team fit

## 1. Build & Toolchain Hygiene

```sh
make build && make test && make lint
go vet ./...          # Go static analysis
```

**Signal:** A project that can't pass its own lint/test gates has already lost to technical debt.

## 2. Test Coverage

```sh
# Go
go test -coverprofile=tmp/cov.out ./... && go tool cover -func=tmp/cov.out | tail -5
# Python
pytest --cov=. --cov-report=term-missing
# JS/TS
npx jest --coverage
```

- < 30%: high risk — behavior undocumented via tests
- 30–60%: acceptable for early-stage; flag missing critical paths
- > 60% on critical packages: good
- 0% on any package: will break silently in prod

**Check:** concurrency paths, error paths, timeout paths — happy path alone is not enough.

**Coverage measures execution, not verification.** A test with weak asserts still counts every line it touches. Spot-check assert density in 3 tests; weigh failure-path and invariant/property tests over the headline %.

## 3. Architecture Analysis

**Separation of concerns:**
- Layers cleanly separated (transport / logic / storage)?
- Can you swap the transport without touching business logic?
- Do internal packages leak implementation details upward?

**Concurrency:**
- Shared-state mutations guarded?
- Locking documented? (Undocumented locking = future deadlock)
- `go test -race ./...` / `pytest-asyncio` — passes?

**Error handling:**
- Silent failures? (`_ = err` without a comment)
- Errors wrapped with context or swallowed?
- Panics recovered? What do callers see?

**Lifecycle:**
- Clean shutdown? (SIGTERM → drain → exit, not `os.Exit(0)` mid-request)
- Resource cleanup? (goroutine leaks, fd leaks, unclosed connections)

## 4. Operational Readiness

| Dimension | Check |
|-----------|-------|
| Observability | Structured logs? Metrics endpoint? Trace IDs? |
| Metrics shape | RED per service (rate/errors/duration — Wilkie), USE per resource (utilization/saturation/errors — Gregg) |
| Alerts | Symptom/SLO-based with a runbook each — not one alert per cause (Ewaschuk, Google SRE) |
| Health check | `/health` reflects real readiness? |
| Config | 12-factor compliant? Flags/env/file? |
| Deploy artifact | Single binary / container image / pip package? |
| Graceful shutdown | Drains in-flight on SIGTERM? |
| Restart safety | Restartable without losing critical state? |
| Secrets | Env vars / vault — not baked into binary? |

**Flag:** `log.Println` without structure, hardcoded timeouts, config in binary.

**Litmus:** can an on-call answer "is it healthy, and why not?" without SSHing into the box? If diagnosis requires a shell, observability failed.

## 5. Scalability & State

- Where does state live? (In-memory = single-instance only)
- What's the bottleneck? Degrades gracefully under load?
- Back-pressure mechanism present?
- Global mutable singletons blocking horizontal scale?
- What is the measured limit? One load-tested number (max rps / connections / dataset size) beats a scalable-architecture diagram. If nobody can name the limit, nobody has found it — flag.

## 6. Dependency Audit

```sh
grep -E "^\trequire|^require" go.mod | grep -v "^//"
```

For each direct dep: actively maintained? (< 1yr), governance or solo? replaceable in a weekend?

Supply chain: lockfile committed and CI-enforced? Advisories clean (`cargo audit` / `npm audit` / `pip-audit`)? For critical deps, check OpenSSF Scorecard (maintained, fuzzed, pinned workflows) — their risk is inherited risk.

**Rule of thumb:** Each dep is a future security patch, API break, or abandonment. Fewer is better.

## 7. Code Quality Signals

```sh
gocyclo -over 15 .    # complexity (Go)
deadcode ./...         # dead code (Go)
gofmt -l . | wc -l    # formatting discipline — should be 0
```

Read 3 random non-trivial functions: understood in 30 seconds? error paths handled? new team member could own in a week?

## 8. Maintenance Burden Forecast

| Factor | Low | High |
|--------|-----|------|
| Direct deps | < 5 | > 20 |
| LOC | < 2000 | > 20000 |
| Test coverage | > 60% | < 20% |
| Maintainers | Team/org | 1 person |
| Protocol | Open standard | Proprietary |
| Docs | README + arch doc | None |
| CI | Automated | Manual |
| Upstream churn | Stable, boring deps | Fast-moving frameworks |

Burden ≈ expected lifetime × change rate of everything beneath it — "software engineering is programming integrated over time" (Titus Winters). A 10-year system on fast-churning deps pays the upgrade tax annually.

## 9. Team Fit

- Language/framework matches team skills?
- Onboarding practical from code style alone?
- Abstractions at the right level, or does wrapping add complexity?
- Need to fork to get what you need?

## Verdict Template

```
## CTO Eval: <project> v<version>

**Verdict:** ADOPT / ADOPT WITH CONDITIONS / TRIAL / DO NOT ADOPT

**Fit for:** [dev tooling / internal service / production user-facing / data pipeline]

### Strengths
- ...

### Risks & Gaps
- ...

### Conditions for Production Adoption
1. ...

### Maintenance Forecast
[1-2 sentences on long-term ownership cost]
```

| Verdict | Meaning |
|---------|---------|
| **ADOPT** | Production-ready for stated scope; adopt as-is |
| **ADOPT WITH CONDITIONS** | Good bones; specific gaps to close before production |
| **TRIAL** | Good for non-critical / dev use; not ready for prod path |
| **DO NOT ADOPT** | Fundamental architectural issues or unacceptable risk |
