---
name: py
description: Python development. USE when editing .py files or writing Python code. pyproject.toml, pytest, aiohttp, FastAPI, asyncpg, dataclass, async/await, type annotations. NOT for shell scripting (use sh) or non-Python code.
---

# Python

## Version
- ALWAYS target Python 3.14+, use newest language features
- `type Alias = int | str` (PEP 695), not `TypeAlias`
- `type Point[T] = tuple[T, T]` for generic type aliases

## Type Annotations
- Builtin generics: `dict[str, float]`, `list[str]`, `Type | None`
- NEVER move imports into `TYPE_CHECKING` blocks — breaks runtime
- NEVER `default_factory=lambda: []` — use `default_factory=list`

## Async
- NEVER manually close async context managers (corrupts asyncpg)
- Return batches, not yield individual items

## Stack
- aiohttp for clients (HTTP + WS), FastAPI for servers
- asyncpg direct, no SQLAlchemy
- dataclasses over Pydantic when enough

## Named Data Structures
- Prefer dataclass/NamedTuple over bare tuples for return types
- Skip for trivial cases or test code

## Datetime
- `datetime.fromtimestamp(ts, tz=timezone.utc)` not `utcfromtimestamp`

## Logging
- ALWAYS `log = logging.getLogger(__name__)` — variable ALWAYS named `log`

## Style
- Exception variables: NEVER `e` — use `ex`, `exc`, `err`
- NEVER ambiguous single-letter loop vars (`o`, `c`, `l`) — use descriptive names
- NEVER `sys.path` modification
- NEVER `global` keyword except trivial scripts or signal handlers
- NEVER multi-assign tuples: `a, b, c = x, y, z` — one per line

## Package Structure
- NEVER create `__init__.py` unless it contains actual code

## Build
- uv for packages, pyright for types
- pre-commit: ruff format + lint, end-of-file-fixer, trailing-whitespace
- `make right`: pyright only (not in pre-commit)

## Testing
- ALWAYS `python -m pytest` not `pytest` directly (package discovery)
- Set PYTHONPATH once at Makefile top, not per target
- Testcontainers: centralize in `conftest.py`

## Subprocesses
- `start_new_session=True` on `create_subprocess_exec` (prevents Ctrl-C leak)
- Kill process groups: `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)`
