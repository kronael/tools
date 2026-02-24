# dockbox

Dockerized Claude Code with isolated filesystem access.

## Build

```bash
make image              # builds with your UID and TZ
make image UID=1001     # custom UID
make image TZ=EST       # custom timezone (default: host TZ or UTC)
```

The container user `claude` is created with your UID so mounted files
remain accessible with correct permissions.

## Install

```bash
make install            # installs dockbox to ~/.local/bin
make clean              # remove binary and docker image
```

## Usage

```bash
dockbox                           # current dir, claude in zsh
dockbox -s nu ~/wk/project        # claude in nushell
dockbox ~/wk/p1 ~/wk/p2           # mount multiple dirs
dockbox -n mybox .                 # custom container name
dockbox . -- bash                  # run command directly (no claude)
```

Default: auto-launches claude, drops to shell on exit. The container
stays alive after claude exits. Use `-s` to pick shell (zsh/bash/nu),
`--` to skip claude and run a command directly.

## Configuration

Extra docker args via `.dockboxrc` files (one arg per line, `#` comments):

- `~/.dockboxrc` — global defaults (e.g. `--gpus all`)
- `.dockboxrc` in project dir — per-project overrides

Both are optional. Global applies first, project appends. The
project `.dockboxrc` is overmounted with `/dev/null` inside the
container so the boxed agent can't modify it.

## Mounts

Automatic:
- `~/.claude` -> `/home/claude/.claude` (rw) - credentials and runtime
- `~/.claude.json` -> copied at startup (fallback creates minimal file)
- `~/.gitconfig` -> `/home/claude/.gitconfig` (ro)
- `~/.dockbox_history` -> `/home/claude/.zsh_history` (rw)
- `/etc/localtime` -> `/etc/localtime` (ro)

Project dirs are mounted at exact paths with read-write access.

## Authentication

Uses `~/.claude/.credentials.json` from host (via mounted `~/.claude`).

## Permissions

All Claude Code permissions are bypassed inside the container
(`--dangerously-skip-permissions`). The container itself is the sandbox.

## Included Tools

- claude, codex, pi (AI coding agents)
- go (via g version manager)
- rust (via rustup)
- python (via uv)
- java/kotlin (via sdkman)
- nushell (via cargo)
- node (npm, pnpm, bun, nvm)
