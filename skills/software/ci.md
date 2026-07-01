# CI / Makefile

## Makefile pattern for Python + uv

Standard targets — names are universal across projects so muscle memory works:

```makefile
name = <project>

.PHONY: help prepare build test right image clean

help:
	@echo "    prepare    install deps"
	@echo "    test       run tests"
	@echo "    right      type-check (pyright)"
	@echo "    image      build docker image"
	@echo "    clean      remove caches"

prepare:
	uv sync --group dev

build:  # no build step, interpreted python

test:
	uv run python -m pytest tests/

right:
	uvx pyright <pkg> tests

image:
	docker build -t $(name) .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf dist build
```

- ALWAYS the target name `right` (not `pyright`) — short, fast to type.
- ALWAYS `python -m pytest`, never bare `pytest` (package discovery).
- ALWAYS `uvx <tool>` for type-checkers, NOT `uv run <tool>`. uvx pulls
  the tool independent of dev deps, so `make right` works after a fresh
  checkout without first running `uv sync --group dev`.
- NEVER add a `lint` target. Linting (ruff, etc.) belongs in pre-commit
  — running it from `make` duplicates work and creates a second source
  of truth for which checks must pass.
- Universal target names: `prepare`, `build`, `test`, `right`, `image`,
  `clean`. `build` stays as a documented no-op for interpreted Python
  so cross-language CI calls `make build` uniformly.
- For monorepo components, set PYTHONPATH per-target (`PYTHONPATH=../lib/src:src`).
  For standalone repos, `uv sync` installs the project itself; PYTHONPATH
  is unnecessary.

## `make demo` targets

`demo` MUST use proper file targets with real prerequisites, e.g.:

```makefile
demo: tmp/demo.gif

tmp/demo.cast: $(BIN) demo/script
	...

tmp/demo.gif: tmp/demo.cast
	...
```

Output goes in `tmp/` (never committed). NEVER flatten into one phony
target — Make must be able to skip the recording if the cast is fresh and
only re-render the gif.
