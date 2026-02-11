---
name: testing
description: Testing patterns. Use when writing tests, setting up test infrastructure, testcontainers.
---

# Testing

## Philosophy

- Test with real APIs immediately, not after 100 lines
- Mental models about external APIs are always wrong

## Testcontainers (Rust)

```rust
// Centralize setup in tests/common/mod.rs
async fn setup_test_db() -> Result<(String, ContainerAsync<Postgres>)> {
    let node = Postgres::default()
        .with_tag("15-alpine")
        .start()
        .await?;
    let conn = format!(
        "postgres://postgres:postgres@127.0.0.1:{}/postgres",
        node.get_host_port_ipv4(5432).await?
    );
    setup_database(&conn).await?;
    Ok((conn, node))
}

// Test app owns containers for automatic cleanup
pub struct TestApp {
    pub client: Client,
    _node: ContainerAsync<Postgres>,  // prefix _ keeps alive
}
```

## Naming

- **unit**: fast, no external deps (<5s)
- **e2e**: self-contained (testcontainers)
- **smoke**: against running API (pytest + playwright)

## Best Practices

- Remove real API/database tests from unit tests
- Use synthetic/fixture data for unit tests
- `--test-threads=1` if using global state
- Dynamic port mapping: `.get_host_port_ipv4()`
- RAII pattern: container cleanup via ownership
- Run migrations after container start
- Return `Result<()>` for clean error propagation
- Use `#[tokio::test]` for async Rust tests
- conftest.py (Python) or common/mod.rs (Rust) for shared fixtures
