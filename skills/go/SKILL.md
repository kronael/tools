---
name: go
description: Go development. NOT for non-Go code (use rs, py, ts, tsx, or sh).
when_to_use: editing .go files or writing Go code
---

# Go

Requires the `software` skill's `code.md` for shared naming, style, and design
rules. Below are Go-specific additions.

## Build output

- ALWAYS build into `dist/` in the tree root: `go build -o dist/<name>`. Bare
  `go build` drops the binary in the cwd — never leave it there or in the repo
  root where it gets committed by accident.
- `dist/` is GoReleaser's own default output dir, so hand-builds and released
  artifacts land in the same place — one `dist/` line in `.gitignore` covers
  both, no per-binary ignores. (`bin/` is the older GOPATH-era convention; use
  `dist/` here for the GoReleaser alignment.)

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

## Variadic parameters

- Reserve `...T` for sugar: formatting APIs (`Printf`-style), functional
  options (`...Option`), and convenience wrappers where an inline arg list
  reads naturally at the call site.
- For a normal collection of data, take an explicit `[]T` instead — a slice
  states "this is the set" and forbids the meaningless zero-arg call that
  variadic silently allows (`Middleware()` compiling to "no known paths" is a
  footgun).
- Smell: `New(paths ...string)` where the paths are config/data — use
  `[]string`.

## Wrapper types vs functions

- A struct whose only purpose is to hold one injected dependency so methods can
  hang off it (`type Client struct{ dep }` + `func (c *Client) Do()`) is optional
  ceremony. If the type carries no invariant of its own, prefer plain package
  functions taking the dependency as a parameter (`Do(ctx, dep, …)`) — one fewer
  type, dependency explicit. Go forbids methods on types from other packages, so
  wrapping a foreign type just to get method syntax is exactly when free functions
  win.

## Naming
- Write the full word for compound names: `rateLimiter` not `rl`, `group` not `g`, `upstream` not `up`
- Short vars OK: `n`, `k`, `i`, `j`, `x`, `y`, `z`, `m`, `g`, `f`, `h`, `buf`, `err`, `ctx`; doubled (`kk`, `vv`) for nested/plural; short descriptive (`data`, `msg`) fine too
- NEVER visually ambiguous singles: `o`, `O`, `I`, `l` (look like `0` or `1`)
- **Package names**: single word, lowercase, no underscores — Go convention
  (`httputil`, `strutil`, `filepath`, NOT `http_utils`, `string_utils`). Linters
  flag underscored package names. The `*_utils.*` project rule applies to FILES
  inside a package (e.g., `string_utils.go`), not to package names themselves.

## Error Suppression

Intentionally dropped errors must be explicit in code, not hidden in linter config.
Config exclusions are for structural cases only (generated files, test path patterns).

**Non-defer**: use `_ =` with a short reason on the line above.
```go
// body fully read into buffer above
_ = resp.Body.Close()
```

**Defer**: `defer func() { _ = x.Close() }()` is uglier than the problem.
Use `//nolint:errcheck` with the reason on the line above — no inline text:
```go
// body drained; close error unactionable
defer resp.Body.Close() //nolint:errcheck

// commit already succeeded; rollback is best-effort
defer tx.Rollback(ctx) //nolint:errcheck
```

**Inline `_ =` in HTTP handlers** — `w.Write` failure means client disconnected;
response is already committed. One short inline comment is fine:
```go
_, _ = w.Write([]byte(`{"status":"ok"}`)) // client disconnect; nothing to do
```

NEVER write a suppression without a reason. The comment must answer WHY.

NEVER use a linter config exclusion for a specific symbol or call site — a reader
has to look up the config. Config exclusions are for structural cases only:
generated files, test path patterns, project-wide style choices (no-comment policy).

## Comments

- Prefer a comment on its own line ABOVE the code it describes; avoid trailing
  inline comments. Inline comments crowd the line, get truncated on wrap, and
  drift as the code changes. Even a short field annotation goes above:
  ```go
  // pre-formatted "200 OK"; built once at store time
  statusText string
  ```
  not `statusText string // pre-formatted "200 OK"`. Narrow exceptions: the
  suppression-reason and handler one-liners noted above.

## Testing
- Test files: `*_test.go` next to code
- Skip slow tests: `if testing.Short() { t.Skip() }`
