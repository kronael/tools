---
name: rust
description: Rust development patterns. Use when working on .rs files, Cargo.toml, or Rust projects. Covers imports, concurrency, state management, testcontainers.
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

- Never use accessor methods; access fields directly with interior mutability
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

## Development Workflow

- `cargo check` fastest for error checking (no codegen)
- Debug builds ~3x faster than release (6s vs 20s)
- Better error messages and stack traces in debug
