# Refine lenses — py

What a Python refine pass goes looking for. Read WITH the `py` skill
(write-time rules), NEVER instead of it. Each lens carries the tag refine step 6
reads to pick the agent type.

## One shared helper, never a local copy `simplify`

- NEVER wrap short local file I/O in a thread or `aiofiles`, and NEVER pair
  `open`/`close` where `with` belongs.
- NEVER accept a per-module wrapper around threads, subprocesses, retry or
  clocks. ALWAYS grep the project's shared lib first: reuse its helper, or put
  the missing one there.

## Threads and subprocesses end before their caller `correctness`

- ALWAYS make the shared thread helper wait for its thread on cancel
  (`create_task` + `shield`, then await the job again); NEVER let a call site
  hand-roll it.
- NEVER a hand-rolled `killpg` per call site. ALWAYS one context manager: a
  normal exit waits and reaps; an exception or a cancel sends SIGTERM to the
  group, waits a grace period, then SIGKILL — with a `run` wrapper that raises
  `CalledProcessError`.

## Data, not code, at the call site `simplify`

- NEVER a lambda where data would do: an option takes a tuple, sequence or
  collection as its plain form, and a callable only as a separate keyword. A
  callable delay receives the attempt and the outcome.
- NEVER a string where an Enum exists, and NEVER parallel lookup tables or an
  if/elif chain per member — ALWAYS one table of frozen records.
- NEVER build a mapping with `dict.fromkeys(keys, value)` or another clever
  construct where an explicit literal is clearer.
- NEVER a wrapper that only renames stdlib (`today()` for
  `datetime.now(UTC).date()`), and NEVER `utcnow()`.
- ALWAYS pass the record, NEVER its fields one by one; ALWAYS the domain term
  (`interval`), NEVER a vague one (`nested`, `granularity`).

## Less source `simplify`

- NEVER a comment or docstring that restates the code; keep one short clause
  only for a non-obvious why.
- NEVER an option or branch no caller uses. The change MUST shrink the source
  unless it adds a needed capability.
- NEVER defensive generator plumbing: no `aclose()`, `aclosing` or
  `try`/`finally` around a generator or iterator that holds no resource of its
  own; exhaustion or `asyncio.run` shutdown finalizes it.

## Config `correctness`

- ALWAYS one project-wide pyright `strict`, NEVER `basic` plus a per-file
  `strict` list; a test file opts down with `# pyright: basic`.
- NEVER a formatter workaround (`# fmt: skip`) the pinned formatter config
  already makes redundant.
