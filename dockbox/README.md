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
dockbox                           # current dir, runs claude
dockbox ~/wk/project              # mount project
dockbox ~/wk/p1 ~/wk/p2           # mount multiple dirs
dockbox -n mybox .                # custom container name
dockbox -e bash .                 # run bash instead
dockbox -c                        # continue session
dockbox ls                        # list dockbox containers
dockbox rm [pattern]              # remove containers
dockbox prune [hours]             # remove exited containers older than N hours (default: 2160)
```

Default command: claude. Use `-e` to override.

## Configuration

Extra docker args via `.dockboxrc` files (bash-style, `#` comments):

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
- `gpg-agent socket` -> same path inside container
- `~/.gnupg/pubring.kbx` -> `/home/claude/.gnupg/pubring.kbx` (ro)
- `~/.dockbox_history` -> `/home/claude/.zsh_history` (rw)
- `/etc/localtime` -> `/etc/localtime` (ro)
- `/tmp/capture.png` -> `<workdir>/capture.png` (ro)

Project dirs are mounted at exact paths with read-write access.

## Authentication

Uses `~/.claude/.credentials.json` from host (via mounted `~/.claude`).

## Permissions

All Claude Code permissions are bypassed inside the container
(`--dangerously-skip-permissions`). The container itself is the sandbox.

## Cookbook

### Screenshot sharing

Host `/tmp/capture.png` is auto-mounted as `capture.png` in the
project root. Bind a hotkey on your host to capture:

```bash
maim -s /tmp/capture.png    # mouse-select region (Arch: pacman -S maim)
```

Then in dockbox Claude, reference `capture.png` — it auto-attaches.

### Share a host file

Add to `~/.dockboxrc`:

```
-v /tmp/data.csv:/tmp/data.csv:ro
```

### GPU passthrough

```
--gpus all
```

## Included Tools

- claude, codex, pi (AI coding agents)
- go (via g version manager)
- rust (via rustup)
- python (via uv)
- java/kotlin (via sdkman)
- nushell (prebuilt binary)
- node (npm, pnpm, bun, nvm)
