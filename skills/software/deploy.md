# Deployment

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

## Per-deployable subdir layout

Every deployable (long-running service or cron timer) lives in its own
subdir at the repo root. Each subdir is **self-contained**:

```
<repo>/
  Makefile               # repo-wide aggregation (optional)
  pyproject.toml         # the library, if any
  <library-pkg>/         # importable package
  lib/                   # shared seam (if applicable)
  tests/

  <deployable-1>/
    Makefile             # prepare/build/test/right/image/clean
    Dockerfile           # python:3.13-slim + uv two-layer
    pyproject.toml       # OWN deps, not the library's
    main.py              # entrypoint expected by docker-service smart entry
    tests/               # OWN tests, run independently
    README.md

  <deployable-2>/
    ... same shape
```

- A subdir's image name = the subdir name in dashes (`my-service`).
  Systemd unit name derives via dash → underscore (`my_service`).
- Subdir's `pyproject.toml` lists ONLY what its `main.py` needs. Don't
  drag the library's deps into a downloader, and vice versa.
- A subdir does NOT import from the parent library unless it really
  shares runtime code. Inline tiny helpers (e.g. `os.getenv('PREFIX')`)
  rather than depend on lib for one function.
- Each deployable has its OWN test suite under `<subdir>/tests/`. Repo
  root tests cover the library; each subdir's tests cover that
  deployable. Don't pollute one with the other.
- Build context for a subdir's Dockerfile is the subdir itself. Each
  image is independently buildable: `cd <subdir> && make image`.
- Repo root `pyproject.toml` excludes deployable dirs from its test
  discovery: `addopts = "--ignore=<deployable-1> --ignore=<deployable-2>"`.

This is what core's ansible/CLAUDE.md describes from the deployment side
(image per service, systemd unit per image). The per-subdir code layout
is the upstream half of the same pattern: code is colocated with its
deployment unit so you can reason about each in isolation and they
evolve independently.
