# dockbox

A sandbox you actually use — full credentials, no permission prompts, mounts
whatever you point at. Docker provides working directory scoping and a clean
environment. The boxed agent has full access to your tools, config, and
credentials — treat it as yourself in a container.

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
dockbox ~/wk/p1 ~/wk/p2           # mount multiple dirs, work in last
dockbox -v ~/wk/lib               # extra mount at same path (ro, default)
dockbox -v ~/wk/lib:rw            # extra mount at same path (rw)
dockbox -n mybox .                # custom container name
dockbox -e bash .                 # run bash instead
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
- `~/.claude` -> `/home/claude/.claude` (rw) - credentials, skills, settings
- `~/.claude.json` -> copied at startup (fallback creates minimal file)
- `~/.gitconfig` -> `/home/claude/.gitconfig` (ro)
- `gpg-agent socket` -> `/home/claude/.gnupg/S.gpg-agent`
- `~/.gnupg/pubring.{kbx,gpg}` -> `/home/claude/.gnupg/` (ro)
- `~/.dockbox_history` -> `/home/claude/.zsh_history` (rw)
- `/etc/localtime` -> `/etc/localtime` (ro)
- `/tmp/capture.png` -> `<workdir>/capture.png` (ro)

Project dirs are mounted at exact paths with read-write access.

`~/.claude` is rw so the boxed agent can update skills, settings, and
memory just like a normal session. This is intentional — treat the
container as a full peer that should continuously improve shared config.

## Authentication

Uses `~/.claude/.credentials.json` from host (via mounted `~/.claude`).

## Permissions

All Claude Code permission prompts are bypassed two ways: `bypassPermissions`
mode injected via `settings.local.json`, and `--dangerously-skip-permissions`
passed by the `claude` wrapper in the image. This is intentional — the use
case is a trusted agent doing real work, not untrusted code execution. If you
need security isolation, this is not the tool.

## Cookbook

### Screenshot sharing

Host `/tmp/capture.png` is auto-mounted as `capture.png` in the
project root. Bind a hotkey on your host to capture:

```bash
maim -s /tmp/capture.png    # mouse-select region (Arch: pacman -S maim)
```

Then in dockbox Claude, reference `capture.png` — it auto-attaches.

### Share a host file

```bash
dockbox -v /tmp/data.csv ~/wk/project    # mounts at same path, ro
```

### GPU passthrough

```
--gpus all
```

## Included Tools

- claude, codex, pi (AI coding agents)
- agent-browser (headless browser automation via Playwright/Puppeteer)
- go (via g version manager)
- rust (via rustup)
- python (via uv)
- java/kotlin (via sdkman)
- nushell (prebuilt binary)
- node (npm, pnpm, bun, nvm)
