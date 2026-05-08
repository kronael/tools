---
name: ops
description: DevOps and deployment. Dockerfile, systemd, GitHub Actions, monitoring, Ansible. NOT for app code (use language skill).
when_to_use: Dockerfile, docker-compose, systemd services, GitHub Actions CI, Ansible playbooks, monitoring setup, PID files
---


# Ops

## Docker

- ALWAYS pin image versions (NEVER :latest)
- ALWAYS multi-stage if intermediate layers >100MB
- ENTRYPOINT for production, CMD for development
- Layer order: base+system deps -> lang deps (Cargo.toml, requirements.txt) -> fetch deps -> copy source -> build
- Cross-compilation: volume mount source, NEVER copy
- ALWAYS set memory limits (2GB typical) and build timeout (30m)

### Python + uv Dockerfile pattern (standalone repo)

Two-layer image for max cache hit. Layer 1 is deps only (changes
infrequently); layer 2 is source (changes every push):

```dockerfile
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PREFIX=/srv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN apt-get update -yy \
  && apt-get install -yy --no-install-recommends \
        build-essential ca-certificates curl \
  && curl -LsSf https://astral.sh/uv/install.sh | sh \
  && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /srv/app/<NAME>

# Layer 1: deps only — re-runs only when pyproject.toml/uv.lock change.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Layer 2: source.
COPY <pkg>/ <pkg>/
COPY lib/  lib/
RUN uv sync --frozen --no-dev

ENTRYPOINT ["uv", "run", "<console-script>"]
CMD ["--help"]
```

- `--no-install-project` keeps layer 1 deps-only; the second `uv sync`
  in layer 2 installs the project (cheap because deps are already there).
- ALWAYS ship `.dockerignore` excluding `.git`, `.diary`, `.ship`,
  `__pycache__`, `tmp`, `docs`, `specs`, all `*.md` except `README.md`.
- ALWAYS use `python:3.13-slim` (or pinned current); NEVER `python:latest`.

### Python + uv inside a monorepo (m4 template)

When many sibling components share `lib/`, generate Dockerfiles from
`m4/Dockerfile.m4` rather than maintaining one each. Pattern:

```makefile
Dockerfile: ../m4/Dockerfile.m4
	m4 -D NAME=$(name) ../m4/Dockerfile.m4 > Dockerfile

image: Dockerfile
	cd ..; docker build -t $(name) -f $(name)/Dockerfile .
```

Build context is the monorepo root so `lib/` is COPY-able. Dockerfile
sets `WORKDIR /srv/app/<repo>/NAME`.

## Configuration

- Three-level: base TOML -> env.toml (`${PREFIX:-/srv}/key/env.toml`) -> env vars
- Secrets in /srv/key/env.toml (NOT committed), chmod 600 for keypairs

## Logging

- Format: `Mon DD HH:MM:SS.fff [LEVEL] message key=value`
- CRITICAL prefix for monitoring alerts
- Log rotation via logrotate (not in app)
- RUST_LOG: `info` (prod), `debug` (dev), `module::path=debug,info` (selective)

## Monitoring

- Heartbeat: ./tmp/<service>.heartbeat
- Health: /.well-known/live, Metrics: /metrics (Prometheus)
- Prometheus labels: NEVER unbounded values, ONLY bounded enums. High cardinality -> logs.

## Error Handling

- Hierarchy: ApplicationError, InfrastructureError, DomainError
- Exponential backoff: 100ms...1600ms, ONLY retry transient errors
- Alert on >10 persistent failures

## Storage

- Config: `${PREFIX:-/srv}/key/`, Runtime: `${PREFIX:-/srv}/run/`, Data: `${PREFIX:-/srv}/data/<project>/`

## Anti-Patterns

- Use EWMA (not sliding windows) for window calculations
- NEVER manually .close() async context managers

## Ansible docker-service Role

- Containers MUST have `./main` or `python -m main`
- Entrypoint: `[[ -x ./main ]] && exec ./main $args $cfg || exec python -m main $args $cfg`
- Service names: underscores (`funding_report`), image names: dashes (`funding-report`)
- `--network=host` (no port mapping), config: `/cfg/<server>/<service>.toml`
- Volumes: `/srv/spool/<name>` (persistent), `/srv/run/<name>` (runtime)

```yaml
service:
  - image: my-service              # Long-running
  - image: my-timer                # Cron timer
    minute: "*/5"
    timeout: 600
  - image: my-calendar             # Calendar timer
    oncalendar: "daily"
```

## CI/CD

- ALWAYS explicit make targets: `make prepare`, `make image`, `make test`
- NEVER run release builds locally, mix debug/release artifacts

## Makefile pattern for Python + uv

Standard targets — names are universal across projects so muscle memory works:

```makefile
name = <project>

.PHONY: help prepare build test right lint image clean

help:
	@echo "    prepare    install deps"
	@echo "    test       run tests"
	@echo "    right      type-check (pyright)"
	@echo "    lint       ruff lint"
	@echo "    image      build docker image"
	@echo "    clean      remove caches"

prepare:
	uv sync --group dev

build:  # no build step, interpreted python

test:
	uv run python -m pytest tests/

right:
	uvx pyright <pkg> tests

lint:
	uvx ruff check <pkg> tests

image:
	docker build -t $(name) .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf dist build
```

- ALWAYS the target name `right` (not `pyright`) — short, fast to type.
- ALWAYS `python -m pytest`, never bare `pytest` (package discovery).
- ALWAYS `uvx <tool>` for type-checkers and linters, NOT `uv run <tool>`.
  uvx pulls the tool independent of dev deps, so `make right` works after
  a fresh checkout without first running `uv sync --group dev`.
- Universal target names: `prepare`, `build`, `test`, `right`, `lint`,
  `image`, `clean`. `build` stays as a documented no-op for interpreted
  Python so cross-language CI calls `make build` uniformly.
- For monorepo components, set PYTHONPATH per-target (`PYTHONPATH=../lib/src:src`).
  For standalone repos, `uv sync` installs the project itself; PYTHONPATH
  is unnecessary.

## Distributable Python tools — single-file uvx scripts when possible

For tools that fit, prefer a **single-file PEP 723 script** with inline
`/// script` metadata. `uvx` runs it with no clone, no install, no entry
points:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click", "httpx"]
# ///
import click

@click.command()
def main(): ...

if __name__ == '__main__':
    main()
```

Run anywhere: `uv run https://example.com/script.py` or
`uvx --from <raw-url>`. No `pyproject.toml`, no Docker, no package
ceremony. Use this whenever a tool fits comfortably in one file —
reach for a package layout only when justified.

### Use a package layout when ANY apply

- multiple modules with cross-imports
- bundled non-Python assets (templates, fixtures)
- own test suite
- shared internal lib with sync seam
- intended for `pip install` / pinning

```toml
[project.scripts]
mytool = "mytool.mytool:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["mytool", "lib"]
```

Run from anywhere off GitHub:
```
uvx --from git+https://github.com/<owner>/<repo> mytool ...
```

- The CLI module name conventionally matches the package name
  (`mypkg/mypkg.py:main`) so `uvx mypkg` lines up cleanly.
- Local dev: `uvx --from . mytool ...` reproduces the github flow.
- Bundle assets inside the package dir — hatchling picks them up via
  `packages = [...]`.

## Makefile pattern for Python + uv

Standard targets. Names are universal across projects so muscle memory works:

```makefile
name = <project>

.PHONY: help prepare build test right lint image clean

help:
	@echo "    prepare    install deps"
	@echo "    test       run tests"
	@echo "    right      type-check (pyright)"
	@echo "    lint       ruff lint"
	@echo "    image      build docker image"
	@echo "    clean      remove caches"

prepare:
	uv sync --group dev

build:  # no build step, interpreted python

test:
	uv run python -m pytest tests/

right:
	uv run pyright <pkg> tests

lint:
	uv run ruff check <pkg> tests

image:
	docker build -t $(name) .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf dist build
```

- ALWAYS the target name `right` (not `pyright`) — short, fast to type,
  used across the codebase. `make right` runs pyright.
- ALWAYS `python -m pytest`, never bare `pytest` (package discovery).
- Universal targets: `prepare`, `build`, `test`, `right`, `lint`, `image`,
  `clean`. `build` stays as a documented no-op for interpreted Python so
  cross-language pipelines call `make build` uniformly.
- For monorepo components, set PYTHONPATH per-target (`PYTHONPATH=../lib/src:src`).
  For standalone repos, `uv sync` installs the project itself; PYTHONPATH
  is unnecessary.

## Distributable Python tools — prefer single-file uvx scripts

For tools that fit, a **single-file PEP 723 script** with inline
`/// script` metadata is preferable to a full package — `uvx` runs it
directly with no clone, no install, no entry-point ceremony:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click", "httpx"]
# ///
import click

@click.command()
def main():
    ...

if __name__ == '__main__':
    main()
```

Run anywhere: `uvx --from <url-to-raw-file>` or
`uv run https://example.com/script.py`. No `pyproject.toml`, no `lib/`,
no Docker. Use this whenever a tool fits comfortably in one file —
don't reach for a package layout you don't need.

### When to use a package layout instead

Use a `[project]`-style package only when at least one applies:

- multiple modules with cross-imports
- bundled non-Python assets (templates, fixtures)
- tests
- shared internal lib
- intended for `pip install` / pinning

```toml
[project.scripts]
mytool = "mytool.mytool:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["mytool", "lib"]
```

Then anywhere:

```
uvx --from git+https://github.com/<owner>/<repo> mytool ...
```

- CLI module name conventionally matches the package name
  (`mypkg/mypkg.py:main`) so `uvx mypkg` lines up cleanly.
- For local dev: `uvx --from . mytool ...` reproduces the github flow.
- Bundle assets inside the package dir — hatchling picks them up via
  `packages = [...]`.
