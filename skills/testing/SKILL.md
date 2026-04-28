---
name: testing
description: Testing patterns. Use when writing tests, running tests, debugging or triaging
  test failures, reading test output, testcontainers.
---

# Testing

## Diagnosing Failures

- NEVER re-run tests to analyze output; capture once:
  `make test 2>&1 | tee ./tmp/test.log && tail -8 ./tmp/test.log && grep "FAILED\|failed" ./tmp/test.log`
- For complex failures, delegate to a subagent with the log file path

## Naming

- **unit**: fast, no external deps (<5s)
- **e2e**: self-contained (testcontainers)
- **smoke**: against running API (pytest + playwright)

## Testcontainers (Rust)

- Centralize setup in tests/common/mod.rs
- TestApp struct owns ContainerAsync (prefix _ keeps alive, RAII cleanup)
- Dynamic port: `.get_host_port_ipv4()`, run migrations after start
- `--test-threads=1` if using global state

## Pitfalls

- Remove real API/database tests from unit test suite
- conftest.py (Python) or common/mod.rs (Rust) for shared fixtures
- Return `Result<()>` for clean error propagation
