---
name: python
description: Python development patterns. Use when working on .py files, pyproject.toml, or Python projects.
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

## Testing
- Test files: `test_*.py` next to code
- Testcontainers: centralize in `conftest.py`
- ALWAYS use `python -m pytest` not `pytest` directly (ensures proper package discovery)
- Set PYTHONPATH once at Makefile top, not per target
