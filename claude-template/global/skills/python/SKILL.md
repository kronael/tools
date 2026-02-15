---
name: python
description: Python development. .py files, pyproject.toml, pytest, aiohttp, FastAPI, asyncpg, dataclass, async/await, type annotations.
---

# Python

## Type Annotations
- `dict[str, float]` not `Dict[str, float]`
- `list[str]` not `List[str]`
- `Type | None` not `Optional[Type]`

## Async
- NEVER manually close async context managers (corrupts asyncpg)
- Return batches, not yield individual items

## Stack
- aiohttp for clients (HTTP + WS), FastAPI for servers
- asyncpg direct, no SQLAlchemy
- dataclasses over Pydantic when enough

## Named Data Structures
- Prefer dataclass/NamedTuple over tuple[...] for return types
- Minimize type proliferation: reuse existing types, consolidate similar shapes
- Bad: `def calc() -> tuple[float, float]:`
- Good:
  ```python
  @dataclass
  class CalcResult:
      real_value: float
      equity: float
  ```
- Skip for trivial cases or test code where overhead isn't justified

## Datetime
- `datetime.fromtimestamp(ts, tz=timezone.utc)` not `utcfromtimestamp`

## Style
- Never modify `sys.path` from scripts
- Use `.get()` for dict existence checks

## Build
- uv for package management, pyright for type checking
- pre-commit: ruff format + lint, end-of-file-fixer, trailing-whitespace
- `make right`: pyright only (run manually, not in pre-commit)
- `make test`: pytest

## Testing
- Test files: `test_*.py` next to code
- Testcontainers: centralize in `conftest.py`
- ALWAYS use `python -m pytest` not `pytest` directly (ensures proper package discovery)
- Set PYTHONPATH once at Makefile top, not per target

## Subprocesses
- `start_new_session=True` on `create_subprocess_exec` (prevents Ctrl-C leaking to children)
- Kill process groups: `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)`
