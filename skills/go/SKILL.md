---
name: go
description: Go development. NOT for non-Go code (use rs, py, ts, tsx, or sh).
when_to_use: editing .go files or writing Go code; gopls, gopls mcp, go_diagnostics, go_symbol_references, staticcheck, go vet, govulncheck, deadcode, testing/synctest, goleak, race detector, goroutine leak, enum switch exhaustiveness, anthropic-sdk-go
---

# Go

Requires `software/code.md` (naming, style, design), `software/strict-typing.md`
(golangci-lint set), and `software/dynamic-analysis.md` (test-target checkers:
`-race`, fuzzing, sanitizers). Below are Go-specific additions.

## Toolchain — the edit loop

- ALWAYS have the gopls MCP server registered before editing Go. Install and
  registration: `software` skill, `lsp.md`. `gopls mcp` over stdio sees saved
  files only; `gopls serve -mcp.listen=localhost:8092` also sees unsaved
  buffers. Still marked experimental upstream.
- ALWAYS `gopls mcp -instructions` and load the output once per session — it is
  upstream's own read/edit workflow for models, not published at init.
- ALWAYS `go_workspace` first in a Go repo, then `go_vulncheck`.
- ALWAYS `go_file_context` right after first reading a `.go` file — it surfaces
  the same-package declarations that reading one file alone hides.
- ALWAYS `go_symbol_references` BEFORE changing any symbol's definition. Go
  interfaces are implicit, so grep under-reports implementers and a rename
  compiles green while silently dropping an interface satisfaction.
- ALWAYS `go_diagnostics` after every edit; fix to zero BEFORE running tests.
- NEVER `go test ./...` unless asked — test only the packages you changed.

## Static analysis

- ALWAYS `go vet ./...` and `staticcheck ./...` before calling work done.
- ALWAYS `govulncheck ./...` after touching `go.mod` — it reports only
  vulnerabilities in symbols actually reachable, so a hit is real work.
- ALWAYS `deadcode ./...` after a refactor that removed call sites.
- ALWAYS the `exhaustive` linter for switches on a named string/int type — the
  compiler NEVER checks switch completeness, so a new enum value fails silently
  at runtime.

## Build output

- ALWAYS `go build -o dist/<name>` — NEVER leave a binary in the package dir or
  repo root. `dist/` (not `bin/`) matches GoReleaser's default, so dev and
  release builds share one gitignored dir.

## Slices

- Stdlib `slices` for insert/delete/sort/search — NEVER add a dep for those.
- `samber/lo` for filter/map/reduce/group: `lo.Filter`/`lo.Map` read as intent
  where a manual loop doesn't. Zero deps beyond stdlib.

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
- ALWAYS `-race` on every test run.
- ALWAYS `testing/synctest` (GA in Go 1.25) for concurrency, timeout, and
  retry-backoff tests — each bubble gets its own fake clock, so the test is
  deterministic and instant. NEVER `time.Sleep` to sequence goroutines.
- ALWAYS `uber-go/goleak` in `TestMain` for any package that spawns goroutines
  — a leak is invisible to both the compiler and `-race`.

## Anthropic API in Go

- SDK is `github.com/anthropics/anthropic-sdk-go`. NEVER hand-roll the agent
  loop or the JSON-schema plumbing: `toolrunner/` runs the tool loop,
  `betaparse.go` (see `examples/structured-outputs`) gives typed outputs, and
  `mcp/` wires MCP servers in as tools.
- Token counts come from `Messages.CountTokens` — there is NO local tokenizer
  for Claude, so NEVER estimate from string length.
- Tracing is OTel plus `Arize-ai/openinference` (`go/`). There is no Langfuse
  or OpenLLMetry Go SDK — budget for writing the eval harness yourself.
- Models, pricing, params: `claude-api` skill.

## Lints
- No ast-grep pack: golangci-lint (errcheck, revive, the strict-typing set)
  owns Go's structural checks. Add a rule under `skills/go/lints/` only for a
  kronael-specific pattern golangci-lint cannot express — never duplicate it.
