---
name: go
description: Go development. .go files, go.mod, *_test.go, testing.Short, goroutines, go test.
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
- No abbreviated variable names unless the function is very small (≤5 lines)
  or the abbreviation is completely standard (e.g. `buf`, `err`, `ctx`, `ok`)
- Write the full word: `rateLimiter` not `rl`, `group` not `g`, `upstream` not `up`
- Single-letter names only for loop indices (`i`, `j`) and trivial type parameters

## Testing
- Test files: `*_test.go` next to code
- Skip slow tests: `if testing.Short() { t.Skip() }`
