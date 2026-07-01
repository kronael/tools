# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## (resolved) dockbox: `-D` docker socket unusable after gosu drop

[resolved 2026-06-13] Fix: `dockbox-init` now (1) adds the runtime user to
each `--group-add` supplementary gid in `/etc/group`, and (2) drops with
`gosu "$USERNAME"` (by name) instead of numeric `uid:gid` — numeric specs
skip `initgroups`, so supplementary groups were silently dropped. Verified on
a fresh image: `groups=…,964` + socket read/write OK with `dockbox -D`.

While fixing, two latent cold-build breakers in `dockbox/Dockerfile` were also
fixed: `uv tool install` was given four packages at once (takes one per call),
and gitleaks was pinned to a nonexistent `v9.1.0`/`amd64` (now `8.30.1`/`x64`
with a fail-fast download). These only surfaced once the build cache went cold.
