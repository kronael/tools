# Node multi-worker cluster (CPU-bound services)

Scaling a single-threaded, CPU-bound Node/NestJS service to N workers per pod
with `node:cluster`, routing each connection to an idle worker without
re-serialising payloads. Reference implementation: `cluster/cluster.dispatcher.ts`
(`dispatcherLoop`), `cluster/cluster.worker.ts` (`workerLoop`),
`cluster/cluster.protocol.ts`.

The Node cluster primary is named for its ROLE here — the dispatcher — because
`primary` says nothing about what it does.

## Process shape

- ALWAYS name the long-lived routine of each process kind `xxxLoop()` — one per
  kind, symmetric: `dispatcherLoop()`, `workerLoop()`. NEVER scatter a process's
  main flow across ad-hoc functions.
- ALWAYS name a process for its ROLE, not the framework term: the cluster primary
  IS the dispatcher; `primary`/`main` describe nothing.
- The dispatcher owns the listening socket and the metrics port; a worker's HTTP
  server NEVER calls `listen()` — it only serves connections handed to it, which
  keeps the dispatcher the single place that decides who is idle.
- Fork only when asked to scale: gate on `cluster.isPrimary && workerCount > 1`,
  else run the app inline (`bootstrap()`).

## Pass the socket HANDLE, not the payload

- ALWAYS accept in the dispatcher with `net.createServer({ pauseOnConnect: true })`
  and read NOTHING off the wire; `pauseOnConnect` stops the dispatcher consuming a
  single byte. NEVER parse, decode, or buffer the request in the dispatcher.
- ALWAYS hand the raw handle over IPC: `worker.send({ type: 'connection' },
  socket, cb)`. The worker takes ownership with `server.emit('connection',
  socket)` then `socket.resume()`, and writes the response straight to the
  client.
- The body is serialised exactly ONCE, by the worker that produced it. NEVER
  proxy a decoded payload through the dispatcher — ALWAYS forward the handle so the
  response is not re-serialised in a second process.
- ALWAYS destroy the socket and roll back the worker's load in the `send`
  callback if `error` is set (the worker died mid-handoff).

## Idle-first dispatch (NOT cluster's round-robin)

- Node cluster's built-in scheduler is round-robin: it will park a request
  behind a worker that is mid-computation (head-of-line blocking). For CPU-bound
  work NEVER rely on it — ALWAYS dispatch yourself from the dispatcher.
- ALWAYS track an in-flight count per worker; pick the least-loaded, rotating a
  cursor to break ties. Increment on `send`, decrement on release.
- The worker signals completion by IPC on socket `'close'`: `process.send?.({
  type: 'release' })`; the dispatcher decrements that worker's count and clamps at
  0. NEVER infer completion any other way — the worker owns the truth.
- A `release` decrement MUST read the current count and bail if it is absent
  (`load.get(id)` is `undefined`) — NEVER `(load.get(id) ?? 0) - 1`, which
  re-inserts a dead or unready worker into the pool at count -1.
- When EVERY worker is busy, ALWAYS still route to the least-loaded one; NEVER
  refuse or queue. If every worker just died, hold (retry `setTimeout`) until one
  respawns rather than dropping the connection.
- ALWAYS gate dispatch on a worker-ready handshake: `cluster.fork()` returns
  before the child has attached its `process.on('message')` listener, and a
  socket handed over in that window is SILENTLY DROPPED (Node buffers nothing)
  AND leaks the load counter (no `'close'`, so no `release`) forever. The worker
  sends a `ready` message as the LAST thing in its loop; the dispatcher adds it
  to the pool only then. NEVER seed a freshly forked worker's load at 0 — that
  makes it the *preferred* pick before it can receive. Fires on every crash
  respawn under live traffic, not just cold start.

## Prometheus across workers = PULL via clusterMetrics()

- ALWAYS aggregate with prom-client's `AggregatorRegistry.clusterMetrics()` (the
  production standard; PM2's pm2-cluster-prometheus wraps the same call): on
  scrape the dispatcher asks each worker for its registry over IPC and sums, then
  appends its own dispatcher gauges. NEVER build a bespoke push-snapshot channel
  — it is needless complexity that duplicates a built-in.
- **THE GOTCHA (cost two debugging cycles):** the worker-side responder is
  installed ONLY by CONSTRUCTING an `AggregatorRegistry` INSIDE the worker
  process — `new AggregatorRegistry()` for its constructor side-effect (it adds
  the IPC listener, guarded to the worker branch). Merely `import`ing prom-client
  does NOT install it. If you construct the aggregator only in the dispatcher, every
  `/metrics` scrape returns **HTTP 500 "Operation timed out" after exactly 5s**
  (prom-client's internal request timeout) because no worker ever answers.
- prom-client's docs line "instantiate the cluster registry before branching on
  `cluster.isPrimary`" is LOAD-BEARING, not stylistic — ALWAYS construct the
  aggregator in both process kinds.

## Worker count = pod CPU limit, NOT host cores

- `os.availableParallelism()` reports the HOST's cores, not the cgroup/pod CPU
  limit — a 4-CPU k8s pod on a 64-core node would fork 64 workers.
- ALWAYS read an explicit env (`WORKERS`) set to the pod's CPU allocation;
  validate it as a positive integer and throw on garbage. Fall back to
  `availableParallelism()` ONLY for a local single-box run.

## Per-worker in-memory state multiplies by N

- Anything counted or cached in-process is now `value × workers`: an in-memory
  rate limiter enforces `limit × workers`, an in-memory cache holds N copies.
- ALWAYS flag this whenever adding workers. NEVER leave an in-process
  limit/counter unexamined under a cluster.
- For a per-IP rate limiter under NON-STICKY dispatch, PREFER defining the
  config value as PER WORKER and letting whoever sets the env pick it — the code
  stays a plain `limit: config.max` with no arithmetic, and the operator already
  knows the worker count. ALWAYS say so where the value is read, so nobody reads
  it as a pod-wide cap. Dividing a pod-wide value in code
  (`ceil(limit / workers)`) is the alternative; it hides a second knob inside the
  app and buys nothing the operator cannot set directly. NEVER reach for a shared
  store (Redis) for this unless you need an exact global cap.

## Run pod-wide singletons in the DISPATCHER, not in a tagged worker

- A poller, a cron, or the sole writer of a shared file MUST run in exactly one
  process — N workers each running it means N× the external calls and, for a
  shared file, concurrent writers that corrupt it.
- ALWAYS run it in the dispatcher: it already exists exactly once, serves no
  requests, and never dies-and-respawns. In Nest that is
  `NestFactory.createApplicationContext(AppModule)` alongside `dispatcherLoop()`
  — no HTTP server, same DI graph. NEVER elect a "leader" worker via a fork env
  and re-tag its replacement on death: that invents an identity the runtime
  already gives you, and every worker crash becomes a re-election.
- The discriminator is then just `cluster.isPrimary` — true in the dispatcher AND
  in a non-clustered single-process run, so unclustered behaviour is unchanged
  and no env var is needed.
- Workers that need the singleton's output ALWAYS re-read the shared artifact;
  the writer ALWAYS writes it atomically (`write tmp` + `rename`) so a reader
  mid-write gets the old complete version, never a torn one.
- Split the artifact by change rate: a large slow-changing file is re-read ONLY
  when its `mtime` moves (one `stat` per poll, not a reparse), while a small
  fast-changing value (an intraday price, a leader-elected config) gets its own
  single-line file that is cheap to re-read every tick. NEVER poll by reparsing
  the big file on a timer, and NEVER leave the fast value in the writer's memory
  only — it silently diverges per worker.

## Fail loud on bind, but NEVER on a client reset

- ALWAYS exit non-zero from the dispatcher on the listen `'error'` event (shut
  down, set `process.exitCode = 1`). NEVER swallow it — otherwise the dispatcher
  survives a failed bind while the `exit` handler keeps respawning workers: a pod
  that is "up" but serves nothing.
- ALWAYS attach an `'error'` listener to EVERY accepted socket. A plain
  `net.Socket` with no listener THROWS on RST, which lands in
  `process.on('uncaughtException')` and kills the dispatcher — one client reset
  (health-check timeout, aborted request) takes down the whole pod. Attach it
  once in the connection callback (`socket.on('error', () => socket.destroy())`),
  NOT inside a retrying `dispatch()` that would stack duplicate listeners.

## Keep the periodic yield — do NOT disable it per-connection

- ALWAYS keep the hot path's periodic `setImmediate` yield ON. It is what lets a
  worker answer IPC — a metrics request, a second dispatched connection, a client
  abort — at its next yield boundary instead of only when the whole job finishes.
- The real per-call cost is the `await`, not the yield: ALWAYS gate it —
  `const p = yieldWork(i); if (p !== undefined) await p` — so the 9999/10000
  no-op calls never touch the microtask queue. That gate is the actual win.
- NEVER add a "this worker holds one connection, so stop yielding entirely" flag.
  It saves only the handful of real `setImmediate`s per job (negligible) while
  stalling every `/metrics` scrape for the full duration of that worker's current
  job — and prom-client's `clusterMetrics()` 5s timeout will 500 the scrape once
  a job runs long. A worker that never yields also cannot observe the second
  connection that would have told it to start yielding.
