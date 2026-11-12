# Dynamic analysis — runtime checkers as test/CI targets

`strict-typing.md` catches what is wrong in the *source*; these catch what only
appears when the code *runs* — data races, undefined behavior, memory errors,
leaks, deadlocks, crashes on odd inputs. Runtime tools only see executed paths,
so their value scales with coverage. Wiring (make targets, CI) is at the bottom.

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

- **mutmut** (>=3.8) — mutation testing: copies the source to `mutants/`, changes
  one operator or constant at a time and runs the tests; a surviving mutant is a
  missing test or dead code. ALWAYS run it on a change through `mut_changed.py`
  beside this file, and before calling a refactor's suite enough:

  ```sh
  python3 ~/.claude/skills/software/mut_changed.py <base> [<component dir>]
  ```

  It mutates only the changed `*.py` under mutmut's `source_paths`, tests
  excluded, by writing `only_mutate` into `[tool.mutmut]` for the run. It runs
  `uv run --no-sync --with 'mutmut>=3.8'` under a `MemoryMax` scope
  (`--memory`, default 4G), `--max-children 4` and `nice -n 19`, then restores
  `pyproject.toml` byte for byte and moves `mutants/` to a temp directory it
  names. It lists the survivors on changed lines only — added lines and the
  neighbours of a deletion — each with `mutmut show`. Exit 0: none; 1:
  survivors listed; 2: failed check. `scope empty` exits 0 and mutated nothing.
  - NEVER run bare `mutmut run` on a package — ALWAYS the script: mutmut 3
    takes no scope on its command line, and generating every mutant of a large
    `source_paths` ran past a 6 GB cgroup.
  - ALWAYS settle each survivor as a test that fails with the mutant's diff
    applied, or as `equivalent` with the reason no input tells it apart, named
    in the closing report. NEVER a bare `# pragma: no mutate`.
  - A project needs no make target and no uv group; the project venv and
    `uv.lock` stay untouched. ALWAYS keep `[tool.mutmut]` only for what the
    script cannot guess: `pytest_add_cli_args` (unit tests only),
    `also_copy` (files the tests import outside `source_paths`), and
    `source_paths` where mutmut's guess — `lib`, `src`, the directory's own
    name — is wrong. Without it the run takes pytest's own test selection;
    mutmut adds `-x`.

Targets: default `test` runs `-X dev -W error`; add `test-prop`, `test-mem`.

---

## Wiring

- NEVER put these in pre-commit — nightly toolchains, clang, and time budgets
  don't belong in a commit gate.
- One `make` target each; aggregate under `make test-all` (what CI runs).
- Time-box fuzz / property / mutation runs in CI; run them longer on a nightly
  schedule.
