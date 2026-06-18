---
name: cto-eval
description: "Technical adoption evaluation. NOT for ROI or business strategy (use ceo-eval)."
when_to_use: "CTO evaluation, technical due diligence, should we adopt this, architecture review, production readiness, tech debt assessment, dependency adoption, engineering risk"
---

# CTO Eval

Engineering-quality evaluation of a project. Goal: assess fitness for adoption, production readiness, and long-term maintenance burden.

## Dimensions

Architecture · code quality · test coverage · operational readiness · scalability · dependency health · maintainability · team fit

## Checklist

### 1. Build & Toolchain Hygiene

```sh
make build          # Does it build?
make test           # Do tests pass?
make lint           # Are lint rules enforced?
go vet ./...        # (Go) Static analysis clean?
```

**Signal:** A project that can't pass its own lint/test gates is signaling technical debt has already won.

### 2. Test Coverage Assessment

```sh
# Go
go test -cover ./...
go test -coverprofile=tmp/cov.out ./... && go tool cover -func=tmp/cov.out | tail -5

# Python
pytest --cov=. --cov-report=term-missing

# JS/TS
npx jest --coverage
```

**Interpret:**
- < 30% coverage: high risk; behavior is undocumented via tests
- 30–60%: acceptable for early-stage; flag missing critical paths
- > 60% on critical packages: good
- 0% on a package: that package will break silently in prod

**Specifically check:** Are the critical concurrency paths tested? Error/timeout paths? The happy path alone is not enough.

### 3. Architecture Analysis

Read key source files and answer:

**Separation of concerns:**
- Are layers cleanly separated (transport / logic / storage)?
- Can you swap the transport (HTTP → gRPC) without touching business logic?
- Do internal packages leak their implementation details upward?

**Concurrency model:**
- Are shared-state mutations guarded?
- Is the locking documented? (Undocumented locking = future deadlock)
- Race detector: `go test -race ./...` or `pytest-asyncio` — does it pass?

**Error handling:**
- Silent failures anywhere? (`_ = err` without a comment)
- Are errors wrapped with context or swallowed?
- Do panics have recovery? What do callers see?

**Lifecycle:**
- Clean shutdown? (SIGTERM → drain → exit, not `os.Exit(0)` mid-request)
- Resource cleanup? (goroutine leaks, file descriptor leaks, unclosed connections)

### 4. Operational Readiness

| Dimension | Check |
|-----------|-------|
| Observability | Structured logs? Metrics endpoint? Trace IDs? |
| Health check | `/health` or equivalent? Does it reflect real readiness? |
| Config | Flags/env/file? 12-factor compliant? |
| Deploy artifact | Single binary / container image / pip package? |
| Graceful shutdown | Drains in-flight requests on SIGTERM? |
| Restart safety | Can restart without losing critical state? |
| Secrets | Config vs code? Env vars or vault? |

**Flag:** `log.Println` without structure (grep for it), hardcoded timeouts, config baked into binary.

### 5. Scalability & State

- Where does state live? (In-memory = single-instance; DB/Redis = horizontally scalable)
- What's the bottleneck? (CPU? Memory? subprocess spawn latency?)
- Does the system degrade gracefully under load or fail hard?
- Is there a back-pressure mechanism?
- Any global mutable singletons that prevent horizontal scaling?

### 6. Dependency Audit

```sh
# Count direct deps
cat go.mod | grep -E "^\trequire|^require" | grep -v "^//"
```

**Evaluate each direct dep:**
- Is it actively maintained? (last commit < 1 year)
- Is it a well-known project with governance, or a one-person library?
- Could we replace it in a weekend if it went abandoned?
- Indirect deps: does the transitive tree look reasonable for the problem scope?

**Rule of thumb:** Each dep is a future security patch, API break, or abandonment event. Fewer is better.

### 7. Code Quality Signals

```sh
# Complexity (Go)
gocyclo -over 15 .

# Dead code (Go)
deadcode ./...

# Formatting discipline
gofmt -l . | wc -l    # should be 0
```

**Read 3 random non-trivial functions** and ask:
- Can you understand what it does in 30 seconds?
- Are there comments explaining WHY (not WHAT)?
- Are error paths handled or ignored?
- Could a new team member own this in a week?

### 8. Maintenance Burden Forecast

| Factor | Low Burden | High Burden |
|--------|-----------|-------------|
| Dep count | < 5 direct | > 20 direct |
| LOC | < 2000 | > 20000 |
| Test coverage | > 60% | < 20% |
| Maintainers | Team/org | 1 person |
| Protocol lock-in | Open standard | Proprietary undocumented |
| Docs | README + arch doc | None |
| CI | Automated | Manual |

### 9. Team Fit

- Does the language/framework match your team's skills?
- Is the code style consistent enough that onboarding is practical?
- Are the abstractions at the right level for your use case, or does heavy wrapping add complexity?
- Does the project's contribution model fit your needs? (do you need to fork?)

## Verdict Template

```
## CTO Eval: <project> v<version>

**Verdict:** [ADOPT / ADOPT WITH CONDITIONS / TRIAL / DO NOT ADOPT]

**Fit for:** [dev tooling / internal service / production user-facing / data pipeline / ...]

### Strengths
- ...

### Risks & Gaps
- ...

### Conditions for Production Adoption
1. Add X before deploying to production
2. ...

### Maintenance Forecast
[1–2 sentences on long-term ownership cost]
```

## Decision Rubric

| Verdict | Meaning |
|---------|---------|
| **ADOPT** | Production-ready for stated scope; adopt as-is |
| **ADOPT WITH CONDITIONS** | Good bones; N specific gaps to close before production |
| **TRIAL** | Good for non-critical / dev use; not ready for prod path |
| **DO NOT ADOPT** | Fundamental architectural issues or unacceptable risk |
