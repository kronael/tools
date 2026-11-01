# Testing

## Diagnosing Failures

- Capture once (WISDOM § Shell), then read the file:
  `mkdir -p tmp && make test 2>&1 | tee ./tmp/test.log && tail -8 ./tmp/test.log && grep "FAILED\|failed" ./tmp/test.log`
- For complex failures, delegate to a subagent with the log file path.

## Naming

- **unit**: fast, no external deps (<5s)
- **e2e**: self-contained, including testcontainers
- **smoke**: against a running API, commonly pytest + Playwright
- **play**: the Play kind below, self-contained like e2e (`make play`)
- The `make test` / `test-all` / `smoke` tiers: `code.md` § House conventions.
- Unit tests live next to the code (`*_test.go`, `test_*.py`); integration
  tests in a dedicated `tests/` directory

## Kinds

For self-contained tests: three kinds, each proving one thing; a test that fits none is not written.

- Component (unit): one unit with plain values or typed props in, output
  checked; loading, empty and error states are inputs. NEVER `fetch` or a
  fixture server.
- API: every module with plain values; a function that reads or writes the
  database runs on the testcontainers fixture, NEVER on a patch of an own
  query function; HTTP tests through the app on the same fixture prove the
  contract — what the API answers.
- Play: user journeys end to end through the built frontend, the real API and
  testcontainers Postgres, one per journey the FLOWS doc names, data created
  through the API calls the UI makes. A UI state is a component test, a
  refusal an API test. Least code: one migrated template database and
  `CREATE DATABASE ... TEMPLATE` per test; one API process per worker on its
  own port and database; `storageState` once per worker; `page.clock`. A slow
  or lost answer is the real answer held or aborted with a route, NEVER a
  rewritten body.
- Fake ONLY what you cannot run — a third party at the API's outbound client,
  the clock, randomness. NEVER an own module (that tests the fake) and NEVER
  the own API contract: a fake answers differently from the real API, and
  every fix adds fake code.
- Assertions update themselves — `toMatchAriaSnapshot`
  (`--update-snapshots=changed`), `toMatchInlineSnapshot` (`-u`),
  `inline-snapshot` (`--inline-snapshot=fix`) — on deterministic output (fixed
  clock and ids). ALWAYS read a snapshot change in the diff like code.

## Scope and layout

- Prefer the real thing: integration/e2e wherever the seam is cheap (container
  DB, real handler, tmpdir I/O); what is faked: § Kinds.
- Test features, not fixes: a runtime failure means fix the code — add a test
  only where the feature itself lacks coverage.
- Test config objects match the target type exactly; omit unknown properties
  rather than widening the type.
- An environment failure (missing binary, no docker, no credential) is a
  reported blocker. NEVER skip, `xfail`, or stub the dependency to get green.
- NEVER a test whose subject is a library, the language or a helper under
  `tests/` — a validator the test module declares, a dataclass being frozen, a
  database feature no production query runs. Every assertion reaches
  production code; a `tests/` helper only drives it.
- A fixture file is its own record: NEVER a provenance file, header or
  manifest beside it. The test that reads it fails when the data changes, and
  the commit that added it says where it came from.

## Which tests to run

- ALWAYS choose the focused tests before the edit — the test beside each file
  you change and the FEATURES.md row's test for the behaviour you change
  (`readme` → `topology.md`). Run those on every iteration and the full
  `make test` tier once before the commit — NEVER the whole suite per edit.
- NEVER report a green focused run as done — ALWAYS name what it did not run:
  the full tier, integration, build. A focused run is evidence for the next
  iteration, not for the commit.

## Proving the suite ran

- NEVER report a suite green without counting what ran against what exists:
  the fixtures the Make target names against the files on disk. A test the
  target omits never runs and looks exactly like a passing one, and a list
  cut with a fixed `grep -A N` window truncates silently. State both counts.
- A model-backed feature is unverified until real weights ran end to end:
  mocked adapters pass while the service cannot start and a threshold sits on
  a scale nobody measured. ALWAYS keep a labelled fixture set, assert the
  accuracy and the observed score range, and derive every threshold from
  that range.

## Descriptions

- A test module's doc-comment and a test's intro name BOTH the SCENARIO and
  the OUTCOME it asserts — condition and concrete result, never one alone.
  Bad: a bare list of return codes with no scenario (`200`, `413`). Bad: a
  scenario with no stated outcome (`when processing`). Good: `an existing
  withdrawer with data -> 200 with the report`, `a report mid-regeneration ->
  200, still serves the last coherent snapshot`, `a never-generated report ->
  413 not-ready`.

## Testcontainers

- ALWAYS centralize container setup in `tests/container_utils.rs` or the language equivalent.
- Test app/harness structs own the container handle; RAII cleanup is part of
  the fixture contract.
- Use dynamic ports, then run migrations after start.
- Use `--test-threads=1` only when global state makes parallelism unsafe.

## Gates and Hangs

- NEVER let a gate run unbounded work - ALWAYS wrap it in a deadline
  (`timeout N cargo bench`).
- ALWAYS print each check's duration in a check target — a slow check is then
  seen and fixed, not waited on.
- NEVER write a busy-wait without a deadline or a recovery pump. A flaky hang
  is worse than a flaky fail because silence reads as progress.
- Harness code is reference usage - hold it to the same idiom bar as examples.
  A harness that misuses the API teaches the bug.

## What an assertion proves

- NEVER derive the expected value from the code under test or its helpers. A
  mirror assertion (`expect(build(x)).toBe(build(x))`) passes whatever `build`
  does — ALWAYS hand-write the literal or a checked fixture.
- Asserting that a file CONTAINS a line proves only that the source is the
  source. ALWAYS run the script, config or template against a controlled input
  and assert its output, side effect or exit code. Prose for humans earns no
  test.

## Pitfalls

- Remove real API/database tests from unit test suites.
- ALWAYS share fixture setup in the language's fixture module (`conftest.py`); container setup follows § Testcontainers.
- Return `Result<()>` or the language equivalent for clean error propagation.
- A test that fails from import/typo/fixture errors proves nothing - confirm
  the failure names the missing behavior before writing code.
- NEVER reshape production typing around tests/fakes - keep production types
  on production contracts.
- Tests run with relaxed type checks and mostly without annotations; NEVER
  spend effort typing tests to strict; NEVER weaken production types.
