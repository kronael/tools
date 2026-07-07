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

## install: `uv tool install faster-whisper` fails (no CLI entrypoint)

`kronael/install/SKILL.md` step 6 lists `faster-whisper` under "Video
rendering" with `uv tool install faster-whisper`. That fails: faster-whisper
is a **library**, not a CLI — `uv tool` reports "No executables are provided
by package `faster-whisper`; removing tool". The /create video-render skill
uses it as a library (likely `uv run --with faster-whisper`), so a global
tool install is both wrong and unnecessary. Fix: drop the row, or replace with
a CLI wrapper like `whisper-ctranslate2` if a binary is actually wanted.
Found 2026-07-07 during a full "install all tools" run.
