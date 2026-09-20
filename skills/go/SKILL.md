---
name: go
description: Go development. NOT for non-Go code (use rs, py, ts, tsx, or sh).
when_to_use: editing .go files or writing Go code
---

# Go

Requires `software/code.md` (naming, style, comments, design), `software/strict-typing.md`
(golangci-lint set), and `software/dynamic-analysis.md` (test-target checkers:
`-race`, fuzzing, sanitizers). Below are Go-specific additions.

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

### Fixed goroutines, never per-item spawning

ALWAYS size the goroutine set at startup: one owner per subsystem, one reader
per connection, a worker pool with a configured width. NEVER spawn a goroutine
per event, per request, per write, or per queued item.

Per-item spawning looks like it removes latency and does not. It moves the work
without bounding it, so a burst becomes an unbounded goroutine count competing
with the goroutines doing the real job; and it destroys ordering, because N
goroutines racing one writer produce records that overtake each other. A log or
audit trail whose lines can reorder is not a trail.

Smell: `go func(){ ... }()` inside a loop body, a handler, or anything called
once per input. A long-lived goroutine reading a channel is almost always the
answer.

### Offload I/O off the hot path — one sink goroutine

Latency-sensitive code (an event loop, a trading decision, a request handler)
MUST NOT perform a write syscall. A synchronous log line or file append puts
the kernel — and on a bad day a blocked disk or a full pipe — between an input
and the action it should have produced. For as long as that write takes, the
loop has stopped doing its job.

The shape:

```go
// One goroutine owns every blocking write. Callers encode and hand over bytes.
type Sink struct {
    queue  chan record
    stop   chan struct{}   // NEVER close(queue): a send on a closed channel
    done   chan struct{}   // panics no matter how carefully the sender checks
    closed atomic.Bool
    Dropped atomic.Uint64
}

func (s *Sink) Send(r record) {          // hot path: never blocks
    if s.closed.Load() { s.Dropped.Add(1); return }
    select {
    case s.queue <- r:
    default:
        s.Dropped.Add(1)                 // count drops; never stall the caller
    }
}

func (s *Sink) run(pinCore int) {
    defer close(s.done)
    if pinCore >= 0 {
        runtime.LockOSThread()           // a blocking write parks THIS thread
        defer runtime.UnlockOSThread()
        _ = pinToCore(pinCore)           // unix.SchedSetaffinity, Linux only
    }
    for {
        select {
        case r := <-s.queue:
            s.write(r)
        case <-s.stop:
            for {                        // drain: don't lose the tail
                select {
                case r := <-s.queue: s.write(r)
                default: return
                }
            }
        }
    }
}
```

Rules that make it work:

- **Encode on the caller, write on the sink.** Formatting is bounded CPU and
  belongs to whoever asked; the syscall is what must move. Encoding on the sink
  also means holding a reference to caller state until the write happens.
- **Copy before queueing.** Bytes from a reused read buffer or a pooled
  `bytes.Buffer` must be copied, or the sink writes whatever the buffer became.
- **Split backpressure by what a record is worth.** High-rate telemetry drops
  under pressure with a counter; records whose loss breaks an audit (orders,
  transactions, the final report) block for queue room instead. Report the drop
  count and fail the run if it is non-zero.
- **Close in dependency order**: stop producers, drain the sink, then close the
  files. Closing the files first discards what the sink still held.
- **Pinning**: `runtime.LockOSThread` is the portable half and does most of the
  work. True CPU affinity needs `golang.org/x/sys/unix.SchedSetaffinity` behind
  a `//go:build linux` file, with a no-op fallback.

For logging specifically, implement `slog.Handler`: format into a pooled buffer
in `Handle`, copy the bytes out, queue them. Each `Handle` needs its own inner
handler bound to its own buffer — slog handlers are not safe to share against
one writer.

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

- What to comment and how to phrase it: canonical in `software/code.md`
  Comments section. This is the only Go-specific addition — placement.
- ALWAYS put a comment on its own line ABOVE the code it describes; NEVER
  trail it inline. Inline comments crowd the line, get truncated on wrap, and
  drift as the code changes:
  ```go
  // body fully read into buffer above
  _ = resp.Body.Close()
  ```
  not `_ = resp.Body.Close() // body fully read`. The one exception is the
  handler one-liner noted above.

## Testing
- Test files: `*_test.go` next to code
- Skip slow tests: `if testing.Short() { t.Skip() }`
