---
name: builder
description: Build tool patterns. Use when writing Dockerfiles, Makefiles, CI/CD, cross-compilation.
---

# Builder/Build Tools

## Docker Build Patterns

- ALWAYS use multi-stage builds for layer caching
- Base stage: dependencies and system packages
- Build stage: compilation and asset generation
- Final stage: runtime only (minimal size)
- NEVER copy source in base layer (breaks cache on every change)

## Cross-Compilation

- Use Docker for cross-platform builds (pyinstaller-windows pattern)
- Mount source as volume: `-v $(pwd):/src`
- Output to shared volume: `-v $(pwd)/dist:/dist`
- Build once, use everywhere (consistent environment)

## Make Integration

- `make image`: Build Docker image
- `make build`: Build inside container
- Parent deploy scripts call child Makefiles (ansible pattern)

## Pre-commit Hooks

- Configuration in .pre-commit-config.yaml
- Multi-project support: check only changed projects (pre-commit-rust)

## Build Artifacts

- ALWAYS output to ./dist or ./target
- ALWAYS gitignore build directories
- Clean target removes all generated files
