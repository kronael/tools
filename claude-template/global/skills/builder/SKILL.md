---
name: builder
description: Build tool patterns. Use when writing Dockerfiles, Makefiles, CI/CD, cross-compilation.
---

# Builder

**TL;DR**: Debug builds default, release only via CI. Docker layers cache
deps before source. Volume mount for cross-compilation. Fail-fast, clean
before retry. Non-workspace Rust requires independent scanning.

## Make Targets

ALWAYS use standard make targets for builds:

```makefile
build-dev           # Debug build (default target)
build               # Release build (via CI only)
image               # Docker image build
prepare             # Install dependencies
clean               # Remove artifacts
```

**Conventions**:
- ALWAYS default to debug builds in development
- NEVER use release builds directly (only via `make image` or CI)
- ALWAYS separate `make image` from source building
- ALWAYS fail-fast on first error

## Docker Build Patterns

### Base Images

- ALWAYS pin version explicitly (ubuntu:22.04, rust:1.75, python:3.12)
- NEVER use :latest or unversioned tags
- ALWAYS use multi-stage if intermediate layers >100MB

### Layer Caching

ALWAYS optimize for cache reuse. Order:
1. Base image + system deps
2. Language deps (Cargo.toml, requirements.txt, package.json)
3. Install/fetch dependencies
4. Copy source
5. Build

```dockerfile
# CORRECT - deps before source
COPY Cargo.toml Cargo.lock ./
RUN cargo fetch
COPY src ./src
RUN cargo build --release

# WRONG - source changes invalidate deps
COPY . .
RUN cargo build --release
```

### Entrypoints

- ALWAYS use ENTRYPOINT for production (fixed binary)
- ALWAYS use CMD for development (allow override)

```dockerfile
ENTRYPOINT ["/app/service"]
CMD ["--config", "/etc/config.toml"]  # Default args
```

## Cross-Compilation

ALWAYS use volume mounts, NEVER copy source:

```bash
# CORRECT - mount source as volume
docker run -v $(pwd):/src builder make -C /src build
```

**Separation**: Image has tools, compilation uses mounted source. Build
image once, reuse across projects. Source changes don't invalidate tool
installation.

## Non-Workspace Rust Projects

ALWAYS scan independently, NEVER assume workspace.members:

```bash
# CORRECT - find all Cargo.toml independently
find . -name Cargo.toml -type f
```

Repos with multiple disconnected Rust projects need per-project scanning.
Each has own Cargo.toml, no workspace umbrella.

## Build Caching

**Docker**: Pin versions, run package manager before copying source. Source
changes never invalidate tool installation.

**Pre-commit**: Tools cached in container/venv. New project = full scan
(one-time), subsequent runs use cache.

## Failure Modes

### Partial Builds

- NEVER continue after first error
- ALWAYS report which component failed
- ALWAYS clean state before retry
- NEVER assume idempotent (explicitly clean first)

### Resource Exhaustion

- ALWAYS set Docker memory limits (2GB typical)
- ALWAYS set build timeout (30m default)
- ALWAYS scan selectively if too many files
- NEVER let builds run unbounded

**Example**:
```bash
docker build --memory 2g --memory-swap 2g .
timeout 30m make build
```

## Build Separation

ALWAYS separate: image building (tools), source compilation (build),
dependency installation (prepare), cleanup (clean).

Parent project calls builder via make/script. Builder handles
packaging/tooling only. Source changes stay in source project.

## When to Extract a Builder

Consider separate builder if:
- Used by 3+ projects
- Multi-stage pipeline (prepare → build → package)
- Custom Docker image required
- Cross-platform compilation needed
- Non-obvious build requirements (Wine, cross-compilation, etc)

Otherwise keep build logic in project Makefile.

## Development Workflow

```bash
# One-time setup
make prepare          # Install deps (pipenv, cargo, npm)
make image            # Build Docker image with tools

# Iterative development
make build-dev        # Debug build (fast, better errors)
make test             # Fast unit tests
make smoke            # Full integration tests

# Release (CI only)
make image            # Rebuilds with make build (release)
```

## CI/CD Integration

ALWAYS use explicit targets in CI:

```yaml
# GitHub Actions example
- run: make prepare
- run: make image
- run: make test
```

NEVER:
- Run release builds locally
- Skip clean before CI build
- Assume cached state in CI
- Mix debug and release artifacts
