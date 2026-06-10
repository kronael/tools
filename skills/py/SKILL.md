---
name: py
description: Python development. NOT for shell scripting (use sh) or non-Python code.
when_to_use: editing .py files or writing Python code
---

# Python

## Version
- ALWAYS target Python 3.13+, use newest language features
- `type Alias = int | str` (PEP 695), not `TypeAlias`
- `type Point[T] = tuple[T, T]` for generic type aliases

## Type Annotations
- Builtin generics: `dict[str, float]`, `list[str]`, `Type | None`
- NEVER move imports into `TYPE_CHECKING` blocks — breaks runtime
- NEVER `default_factory=lambda: []` — use `default_factory=list`
- ALWAYS `typing.Protocol` for duck-typed interfaces; use `abc.ABC` only when runtime `isinstance` is required

## getattr/setattr
- Legitimate ONLY when the attribute name is a code-derived value (variable, loop var, expression) unknown until runtime
- Legitimate: `getattr(obj, field_name)` where `field_name` comes from `__dataclass_fields__`, a loop, or an arg
- Legitimate: `setattr(obj, attr, value)` in a reflection loop (applying a dict of field overrides)
- Legitimate: `getattr(obj, 'attr', default)` when `obj` genuinely may lack `attr` (duck typing, optional mixin, `app.state`, enum `.name` fallback)
- Slop: `getattr(world, 'cfg', None)` when `world.cfg` is a declared typed field — write `world.cfg`
- Slop: `setattr(obj, 'literal_field', value)` when the field is declared — write `obj.literal_field = value`
- Test: if you can swap the call for `.attr` syntax and pyright stays quiet, it's slop

## Async
- NEVER manually close async context managers (corrupts asyncpg)
- Return batches, not yield individual items

## Stack
- aiohttp for clients (HTTP + WS), FastAPI for servers
- asyncpg direct, no SQLAlchemy
- dataclasses over Pydantic when enough

## Named Data Structures
- ALWAYS dataclass/NamedTuple over bare tuples for return types (except trivial/test code)

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
- Short vars OK: `n`, `k`, `r`, `i`, `j`, `x`, `y`, `z`, `m`, `g`, `f`, `h`; `ts`, `ms` for time; doubled (`kk`, `vv`) for nested/plural; short descriptive (`data`, `msg`) also fine
- NEVER visually ambiguous singles: `o`, `O`, `I`, `l` (look like `0` or `1`)
- NEVER `sys.path` modification
- NEVER `global` keyword except trivial scripts or signal handlers
- NEVER multi-assign tuples: `a, b, c = x, y, z` — one per line

## Package Structure
- NEVER create `__init__.py` unless it contains actual code

## Build
- uv for packages, pyright for types
- pre-commit: ruff format + lint, end-of-file-fixer, trailing-whitespace
- `make check`: ruff lint + format check (canonical CQ target)
- `make right`: pyright only (not in pre-commit)

## Testing
- ALWAYS `python -m pytest` not `pytest` directly (package discovery)
- Set PYTHONPATH once at Makefile top, not per target
- Testcontainers: centralize in `conftest.py`

## Subprocesses
- `start_new_session=True` on `create_subprocess_exec` (prevents Ctrl-C leak)
- Kill process groups: `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)`
