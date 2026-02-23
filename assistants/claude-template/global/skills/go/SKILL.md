---
name: go
description: Go development. .go files, go.mod, *_test.go, testing.Short, goroutines, go test.
---

# Go

## Concurrency

- Single goroutine owns all state: direct access, no locks, deterministic order
- Fails fast on conflicts instead of retrying with mutexes

## Testing
- Test files: `*_test.go` next to code
- Skip slow tests: `if testing.Short() { t.Skip() }`
