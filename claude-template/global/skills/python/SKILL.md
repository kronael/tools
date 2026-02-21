---
name: python
description: Python development. .py files, pyproject.toml, pytest, aiohttp, FastAPI, asyncpg, dataclass, async/await, type annotations.
---

# Python

## Type Annotations
- `dict[str, float]` not `Dict[str, float]`
- `list[str]` not `List[str]`
- `Type | None` not `Optional[Type]`
- Be concrete: `list[dict]` or `-> list:` is not acceptable when `list[Row]` or `list[Fill]` is trivial

## Async
- ALL code is single-threaded asyncio — NEVER use threads
- Exception: wrapping blocking external libraries with no async alternative
- If threads exist, project CLAUDE.md must document where and why
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

## Logging
- `log = logging.getLogger(__name__)` at module level, or `WithLogger` mixin for classes
- ALWAYS name the variable `log`

## Style
- Never modify `sys.path` from scripts
- Use `.get()` for dict existence checks
- NEVER use `contextlib.suppress` — use `try/except/pass` (simpler, clearer)

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
