# Builder/Build Tool Patterns

Build tools, Docker builders, and compilation automation across projects.

## Projects

### pyinstaller-windows
**Location**: `/home/ondra/wk/morha/pyinstaller-windows`
**Purpose**: Cross-compile Python to Windows .exe from Linux
**Lang**: Dockerfile + Makefile + Bash

**Architecture**:
- Dockerfile: Wine + Python 3.12 + PyInstaller
- Make targets: `prepare` (install pipenv), `image` (build Docker), `install` (legacy)
- Integration: Called via `deploy client-exe` from parent project
- Output: `core/client/dist/` directory

**Key Patterns**:
- Mounted source directory (`/src/core`)
- Inside container: `make -C /src/core/client exe`
- Build separation: image building separate from source compilation
- Single responsibility: Only handles exe packaging, not source build

**Wisdom**:
- Integration via parent deploy script, not standalone execution
- Prepares dependencies locally before image build
- One-time pipenv setup in container
- Non-idempotent: requires clean before rebuild

**Make Targets**:
```makefile
prepare         # Install pipenv and dependencies locally
image           # Build Docker image with PyInstaller
install         # Obsolete (use deploy client-exe)
```

### pre-commit-rust
**Location**: `/home/ondra/wk/trading/pre-commit-rust`
**Purpose**: Pre-commit hooks for Rust (fmt, check, clippy)
**Lang**: Shell + pre-commit config

**Architecture**:
- Handles multiple DISCONNECTED Rust projects in single repo
- NOT workspace-aware (key difference)
- Each project directory scanned independently
- Runs cargo tools with project-specific flags

**Key Patterns**:
- Works with non-workspace repos (nested arbitrary structures)
- Per-project Cargo.toml resolution
- Avoids monorepo assumptions
- Fail-fast on any error

**Wisdom**:
- Critical for repos with mixed Rust projects
- Don't assume workspace.members (won't work)
- Must locate root of each project independently
- Respects project-specific configurations (Cargo.toml, clippy.toml)

## Shared Patterns

### Make Integration
All builders use `make` for development operations:

```makefile
make build-dev      # Debug build (development)
make build          # Release build (production only via make image)
make image          # Build Docker image
make prepare        # Install dependencies
make clean          # Remove artifacts
```

**Convention**:
- Default target: debug build
- Release builds: Only via explicit CI/container targets
- Image building: Separate `make image` target
- Development: Never use release builds directly

### Configuration Management

**TOML First**:
- Static config: TOML passed as CLI arg
- Secrets: Optional `/srv/key/env.toml` override
- Environment: Optional env var overrides
- Validation: On-load checking, fail fast

**Path Conventions**:
- Data: `${PREFIX:-/srv}/data/<project_name>/`
- Logs: `./log/` (development only)
- Config: `../cfg/<environment>/`

### Docker Patterns

**Dockerfile Checklist**:
- Base image explicit (version pinned)
- Multi-stage if >100MB intermediate
- Clean layers for cache efficiency
- ENTRYPOINT for production, CMD for dev override

**Build Integration**:
- `make image` builds via docker build
- Mount source as volume for development
- Separate build-time and run-time configs
- Cache between builds (layer reuse)

### Logging

**Production Logging**:
- Structured: key=value pairs
- Levels: error, warn, info, debug
- Format: Unix timestamp with milliseconds
- No fancy colors (plain text for logs)

**Development Logging**:
- Allowed to be verbose with debug builds
- RUST_LOG/PYTHONPATH env variables
- Temporary logs in `./log/` directory

## Development Workflow

### Local Development
```bash
cd pyinstaller-windows
make prepare          # Install deps
make image            # Build Docker image
cd ../client          # Go to source project
make exe              # Runs inside Docker
```

### CI/CD Integration
```bash
# From project root (parent deploy script)
deploy client-exe     # Calls pyinstaller-windows + client build
```

### Adding New Builder

1. **Identify builder type**: Docker, pre-commit, Make-based, etc.
2. **Create Makefile** with targets: prepare, build, image, clean
3. **Isolate dependencies**: Use containers or virtual envs
4. **Document integration point**: How parent projects call it
5. **Version pin everything**: Docker base images, tool versions
6. **Add to BUILDERS.md**: Reference in this doc

## Non-obvious Insights

### Cross-compilation Considerations

**Windows EXE building**:
- Wine adds latency (wine startup ~2s per invocation)
- Caching: Build image once, reuse across projects
- Volume mount source, NOT copy (faster iteration)

**Multiple disconnected projects**:
- pre-commit-rust must NOT assume workspace structure
- Scan with find instead of workspace.members
- Handle errors per-project, not global

### Build Caching

**Docker layer caching**:
- Keep Dockerfile stable (pin base images)
- RUN pip/cargo before copying sources
- Changes to source don't invalidate tool installation

**Pre-commit caching**:
- Tools cached in container
- New project = full scan (one-time cost)

### Failure Modes

**Partial builds**:
- Don't continue after first error
- Report which project failed
- Clean state before retry

**Resource exhaustion**:
- Docker: Set memory limits (2GB typical)
- Build: Set timeout (30m default)
- Pre-commit: Scan selectively if too many files

## When to Extract a Builder

Consider separate builder.md documentation if:
- Used by 3+ projects
- Multi-stage pipeline (prepare → build → package)
- Non-obvious build requirements
- Custom Docker image
- Cross-platform complexity

## See Also

- INFRASTRUCTURE.md - Deployment and ops tools
- CLI.md - Command-line tools and entrypoints
- Global CLAUDE.md - Development principles
