---
name: py
description: Python development. NOT for shell scripting (use sh) or non-Python code.
when_to_use: editing .py files, writing Python; dataclasses, type hints, enums, asyncio/asyncpg, pytest, ruff, pyright, uv, FastAPI
---

# Python

## Verify before claiming
- ANY syntax or type question: run `python3 -c "import ast; ast.parse(...)"`, `uv run pyright`, or `ruff check` — NEVER speculate or hedge.

## Version
- ALWAYS target Python 3.13+, use newest language features
- `type Alias = int | str` (PEP 695), not `TypeAlias`
- `type Point[T] = tuple[T, T]` for generic type aliases

## Type Annotations
- Builtin generics: `dict[str, float]`, `list[str]`, `Type | None`
- NEVER move imports into `TYPE_CHECKING` blocks — breaks runtime
- NEVER `default_factory=lambda: []` — use `default_factory=list`; for typed collections pass the parametrized type: `default_factory=dict[K, V]`
- NEVER reflexively add `| None` — if a field is always set at construction give it a real default (`x: float = 0.0`), not `x: float | None = None`. `| None` is for genuine sentinels / optional deps / nullable returns only
- ALWAYS `typing.Protocol` for duck-typed interfaces; use `abc.ABC` only when runtime `isinstance` is required
- NEVER `Literal['a', 'b']` for domain values — ALWAYS use `enum.Enum` (or `str, Enum` for pydantic/TOML compat). `Literal` is only for narrowing external/library types you do not own.
- Compare enum members with `is` / `is not`, not `==` / `!=` — enums are singletons; `is` makes the identity check explicit: `if status is GameStatus.LOST:` not `if status == GameStatus.LOST:`

## Naming
- ALWAYS name functions and methods as verbs: `get_programs()`, `build_index()`, `compute_pnl()`
- NEVER name a function as a noun: `program_lookup`, `symbol_map`, `client_index` — these read as data, not actions
- Exception: boolean predicates — `is_funded()`, `has_positions()`, `can_advance()`

## Properties and accessor overrides
- NEVER use `@property`, `@x.setter`, or `__getattr__`/`__setattr__` overrides — they are code smell
- They hide computation behind attribute access, break "no surprises" reads, and make grep useless
- Two legitimate exceptions:
  1. **Mocking / test doubles** — overriding attribute access on a stub
  2. **Adapting external/library code** — wrapping an API you don't own that requires property protocol
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
- NEVER yield individual items; ALWAYS return batches

## Stack
- ALWAYS aiohttp for clients (HTTP + WS), FastAPI for servers
- ALWAYS asyncpg direct, NEVER SQLAlchemy
- ALWAYS dataclasses over Pydantic unless validation/coercion is needed

## Named Data Structures
- ALWAYS dataclass/NamedTuple over bare tuples for return types (except trivial/test code)
- ALWAYS `@dataclass(frozen=True)` by default for value/data types — immutability prevents aliasing bugs, makes instances hashable, and catches accidental mutation at runtime. Drop `frozen` only for types that are deliberately mutated in place (accumulators, stateful objects like `World`/`Client`)
- PREFER `frozen=True, slots=True` together — slots adds faster attribute access + lower memory; the cost is only modest construction/hash overhead (reads are free)
- ALWAYS `@dataclass(frozen=True)` over a heterogeneous tuple used as a dict/map key — positional `key[2]` or `key[:4]` access is a smell; name the fields
- A wider frozen key projects to a narrower one via a named accessor (`order_key`), NEVER by slicing `key[:4]`
- NEVER `kw_only=True` / `InitVar` to dodge dataclass field-ordering — if every caller passes a value the default is dead, so make the field required

## Datetime
- `datetime.fromtimestamp(ts, tz=timezone.utc)` not `utcfromtimestamp`

## Logging
- ALWAYS `log = logging.getLogger(__name__)` — variable ALWAYS named `log`

## Imports
- NEVER alias a module import unless the name genuinely collides: `import json_utils` not `import json_utils as ju`
- When aliasing a symbol import, use the source module as prefix: `from heapq import merge as heapq_merge`

## Style
- Exception variables: NEVER `e` — use `ex`, `exc`, `err`
- Use `async with asynccontextmanager` for resource cleanup, never bare `try/finally` for pools/connections
- Short vars OK: `n`, `k`, `r`, `i`, `j`, `x`, `y`, `z`, `m`, `g`, `f`, `h`; `ts`, `ms` for time; doubled (`kk`, `vv`) for nested/plural; short descriptive (`data`, `msg`) — NEVER visually ambiguous `o`, `O`, `l`, `I`
- NEVER `sys.path` modification — ALWAYS set PYTHONPATH or install the package
- NEVER `global` keyword except trivial scripts or signal handlers — ALWAYS pass state explicitly
- NEVER multi-assign tuples: `a, b, c = x, y, z` — one per line

## Package Structure
- NEVER create `__init__.py` unless it contains actual code

## Build
- uv for packages, pyright for types
- pre-commit: ruff format + lint, end-of-file-fixer, trailing-whitespace
- `make check`: ruff lint + format check (canonical CQ target)
- `make right`: pyright only (not in pre-commit)
- ruff 0.15.17 `ruff-format` strips parens from `except (TypeError, ValueError):` → Py2 `except T, V:` (SyntaxError); guard with `except (TypeError, ValueError):  # fmt: skip`

## Testing
- ALWAYS `python -m pytest` not `pytest` directly (package discovery)
- Set PYTHONPATH once at Makefile top, not per target
- Testcontainers: centralize in `conftest.py`
- NEVER monkeypatch module globals (`module.fn = stub`) for a test seam — ALWAYS inject the dep as a param (`get_cfg_fn: Callable[...] | None = None`) defaulting to the module fn (`get_cfg_fn or get_cfg`)

## Subprocesses
- `start_new_session=True` on `create_subprocess_exec` (prevents Ctrl-C leak)
- Kill process groups: `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)`
