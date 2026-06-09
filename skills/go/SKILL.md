---
name: go
description: Go development. NOT for non-Go code (use rs, py, ts, tsx, or sh).
when_to_use: editing .go files or writing Go code
---

# Go

## Concurrency

- Single goroutine owns all state: direct access, no locks, deterministic order
- Fails fast on conflicts instead of retrying with mutexes

## Parsing and Types

- Parse at the boundary, pass typed values inward — never re-parse the same wire
  format in two places
- Platform-specific wire types (API response structs, DB row types) live in the
  package that owns that boundary; never leak to callers
- Shared domain types go in `core/` (or equivalent); adapters convert at entry
- DTOs (request/response bodies, MCP params) are defined adjacent to their
  handler — not in a global `types/` package unless ≥3 packages share them
- One canonical parse path per format: if cron parsing lives in `timed/`, ipc
  must import that function, not reimplement it

## Naming
- Write the full word for compound names: `rateLimiter` not `rl`, `group` not `g`, `upstream` not `up`
- Short vars OK: `n`, `k`, `i`, `j`, `x`, `y`, `z`, `m`, `g`, `f`, `h`, `buf`, `err`, `ctx`; doubled (`kk`, `vv`) for nested/plural; short descriptive (`data`, `msg`) fine too
- NEVER visually ambiguous singles: `o`, `O`, `I`, `l` (look like `0` or `1`)

## Testing
- Test files: `*_test.go` next to code
- Skip slow tests: `if testing.Short() { t.Skip() }`
