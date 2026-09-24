# Go concurrency

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
    queue   chan record
    stop    chan struct{}
    done    chan struct{}
    closed  atomic.Bool
    Dropped atomic.Uint64
}

// Send never blocks: a full or closed sink counts the record in Dropped.
func (s *Sink) Send(r record) {
    if s.closed.Load() { s.Dropped.Add(1); return }
    select {
    case s.queue <- r:
    default:
        s.Dropped.Add(1)
    }
}

func (s *Sink) run(pinCore int) {
    defer close(s.done)
    if pinCore >= 0 {
        runtime.LockOSThread()
        defer runtime.UnlockOSThread()
        // affinity is best-effort; the sink stays off the hot path without it
        _ = pinToCore(pinCore)
    }
    for {
        select {
        case r := <-s.queue:
            s.write(r)
        case <-s.stop:
            for {
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
- **Stop on a separate channel; NEVER `close(queue)`.** A send on a closed
  channel panics however carefully the sender checks `closed` first. The stop
  case drains the queue before returning, so the tail is written.
- **Close in dependency order**: stop producers, drain the sink, then close the
  files. Closing the files first discards what the sink still held.
- **Pinning**: `runtime.LockOSThread` is the portable half and does most of the
  work. True CPU affinity needs `golang.org/x/sys/unix.SchedSetaffinity` behind
  a `//go:build linux` file, with a no-op fallback.

For logging specifically, implement `slog.Handler`: format into a pooled buffer
in `Handle`, copy the bytes out, queue them. Each `Handle` needs its own inner
handler bound to its own buffer — slog handlers are not safe to share against
one writer.

