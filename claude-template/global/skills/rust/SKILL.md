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

## Design Patterns

- Prefer direct field access over getters/setters for simple structs
- Use interior mutability (Cell/RefCell/Mutex) when shared refs need mutation
- FxDashMap fastest for concurrent access (but no locks best)

## State Management

- Use explicit enum states, not implicit flags
- Document state transitions with edge cases
- Document lock acquisition order to prevent deadlocks

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

## Non-Workspace Repos

ALWAYS scan Cargo.toml independently, NEVER assume workspace.members:
- Repos with multiple disconnected Rust projects need per-project scanning
- Each has own Cargo.toml, no workspace umbrella

## Development Workflow

- `cargo check` fastest for error checking (no codegen)
- Debug builds ~3x faster than release (6s vs 20s)
- Better error messages and stack traces in debug

## Async

- tokio runtime for async I/O, NEVER mix blocking in async context
- Use `tokio::spawn` for concurrent tasks, `JoinSet` for managing groups
- `spawn_blocking` for CPU-heavy work inside async context
- ALWAYS use `select!` with cancellation tokens for graceful shutdown
