# Docker runbooks

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
