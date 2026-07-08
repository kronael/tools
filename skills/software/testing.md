# Testing

## Diagnosing Failures

- NEVER re-run tests to analyze output; capture once:
  `make test 2>&1 | tee ./tmp/test.log && tail -8 ./tmp/test.log && grep "FAILED\|failed" ./tmp/test.log`
- For complex failures, delegate to a subagent with the log file path.

## Naming

- **unit**: fast, no external deps (<5s)
- **e2e**: self-contained, including testcontainers
- **smoke**: against a running API, commonly pytest + Playwright

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

- Remove real API/database tests from unit test suites.
- Use shared fixture modules (`conftest.py`, `common/mod.rs`) for common setup.
- Return `Result<()>` or the language equivalent for clean error propagation.
- A test that fails from import/typo/fixture errors proves nothing - confirm
  the failure names the missing behavior before writing code.
- NEVER reshape production typing around tests/fakes - keep production types
  on production contracts.
- ALWAYS relax type checks for test paths when strict test typing is
  impractical; NEVER weaken production types.
