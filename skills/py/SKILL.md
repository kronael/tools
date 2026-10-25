---
name: py
description: Python development. NOT for shell scripting (use sh) or non-Python code.
when_to_use: "editing .py files, writing Python; dataclasses, TypedDict, pydantic, dacite, heterogeneous records, hashable keys, type hints, enums, asyncio/asyncpg, pytest, ruff, pyright, uv, FastAPI; psycopg, pg_config not found, binary wheel; rename, codemod, LibCST, move a module"
---

# Python

ALWAYS Read `../software/code.md` before the first edit — it owns naming,
comments, design and the boring-code rules. Also requires
`../software/dynamic-analysis.md` (test-target checkers:
`-X dev -W error`, hypothesis, pytest-memray, TSan). Below are
Python-specific additions and deltas.

## Verify before claiming
- ANY syntax or type question: run `python3 -c "import ast; ast.parse(...)"`, `uv run pyright`, or `ruff check` — NEVER speculate or hedge.

## Version
- ALWAYS target Python 3.13+, use newest language features
- `type Alias = int | str` (PEP 695), not `TypeAlias`
- `type Point[T] = tuple[T, T]` for generic type aliases

## Type Annotations
- Builtin generics: `dict[str, float]`, `list[str]`, `Type | None`
- NEVER `Any` in an annotation — bare or inside a generic (`dict[str, Any]`, `list[Any]`): a value whose shape has no name is a dataclass not yet written (§ Named Data Structures). `../software/strict-typing.md` holds the config and the narrow suppression for pass-through `**kwargs` below.
- NEVER move imports into `TYPE_CHECKING` blocks — breaks runtime
- NEVER `default_factory=lambda: []` — use `default_factory=list`; for typed collections pass the parametrized type: `default_factory=dict[K, V]`
- NEVER reflexively add `| None` — if a field is always set at construction give it a real default (`x: float = 0.0`), not `x: float | None = None`. `| None` is for genuine sentinels / optional deps / nullable returns only
- ALWAYS `typing.Protocol` for duck-typed interfaces; use `abc.ABC` only when runtime `isinstance` is required
- ALWAYS declare a `Protocol`'s data members as read-only `@property`s — a plain class then satisfies it with plain assignments (`name = 'x'`, `lists = ()`, `server = Server()`). NEVER a bare `name: str` or `ClassVar` member in a protocol a class implements by assignment, unless code reads it off the class itself: a mutable member is invariant, so a subtype value fails.
- ALWAYS name a `Protocol` by the plain noun of the thing it describes (`Venue`, `Job`, `Server`); an implementation is often `<Qualifier><Noun>` (`BinanceVenue`) but takes any fitting name. `<Verb>able` when it promises one or a few methods and nothing else (`Runnable`: `run()`). NEVER a suffix or prefix that only says it is a protocol: `VenueLike`, `VenueProtocol`, `VenueInterface`, `IVenue`
- NEVER introduce `Protocol` or broad duck typing only for tests/fakes — ALWAYS type production code from production contracts
- NEVER `Literal['a', 'b']` for domain values — ALWAYS use `enum.Enum` (or `str, Enum` for pydantic/TOML compat). `Literal` is only for narrowing external/library types you do not own.
- Compare enum members with `is` / `is not`, not `==` / `!=` — enums are singletons; `is` makes the identity check explicit: `if status is GameStatus.LOST:` not `if status == GameStatus.LOST:`
- ALWAYS write an `Enum` member's value, `LIVE = 1` — NEVER `auto()`. Lint `py-no-enum-auto`.
- Forward a pass-through `**kwargs` as plain `**kwargs: Any` to a callee that owns the real typed signature, with the narrow suppressions in `../software/strict-typing.md` — NEVER `Unpack` over a kwargs `TypedDict` (§ Named Data Structures bans declaring one anyway): the machinery costs more than the duplication it removes
- NEVER widen an annotation to `object` to silence a checker complaint — ALWAYS read what the values actually are and name that (`Mapping[str, str]`, never `Mapping[str, object]`). A dodge annotation switches the checker off at the one place it was working. `object` is right only for a value genuinely never inspected, such as a discarded callback return
- NEVER answer a container-invariance error by widening the value type — ALWAYS take `Mapping` or `Sequence`, which are covariant, and keep the precise value type

## Naming
`software/code.md` § Naming owns names. Python additions:
- ALWAYS call `datetime.now(UTC)` and `.date()` directly — NEVER wrap them in a `now()`/`today()` helper, NEVER `utcnow()` (deprecated, naive).
- ALWAYS name item-iteration helpers `iter_<items>`; preserve framework-required names.

## Properties and accessor overrides
- NEVER use `@property`, `@x.setter`, or `__getattr__`/`__setattr__` overrides — they are code smell
- They hide computation behind attribute access, break "no surprises" reads, and make grep useless
- Four legitimate exceptions:
  1. **Mocking / test doubles** — overriding attribute access on a stub
  2. **Adapting external/library code** — wrapping an API you don't own that requires property protocol
  3. **A record's value derived from its own fields** — § Named Data Structures owns the rule
  4. **A `Protocol`'s data member** — a read-only declaration with only `...` or `pass` (§ Type Annotations); the lint exempts that declaration
- Instead: plain method (`def program_lookup(self)`) or compute once and store on the dataclass field

## getattr/setattr
- Legitimate ONLY when the attribute name is a code-derived value (variable, loop var, expression) unknown until runtime
- Legitimate: `getattr(obj, field_name)` where `field_name` comes from `__dataclass_fields__`, a loop, or an arg
- Legitimate: `setattr(obj, attr, value)` in a reflection loop (applying a dict of field overrides)
- Legitimate: `getattr(obj, 'attr', default)` when `obj` genuinely may lack `attr` (duck typing, optional mixin, `app.state`, enum `.name` fallback)
- Slop: `getattr(world, 'cfg', None)` when `world.cfg` is a declared typed field — write `world.cfg`
- Slop: `setattr(obj, 'literal_field', value)` when the field is declared — write `obj.literal_field = value`
- Test: if you can swap the call for `.attr` syntax and pyright stays quiet, it's slop

## Async
- NEVER manually close async context managers (corrupts asyncpg) — ALWAYS `async with`
- ALWAYS return batches from data-fetch functions; use iterators when the caller controls scheduling or consumption.
- NEVER send short local file I/O (`open`, `stat`, `exists`, a small read, a chunk
  write) to a thread or `aiofiles`, which is the same thread pool — the handoff costs
  more than the I/O. ALWAYS run it inline and silence ruff with `# noqa: ASYNC230` /
  `ASYNC240` plus a one-clause reason.
- ALWAYS run long blocking work (unpacking a large archive) through the project's one
  shared `to_thread` helper — NEVER a per-module wrapper.
- ALWAYS write a thread's output through `.part` + `os.replace`, so a cancel leaves
  only a file the next run replaces; work that must stop on cancel ALWAYS runs as a
  subprocess — a thread cannot be cancelled.
- ALWAYS have a retry helper take a plain backoff sequence and `iter()` it on each
  call (`@retry(BACKOFF, …)`) — NEVER make call sites pass `lambda: iter(...)`.

## Stack
- ALWAYS follow `software/code.md` § System changes for existing layer idioms.
  With no repo choice, ALWAYS use aiohttp for clients (HTTP + WS), FastAPI for servers.
- ALWAYS asyncpg direct, NEVER SQLAlchemy. A database module — one call per operation, lists in and out, a batch as one `jsonb` or array parameter — is the `sql` skill § Database Modules.

## Named Data Structures
- ALWAYS a `dataclass` for every application-owned structured value — record, return value, parameter bundle,
  queued work item, decoded message. NEVER declare a `TypedDict`: at runtime it is a plain
  dict, so a payload cast to it is never checked and a missing key fails at the read, not at
  the boundary.
- For `../software/code.md` § Design, ALWAYS use one `@dataclass(frozen=True)` per variant
  on one `Protocol` or small base; dispatch with `isinstance(sample, Quote)` / `case Quote():`.
  Lints `py-no-str-case-dispatch` and `py-no-str-callable-table` — a `dict[str, Callable]` table is
  the same dispatch respelled. NEVER a `KIND`/`VERSION` `ClassVar` on a variant: its stored
  format's version is its module's name, `depth_v1.py`.
- ALWAYS confine pydantic to the input/output boundary that needs validation or coercion —
  external API JSON, HTTP bodies, config files; NEVER a pydantic model for a value born inside
  the program: the validation costs and catches nothing there.
- ALWAYS preserve upstream wire types and their codecs (`software/code.md` § Design); otherwise use the project's
  one codec (`from_dict`/`to_dict`) — NEVER dacite, cattrs or a hand-written `cls(**d)` beside it; a second
  structurer drifts from the first.
- ALWAYS put a constructor that only derives a record from its own inputs on the record as a
  classmethod (`Changes.of(writes)`), and a value computed from its own fields as a property —
  NEVER a method that does I/O, reads config or uses another layer's types; that stays a
  plain function beside the layer that owns the rule.
- ALWAYS build a record from a row of the program's own SQL with `Record(**row)`, the SQL naming
  its output columns as the fields — NEVER `Record(row['a'], row['b'], ...)`; `**row` fails on a
  missing or extra column.
- NEVER `NamedTuple` — a record that is also a tuple invites the positional access `@dataclass(frozen=True)` exists to stop, and `slots=True` gives the same compactness
- ALWAYS `@dataclass(frozen=True)` by default for value/data types — freezing prevents field reassignment, not mutation inside a field. Drop `frozen` only for types deliberately mutated in place (accumulators, stateful objects like `World`/`Client`), whose updates are its methods (`../software/code.md` § Design).
- PREFER `frozen=True, slots=True` together — slots adds faster attribute access + lower memory; the cost is only modest construction/hash overhead (reads are free)
- ALWAYS use frozen dataclasses for heterogeneous dict/set keys, with hashable fields and stable equality/hash behavior; `frozen=True` alone does not guarantee hashability.
- A wider frozen key projects to a narrower one via a named accessor (`order_key`), NEVER by slicing `key[:4]`
- NEVER `kw_only=True` / `InitVar` to dodge dataclass field-ordering — if every caller passes a value the default is dead, so make the field required
- NEVER use tuple as a generic collection just because the values are not mutated — ALWAYS use `list` for ordinary sequences; reserve tuple for dict/set keys, deliberate immutability boundaries, varargs/returns where positional shape is the point, or small fixed heterogeneous records when a dataclass would be overkill.

## Datetime
- `datetime.fromtimestamp(ts, tz=timezone.utc)` not `utcfromtimestamp`

## Logging
- ALWAYS `log = logging.getLogger(__name__)` — variable ALWAYS named `log`

## Imports
- NEVER alias a module import unless the name genuinely collides: `import json_utils` not `import json_utils as ju`
- When aliasing a symbol import, use the source module as prefix: `from heapq import merge as heapq_merge`

## Style
- NEVER a docstring on a private function, method, or class — `code.md`'s
  public-API exception is the whole allowance. A module docstring only where
  the module is an imported public surface
- Exception variables: NEVER `e` — use `ex`, `exc`, `err`
- Use `async with asynccontextmanager` for resource cleanup, never bare `try/finally` for pools/connections
- Python-specific short vars: `ts`, `ms` for time
- NEVER `sys.path` modification — ALWAYS set PYTHONPATH or install the package
- NEVER `global` keyword except trivial scripts or signal handlers — ALWAYS pass state explicitly
- NEVER multi-assign tuples: `a, b, c = x, y, z` — one per line
- NEVER `dict(...)` for a value built in place — ALWAYS the `{}` literal, or an `Enum` for a closed
  set of names; allowed only as a call argument, `log.info(..., extra=dict(id=id))`. Lint `py-no-dict-call`
- Emptiness by truthiness: `if not xs` / `if xs`, NEVER `len(xs) == 0` / `len(xs) > 0` (works for any `__len__`/`__bool__` type)
- NEVER rewrite an expression into an equivalent form for its own sake (`Field(None)` → `Field(default=None)`, adding/removing a redundant `# noqa`) — keep diffs to real changes
- For small fixed sequences used only by a `for` loop, prefer comma iteration: `for x in A, B:` not `for x in [A, B]` or `for x in (A, B)`
- NEVER contort an f-string to fit its own quotes — no same-quote nesting, no `chr(39)`, no expression reshaped to dodge a brace. ALWAYS bind the value to a local on the line above and interpolate the bare name (PEP 701 permits the nesting; readability bans it)

## Package Structure
- NEVER create `__init__.py` unless it contains actual code

## Refactor tools
- ALWAYS rename with the `serena` skill — NEVER grep-and-edit.
- ALWAYS take a rewrite ruff has a rule for through ruff: `ruff check
  --select <rule> --fix --diff`, then without `--diff` — NEVER hand-edit
  each site (`UP006` turns `List[int]` into `list[int]`).
- ALWAYS update every import and use after moving an object with LibCST —
  NEVER by hand. `--no-format` skips its default formatter, black; `-u3`
  prints a diff instead of writing:
  `uv run --with libcst python -m libcst.tool codemod --no-format -u3
  rename.RenameCommand --old_name pkg.old.f --new_name pkg.new.f .` — it
  rewrites the users, not the definition you moved.
- ALWAYS a LibCST codemod for a structural change no rule covers (add an
  argument at every call, change a signature): a `VisitorBasedCodemodCommand`
  in a module outside the repo, run as `PYTHONPATH=<dir> uv run --with libcst
  python -m libcst.tool codemod -x --no-format <module>.<Class> <paths>`. It
  keeps comments and whitespace; `ruff format` after.

## Lints
- ast-grep rules in `skills/py/lints/` (`make lints`): `py-except-var-e`,
  `py-no-lambda-default-factory`, `py-no-property`, `py-no-enum-auto`, `py-bool-fn-prefix`
  (`software/code.md` § Naming), `py-no-str-case-dispatch`, `py-no-str-callable-table`, `py-no-dict-call` (overlaps ruff
  `C408` only because `C408` cannot spare the call-argument form). ruff owns the rest — NEVER duplicate a ruff rule here.

## Build
- uv for packages, pyright for types
- NEVER a binary wheel of a native dependency (`psycopg2-binary`, `psycopg[binary]`): its
  bundled libssl segfaults beside `ssl` — ALWAYS the source build, the builder given the
  dev headers (`libpq-dev`).
- ALWAYS one project-wide `typeCheckingMode: "strict"` over every source; NEVER a
  `basic` default with a per-file `strict` list. Every test file opts down with
  `# pyright: basic` on its first line.
- pre-commit: ruff format + lint, end-of-file-fixer, trailing-whitespace
- `make check`: ruff lint + format check (canonical CQ target)
- `make right`: pyright only (not in pre-commit)
- `except T, V:` (no parens) is VALID on Python 3.14 (PEP 758), a SyntaxError only on <3.14. ruff 0.15.17 `ruff-format` strips the parens from `except (T, V):` — fine on 3.14; if the code must also run on <3.14, guard with `except (T, V):  # fmt: skip`

## Testing
- ALWAYS `python -m pytest` not `pytest` directly (package discovery)
- Set PYTHONPATH once at Makefile top, not per target
- Testcontainers and the fixture directory centralize in `conftest.py`: one fixture returning `pytestconfig.rootpath / '<tree>/tests/assets'` — NEVER `Path(__file__)` (`code.md` § Layout and formatting)
- ALWAYS build properly shaped test doubles (`Mock` / `MagicMock` with explicit
  attrs or a small fake class); NEVER make production code tolerate incomplete
  fakes
- NEVER add production parameters solely to replace functions in tests — ALWAYS patch the symbol at its use site when a test needs substitution; keep dependency parameters for real production dependencies.
- Tests stay loose: `# pyright: basic`, and annotate a test only where it documents a contract — NEVER type-fit fixtures, fakes or test functions to strict; NEVER weaken production annotations for fake convenience

## Subprocesses
- ALWAYS start one with `asyncio.create_subprocess_exec(..., start_new_session=True)`
  — NEVER the stdlib `subprocess` from async code, it blocks the loop. The new
  session keeps Ctrl-C off the child and gives it a process group to signal.
- ALWAYS run it inside the project's one async context manager that yields the
  process: a normal block exit waits for it and reaps it; an exception or a cancel
  sends SIGTERM to the group, waits a grace period, sends SIGKILL, and reaps. NEVER
  a hand-rolled `os.killpg` at a call site.
- ALWAYS implement artifact capture and compression in the top-level Python
  runner when the whole orchestration stack is Python — NEVER require shell
  redirection for it
