---
name: rust
description: Rust development. .rs files, Cargo.toml, tokio, DashMap, tracing, cargo clippy, core_affinity, testcontainers, enum states.
---

# Rust

**TL;DR**: FxDashMap for concurrent maps. Enum states not flags. Document lock
order. Debug builds default. testcontainers for integration tests. tracing for
logging. Thread panic handler with exit(0).

## Code Style Example

```rust
// CORRECT
use tracing::info;
use tracing::debug;

// WRONG
use tracing::{info, debug};
```

## Naming

- Function params: NEVER use shortcuts — `value` not `v`, `count` not `c`
- Loop variables: single-letter (`i`, `n`, `s`) is fine
- Mathematical context: `n`, `k` for counts, `m` for size — when obvious
- Macro meta-variables: shortcuts OK — `$a`, `$b`, `$val`, `$k`, `$v`, `$ty`
  - Use meaningful names for semantic roles: `$state`, `$key`, `$rest`

## Design Patterns

- Never use accessor methods; access fields directly with interior mutability
- FxDashMap fastest for concurrent access (but no locks best)
- Semaphore for concurrency control (limit parallel tasks)
- Arc<Self> when spawned tasks need self reference

## State Management

- Use explicit enum states, not implicit flags
- Document state transitions with edge cases
- Document lock acquisition order to prevent deadlocks
- DB status/type columns as smallint, `#[repr(i16)]` enum in code

## Testing

- Unit tests: `#[cfg(test)]` module in same file
- Integration tests: `tests/` dir
- `--test-threads=1` if global state via DashMap/RwLock
- Centralize setup in `tests/common/mod.rs`
- Testcontainers: dynamic port via `.get_host_port_ipv4()`

## Threading

- Pin OS threads to specific CPU cores via core_affinity
- Prevents thread migration and context switches
- Document exact core assignments in CLAUDE.md
- ALWAYS set panic handler to exit(0) on any thread panic:
  `std::panic::set_hook(Box::new(|_| std::process::exit(0)));`

## Production Binary Patterns

- `install_panic_handler()` in every binary — prints info to stderr, exits 1
- `main()` wraps `run()` in retry loop with 5s sleep
- All hot-path code returns Result, never panics
- `on_error_continue!` / `on_none_continue!` for loops
- `defer!` for RAII cleanup guards

```rust
fn main() {
    install_panic_handler();
    tracing_subscriber::fmt::init();
    let config = load_config(); // panics ok at startup
    loop {
        match run(&config) {
            Ok(()) => break,
            Err(e) => {
                tracing::error!("crashed: {e}, restarting in 5s");
                std::thread::sleep(Duration::from_secs(5));
            }
        }
    }
}
```

## Unwrap Safety Rules

- NEVER unwrap() on hot path without `// SAFETY:` comment
- Startup/init: expect("descriptive msg") is ok (fail-fast)
- Hot path: return Result or use match/if-let, never unwrap
- Mutex: use `.lock().unwrap_or_else(|e| e.into_inner())` to recover poison
- Every unwrap() must have `// SAFETY: <reason>` on the line above

## Copy/Clone Rules

- NEVER derive Copy unless trivially copyable (i32, u64, bool, enum variants)
- If it has heap data, String, Vec, or non-trivial state: no Copy, pass by ref
- Clone only when you actually need an owned duplicate
- Newtypes over primitives (Price, Qty) may derive Copy

## Async Spawn Rules

- NEVER use anonymous `spawn(async { ... })` blocks
- Name the coroutine as a function, spawn as a oneliner:

```rust
// WRONG
tokio::spawn(async move { let res = client.fetch().await; process(res); });

// RIGHT
async fn fetch_and_process(client: Client) { ... }
tokio::spawn(fetch_and_process(client));
```

- Named coros are readable, greppable, show in backtraces
- Applies to monoio::spawn, spawn_blocking, etc.

## Crate Organization

- Crate-per-concern: types/, common/, clients/, engine/ — NOT one mega-crate
- Flat modules inside: lib.rs lists all `pub mod` flat, no nested `mod.rs`
- Re-export key types: `use crate::Error` not `use crate::error::Error`
- `_utils.rs` suffix: stateless helpers, pure functions, no state

## Non-Workspace Repos

ALWAYS scan Cargo.toml independently, NEVER assume workspace.members:
- Repos with multiple disconnected Rust projects need per-project scanning

## Development Workflow

- `cargo check` fastest for error checking (no codegen)
- Debug builds ~3x faster than release (6s vs 20s)
- Better error messages and stack traces in debug
