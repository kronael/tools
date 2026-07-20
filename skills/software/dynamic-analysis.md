# Dynamic analysis — runtime checkers as test/CI targets

`strict-typing.md` catches what is wrong in the *source*; these catch what only
appears when the code *runs* — data races, undefined behavior, memory errors,
leaks, deadlocks, crashes on odd inputs. All are too slow (or need
nightly/clang/time budget) for pre-commit. Wire each behind its own `make`
target and run it in `make test-all` (CI), keeping `make test` fast (<5s).
Runtime tools only see executed paths — their value scales with coverage.

---

## Go

- `go test -race ./...` — the data-race detector (ThreadSanitizer-based). ~10×
  slower, more memory; the single highest-value target — ALWAYS in CI.
- `go test -shuffle=on -count=1 ./...` — randomize test order to expose
  inter-test state leakage; `-count=1` defeats the test cache.
- `go test -fuzz=Fuzz -fuzztime=60s` — native coverage-guided fuzzing (1.18+),
  corpus in `testdata/fuzz`. Time-boxed CI target, never the unit run.
- **goleak** (`go.uber.org/goleak`) — fail a package if goroutines leak:
  `goleak.VerifyTestMain(m)` in `TestMain`.
- `go test -asan` / `-msan` — Address / Memory sanitizer; for **cgo** (C-side
  memory bugs, uninitialized reads), needs clang. Skip for pure Go — the race
  detector plus the GC cover it.
- `govulncheck ./...` — vuln scanner with reachability (flags only vulns you
  actually call). CI target.

Targets: `test-race`, `fuzz`, `vuln`.

---

## Rust

- `cargo +nightly miri test` — MIR interpreter detecting UB: out-of-bounds,
  use-after-free, invalid values, misaligned access, data races, leaks. THE
  tool for any `unsafe`; near-useless for pure-safe crates. Slow — drive it via
  `cargo nextest` for process isolation.
- Sanitizers (nightly): `RUSTFLAGS="-Zsanitizer=address" cargo +nightly test
  -Zbuild-std --target <triple>` — also `thread`, `leak`, `memory`. ASan+LeakSan
  are stabilizing for tier-1 targets. TSan catches races on *real* threads that
  Miri only sees on its interpreted path.
- `cargo careful test` — runs std with debug assertions on and poisons
  uninitialized memory; a cheap safety net without full nightly sanitizers.
- **loom** — exhaustive permutation model-checker for lock-free / atomic code;
  gate a `#[cfg(loom)]` suite.
- **cargo-fuzz** (libFuzzer): `cargo +nightly fuzz run <target>` — time-boxed CI.
- `cargo nextest run` — faster process-per-test runner, better flaky handling;
  the default workflow runner (and Miri's).
- `cargo mutants` — mutation testing: proves the tests actually catch bugs.
- **proptest** / **quickcheck** — property-based tests.
- `cargo audit` / `cargo deny` — vuln + license/ban policy in CI.

Targets: `miri`, `test-san`, `fuzz`, `mutants`.

---

## Python

- `python -X dev -W error -m pytest` — Dev Mode turns on faulthandler,
  `PYTHONMALLOC=debug` (buffer overruns / use-after-free in C allocations), and
  ResourceWarning; `-W error` makes warnings — unclosed files/sockets,
  deprecations, un-awaited coroutines — fail the test. Cheapest, biggest win;
  make it the default test invocation.
- **faulthandler** (on by default in pytest) + `--faulthandler-timeout=N` —
  dumps every thread's traceback on a hang; `faulthandler_exit_on_timeout`
  kills a deadlocked run. (Or `pytest-timeout` for a hard per-test cap.)
- **pytest-randomly** — randomize test order + reproducible seed; surfaces
  inter-test state leakage (the Go `-shuffle` analog).
- **hypothesis** — property-based testing: generates and shrinks adversarial
  inputs.
- **pytest-memray** — per-test memory profiling with leak / high-water
  assertions.
- Free-threaded builds (3.13t+): run under **ThreadSanitizer** to validate
  C-extension thread safety — heavy, CI-only; pass pytest `-s`, set a
  `TSAN_OPTIONS` log_path, and give pytest-xdist a faulthandler timeout so a
  hang doesn't stall CI.

Targets: default `test` runs `-X dev -W error`; add `test-prop`, `test-mem`.

---

## Wiring

- NEVER put these in pre-commit — nightly toolchains, clang, and time budgets
  don't belong in a commit gate.
- One `make` target each; aggregate under `make test-all` (what CI runs).
- Time-box fuzz / property / mutation runs in CI; run them longer on a nightly
  schedule.
