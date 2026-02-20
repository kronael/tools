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
- ALWAYS use dataclasses for structured return/input types, not raw tuples
- Raw tuples ok only in tests and obvious 2-field cases (`(x, y)`, `(key, val)`)
- Reuse existing types; don't proliferate similar shapes

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
