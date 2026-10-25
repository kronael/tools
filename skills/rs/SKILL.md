---
name: rs
description: Rust development. NOT for non-Rust code (use go, py, ts, tsx, or sh).
when_to_use: editing .rs files or writing Rust code; rename a Rust symbol, rust-analyzer ssr
---

# Rust

ALWAYS Read `../software/code.md` before the first edit — it owns naming,
comments, design and the boring-code rules. Also requires
`../software/dynamic-analysis.md` (test-target checkers: Miri, `-Zsanitizer`, loom,
cargo-fuzz, cargo-mutants, nextest). Below are Rust-specific additions.

## Imports
- NEVER arbitrary `as` aliases to rename external types
- NEVER `use super::`, NEVER local `use` inside function bodies
  (exception: tests/main where scoping demands it)
- ALWAYS `use crate::` for absolute paths
- **Common items bare, rare items prefixed — the same way project-wide.**
  An item a crate uses often (`Arc`, its main error type, common wire types)
  gets a top-of-file `use` and reads bare. A rare std or external item may
  stay a full inline path (`std::time::Duration`). A rare item of this crate
  goes through its imported module: `use crate::store;` then `store::open(..)`.
  NEVER `crate::` inside a body (a macro body needs `$crate::` paths; that is
  the exception), and NEVER a generic prefix (`types::`, `args::`,
  `accounts::`) that hides which module is meant; keep a prefix only where it
  carries meaning (`postgres::connect` beside `redis::connect`).
- Keep files small enough to hold in one mental context; small files + uniform
  imports make any file quick to reason about. Split a file that outgrows that.

## Naming
`software/code.md` § Naming owns names. Rust additions:
- Constructors (`new()`, `from_str()`) are nouns; every other API-visible function is a verb phrase.
- Macro meta-variables: shortcuts OK (`$a`, `$val`, `$ty`); meaningful names for semantic roles (`$state`, `$key`)

## Code Style
- Prefer `for x in xs {}` over `xs.for_each(|x| ...)` when the closure adds no clarity
- NEVER use `.filter().map().unwrap_or()` as a disguised `if/else` — write `if`/`let` directly
- `.filter()` filters collections; it is NOT a conditional branch
- `.map()`, `.filter()` ok on iterators/collections, NEVER on `Option` to express control flow

## Design Patterns
- NEVER accessor methods — access fields directly with interior mutability
- FxDashMap for concurrent access (but no locks best)
- Semaphore for concurrency control
- Arc<Self> when spawned tasks need self reference

## State Management
- Document lock acquisition order to prevent deadlocks
- DB status/type columns as smallint, `#[repr(i16)]` enum in code

## Testing
- Unit tests live alongside source as `src/<module>_test.rs`, declared at the
  TOP of the source file with the imports, where a reader meets it before the
  code it covers — NOT inline `#[cfg(test)] mod tests { ... }`,
  NOT a `<module>/tests.rs` subdirectory, NOT in `tests/`
- **`#[path]` is REQUIRED on every module that is not the crate root or a
  `mod.rs`.** A bare `#[cfg(test)] mod foo_test;` inside `src/a/foo.rs` resolves
  to `src/a/foo/foo_test.rs`, not the sibling — you get a single-file directory
  per module, or a compile error. Write it as:
  ```rust
  #[cfg(test)]
  #[path = "foo_test.rs"]
  mod foo_test;
  ```
  `#[path]` is relative to the DIRECTORY the declaring file sits in, so this
  lands on `src/a/foo_test.rs`. The test module stays a CHILD of `foo`, which is
  what keeps `foo`'s private items (private fns, private struct fields, consts)
  reachable from the test. A sibling module cannot see them — that is why the
  file must be wired this way and not declared from the parent.
- Integration tests (cross-crate, external API surface) go in `tests/`
- Inside `src/<module>_test.rs` use `crate::` paths, not `super::*`
- `--test-threads=1` if global state via DashMap/RwLock
- ALWAYS follow `../software/testing.md` § Testcontainers for shared container setup.
- Testcontainers: dynamic port via `.get_host_port_ipv4()`

## Threading
- Pin OS threads to specific CPU cores via core_affinity
- Document exact core assignments in CLAUDE.md
- Generic services: set a panic handler `std::panic::set_hook(Box::new(|_| std::process::exit(0)));`. NEVER where the project bans `process::exit` — graceful-shutdown-sensitive code (e.g. trading engines that must cancel orders first) must signal the shutdown path instead.

## CLI with Clap
- ALWAYS derive API, never builder
- ALWAYS short flags for common options
- Subcommands as enum variants with `#[command]`

## Error Handling
- `eyre` + `color-eyre` for new projects; keep `anyhow` if already present
- Libraries: `thiserror` for typed errors
- ALWAYS `color_eyre::install()?` before tracing init
- `.wrap_err("context")` not `.context()` (avoids trait ambiguity)
- NEVER `let _ = call_that_returns_result()`. Silent drops have caused real correctness bugs. Use `?`, `if let Err(e) = ...`, or fail loud.

## Tracing
- ALWAYS `tracing` over `log`
- ALWAYS `EnvFilter` from RUST_LOG for subscriber init
- NEVER `#[instrument]` on hot-path functions (overhead)

## Production Binary Patterns
- `main()` wraps `run()` in retry loop with 5s sleep
- All hot-path code returns Result, never panics

```rust
fn main() -> eyre::Result<()> {
    color_eyre::install()?;
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .init();
    let cli = Cli::parse();
    let config = load_config(&cli.config);
    loop {
        match run(&config) {
            Ok(()) => break Ok(()),
            Err(e) => {
                tracing::error!("crashed: {e:#}, restarting in 5s");
                std::thread::sleep(Duration::from_secs(5));
            }
        }
    }
}
```

## Unwrap Safety
- In a library crate NEVER `.unwrap()`, `.expect()`, `panic!`, `unreachable!`
  or an index that can panic: return `Result` and let `main` or a test decide
  to crash (`software/code.md` § Design). Enforce it at the crate root with
  `#![deny(clippy::unwrap_used, clippy::expect_used, clippy::panic,
  clippy::indexing_slicing)]`, allowed again only in `main.rs` and test
  modules — NEVER per call site.
- In a binary NEVER bare `.unwrap()` in non-test code; use `.expect("msg")`;
  the one exception is a `//` reason on the line directly above (§ Lints)
- In a binary `.expect()` is for truly unrecoverable config at startup, with
  the REASON in its message (§ Unsafe owns `// SAFETY:`); a fn that returns
  `Result` under a retry, backoff or supervisor `?`s the error instead — a
  socket bind or a PG connect fails TRANSIENTLY, and a re-entered startup
  (`run_main` on demote/restart) is no startup.
- Mutex: `.lock().unwrap_or_else(|e| e.into_inner())` to recover poison

## Unsafe
- ALWAYS `cargo +nightly miri test` on modules with `unsafe` blocks; NEVER ship `unsafe` without a `// SAFETY:` invariant comment
- **`// SAFETY:` is RESERVED for justifying `unsafe`** — it documents the
  invariants that make an unsafe block sound, and is the audit signal a reader
  greps when reviewing `unsafe`. NEVER put `// SAFETY:` on SAFE code to justify a
  `.expect()` / `panic!` / fail-fast / `.unwrap()`. That dilutes the convention
  and is wrong. For a deliberate panic, the reason goes in the `.expect("…")`
  message — `// SAFETY:` means "this unsafe is sound", nothing else.

## serde_json Value
- NEVER `serde_json::from_value::<T>(value.clone())` — `&Value` implements `Deserializer`, use
  `T::deserialize(value)` (ref, no clone):
  ```rust
  let Ok(value) = MyType::deserialize(details) else { continue };
  ```
- For sparse reads (1–2 fields), prefer direct access over full deserialization:
  ```rust
  let Some(value) = details.get("count").and_then(|v| v.as_u64()) else { continue };
  ```

## Copy/Clone
- NEVER derive Copy unless trivially copyable (i32, u64, bool, enum)
- Newtypes over primitives (Price, Qty) may derive Copy
- Clone only when you actually need an owned duplicate

## Async Spawn
- NEVER anonymous `spawn(async { ... })` — name the coroutine as a function:

```rust
// WRONG: tokio::spawn(async move { ... });
// RIGHT:
async fn fetch_and_process(client: Client) { ... }
tokio::spawn(fetch_and_process(client));
```

## Crate Organization
- ALWAYS one crate per concern, named for its concrete job.
- Flat modules: lib.rs lists all `pub mod` flat, no nested `mod.rs`
- ALWAYS re-export the crate's own key types at its root — NEVER re-export another crate's items
  (`pub use other_crate::X`, a `pub use solana_pubkey::Pubkey`): a caller depends on the crate that
  defines `X` and imports it from there, so one item has one path and the dependency is visible.
- When the project draws a domain/adapter boundary, keep `Serialize`/`Deserialize` on adapter-layer DTOs, not on core domain entities

## Non-Workspace Repos
- ALWAYS scan Cargo.toml independently, NEVER assume workspace.members

## Lints
- ast-grep rules in `skills/rs/lints/` (`make lints`): `rs-no-unwrap`,
  `rs-no-from-value-clone`, `rs-no-anon-spawn`, `rs-bool-fn-prefix`
  (`software/code.md` § Naming). clippy owns the rest — NEVER duplicate a
  clippy lint here.
- `rs-no-unwrap` exempts test files (`*_test.rs`, `tests/`) and any unwrap
  carrying a `//` reason on the line directly above — one of the in-body
  comments `software/code.md` § Comments allows. NEVER `// SAFETY:` for it;
  that marker is reserved for `unsafe`.

## Refactor tools
- ALWAYS rename with the `serena` skill, then its check for code behind a
  disabled cargo feature — NEVER grep-and-edit.
- NEVER `rust-analyzer ssr` — it rewrites files in place with no preview.
  ALWAYS a scoped `ast-grep scan` rule instead (`astgrep` skill).

## Development Workflow
- `cargo check` fastest for error checking (no codegen)
- Debug builds/tests too slow? The nightly cranelift backend (opt-in per
  invocation, or pinned for the project) and the crates that must stay on
  LLVM are in `cranelift.md`.
