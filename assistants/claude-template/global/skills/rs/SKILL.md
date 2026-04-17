---
name: rs
description: Rust development. .rs files, Cargo.toml, clap, eyre, tracing, tokio, DashMap, cargo clippy, core_affinity, testcontainers, enum states.
---

# Rust

## Imports
- NEVER arbitrary `as` aliases to rename external types
- NEVER `use super::`, NEVER local `use` inside function bodies
  (exception: tests/main where scoping demands it)
- ALWAYS `use crate::` for absolute paths
- Use full path or canonical name; renaming erases origin

## Naming
- ALWAYS verb-based function names unless trivially a constructor
  - `collect_tx_summaries()` not `tx_summaries()`; nouns ok for `new()`, `from_str()`
- Function params: NEVER shortcuts — `value` not `v`, `count` not `c`
- Loop variables and math context: single-letter fine (`i`, `n`, `k`)
- Macro meta-variables: shortcuts OK (`$a`, `$val`, `$ty`); meaningful names for semantic roles (`$state`, `$key`)

## Code Style
- NEVER combinator chains for calculations — use `if`/`let`/early return
- `.map()`, `.filter()` ok for data pipelines, NEVER for conditional logic

## Design Patterns
- Never accessor methods; access fields directly with interior mutability
- FxDashMap for concurrent access (but no locks best)
- Semaphore for concurrency control
- Arc<Self> when spawned tasks need self reference

## State Management
- Document lock acquisition order to prevent deadlocks
- DB status/type columns as smallint, `#[repr(i16)]` enum in code

## Testing
- `--test-threads=1` if global state via DashMap/RwLock
- Centralize setup in `tests/common/mod.rs`
- Testcontainers: dynamic port via `.get_host_port_ipv4()`

## Threading
- Pin OS threads to specific CPU cores via core_affinity
- Document exact core assignments in CLAUDE.md
- ALWAYS set panic handler: `std::panic::set_hook(Box::new(|_| std::process::exit(0)));`

## CLI with Clap
- ALWAYS derive API, never builder
- ALWAYS short flags for common options
- Subcommands as enum variants with `#[command]`

## Error Handling
- `eyre` + `color-eyre` for new projects; keep `anyhow` if already present
- Libraries: `thiserror` for typed errors
- ALWAYS `color_eyre::install()?` before tracing init
- `.wrap_err("context")` not `.context()` (avoids trait ambiguity)

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
- NEVER unwrap() on hot path without `// SAFETY:` comment above
- Startup/init: `expect("msg")` ok (fail-fast)
- Mutex: `.lock().unwrap_or_else(|e| e.into_inner())` to recover poison

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
- Crate-per-concern: types/, common/, clients/, engine/
- Flat modules: lib.rs lists all `pub mod` flat, no nested `mod.rs`
- Re-export key types at crate root

## Non-Workspace Repos
- ALWAYS scan Cargo.toml independently, NEVER assume workspace.members

## Development Workflow
- `cargo check` fastest for error checking (no codegen)
