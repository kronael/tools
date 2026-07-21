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

## install: `go install ...trufflehog/v3@latest` fails (replace directives)

`kronael/install/SKILL.md` step 6 security-audit table installs `trufflehog`
via `go install github.com/trufflesecurity/trufflehog/v3@latest`. That fails:
its `go.mod` contains `replace` directives, so `go install` refuses ("must not
contain directives that would cause it to be interpreted differently than if
it were the main module"). Fix: install the release binary like gitleaks —
`linux_amd64.tar.gz` from github.com/trufflesecurity/trufflehog/releases into
`~/.local/bin`. Found 2026-07-21 during a full "install all tools" run; worked
around with the release binary (v3.95.9) so the install completed.
