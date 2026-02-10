---
name: go
description: Go development patterns. Use when working on .go files, go.mod, or Go projects.
---

# Go

## Testing
- Test files: `*_test.go` next to code
- Skip slow tests: `if testing.Short() { t.Skip() }`
