# Refine lenses — py

What a Python refine pass goes looking for. Read WITH the `py` skill
(write-time rules), NEVER instead of it. Each lens carries the tag refine step 6
reads to pick the agent type.

## One shared helper, never a local copy `simplify`

- NEVER wrap short local file I/O in a thread or `aiofiles`, and NEVER pair
  `open`/`close` where `with` belongs.
- ALWAYS apply `software.md` § Second path beside the first to added thread, subprocess, retry, clock and JSON helpers.
  ALWAYS inspect added `(_utils|helpers|common).py` files, sleep/clock bodies and `to_<type>` over `JsonValue`/`dict`/`Any`;
  ALWAYS compare with `rg -n '^(async )?def ' <lib>`, its codec and boundary pydantic (`py` § Named Data Structures).

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
- NEVER a wrapper that only renames stdlib (`today()` for `datetime.now(UTC).date()`).
- ALWAYS pass the record, NEVER its fields one by one; ALWAYS the domain term
  (`interval`), NEVER a vague one (`nested`, `granularity`).
- NEVER a `type X = tuple[A, B]` alias or a `-> tuple[A, B]` of unlike parts
  (`rg -n 'tuple\[' <added files>`): a shape that earned a name is a
  dataclass unless it meets a tuple exception in `py` § Named Data Structures.
- ALWAYS compare added wire models and field-copy conversions with upstream exports;
  ALWAYS flag replacements for standard types (`software/code.md` § Design; `py` § Named Data Structures).
- ALWAYS grep the added lines, never the tree total, for the typing dodges —
  `git diff <range> | rg '^\+' | rg -n '\bAny\b|: object\b|getattr\(|hasattr\(|
  == ?[\x27"][a-z_]+[\x27"]'` — each is a finding: name the shape, read the
  declared field, make the closed set an Enum (`py` § Type Annotations,
  § getattr/setattr). A `| None` on a field or return where `None` cannot
  occur, and the `assert x is not None` at each caller it breeds, is the same
  finding: return the value and raise where it is missing.

## Less source `simplify`

- NEVER a comment or docstring that restates the code; keep one short clause
  only for a non-obvious why.
- NEVER an option or branch no caller uses. The change MUST shrink the source
  unless it adds a needed capability.
- NEVER defensive generator plumbing: no `aclose()`, `aclosing` or
  `try`/`finally` around a generator or iterator that holds no resource of its
  own; exhaustion or `asyncio.run` shutdown finalizes it.

## Primitives that protect nothing `simplify`

- ALWAYS name, for every `Lock`, `Semaphore`, `Condition`, `Event`, `Queue`
  or bucket the range adds, the interleaving or bound it enforces. Between two
  awaits nothing else runs, so a lock around a non-awaiting section protects
  nothing; a second bucket or limiter where one budget exists is a finding
  (`software.md` § Abstraction that does not pay, fan-out bullet).
- ALWAYS read every `gather`/`TaskGroup` over network calls the range adds:
  N calls with no semaphore is N requests at once.
- Added SQL text in `.py` strings reads the `sql.md` lens in this directory.

## Config `correctness`

- ALWAYS one project-wide pyright `strict`, NEVER `basic` plus a per-file
  `strict` list; a test file opts down with `# pyright: basic`.
- NEVER a formatter workaround (`# fmt: skip`) the pinned formatter config
  already makes redundant.
