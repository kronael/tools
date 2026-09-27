# Testing

## Diagnosing Failures

- NEVER re-run tests to analyze output; capture once:
  `make test 2>&1 | tee test.log && tail -8 test.log && grep "FAILED\|failed" test.log`
- For complex failures, delegate to a subagent with the log file path.

## Naming

- **unit**: fast, no external deps (<5s)
- **e2e**: self-contained, including testcontainers
- **smoke**: against a running API, commonly pytest + Playwright
- `make test`: unit (<5s); `make test-all`: unit + integration (what CI runs);
  `make smoke`: production data
- Unit tests live next to the code (`*_test.go`, `test_*.py`); integration
  tests in a dedicated `tests/` directory

## Scope and layout

- Prefer the real thing: integration/e2e wherever the seam is cheap (container
  DB, real handler, tmpdir I/O). Mock ONLY what you cannot run — paid or
  third-party APIs, clocks, randomness, cloud SDKs. NEVER mock your own modules
  to keep a unit test tidy; that tests the mocks.
- Unit tests next to the code (`*_test.go`, `test_*.py`); integration tests in a
  dedicated top-level `tests/`.
- Test features, not fixes: a runtime failure means fix the code — add a test
  only where the feature itself lacks coverage.
- Test config objects match the target type exactly; omit unknown properties
  rather than widening the type.
- An environment failure (missing binary, no docker, no credential) is a
  reported blocker. NEVER skip, `xfail`, or stub the dependency to get green.
## Descriptions

- A test module's doc-comment and a test's intro name BOTH the SCENARIO and
  the OUTCOME it asserts — condition and concrete result, never one alone.
  Bad: a bare list of return codes with no scenario (`200`, `413`). Bad: a
  scenario with no stated outcome (`when processing`). Good: `an existing
  withdrawer with data -> 200 with the report`, `a report mid-regeneration ->
  200, still serves the last coherent snapshot`, `a never-generated report ->
  413 not-ready`.

## Testcontainers

- Centralize setup in `tests/common/mod.rs` or the language equivalent.
- Test app/harness structs own the container handle; RAII cleanup is part of
  the fixture contract.
- Use dynamic ports, then run migrations after start.
- Use `--test-threads=1` only when global state makes parallelism unsafe.

## Gates and Hangs

- NEVER let a gate run unbounded work - ALWAYS wrap it in a deadline
  (`timeout N cargo bench`).
- NEVER write a busy-wait without a deadline or a recovery pump. A flaky hang
  is worse than a flaky fail because silence reads as progress.
- Harness code is reference usage - hold it to the same idiom bar as examples.
  A harness that misuses the API teaches the bug.

## Pitfalls

- ALWAYS prefer integration/e2e over mocks; unit tests mock external systems
  only. Remove real API/database tests from unit test suites.
- Use shared fixture modules (`conftest.py`, `common/mod.rs`) for common setup.
- Return `Result<()>` or the language equivalent for clean error propagation.
- A test that fails from import/typo/fixture errors proves nothing - confirm
  the failure names the missing behavior before writing code.
- NEVER reshape production typing around tests/fakes - keep production types
  on production contracts.
- ALWAYS relax type checks for test paths when strict test typing is
  impractical; NEVER weaken production types.
- Test config objects match the target type exactly — omit unknown properties
  for type safety.
- Test features, not fixes: a runtime failure → fix the code; add a test only
  when the feature lacks coverage.
