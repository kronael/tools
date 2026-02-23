# dockbox

Dockerized Claude Code with isolated filesystem access.

## Build

```bash
make image              # builds with your UID
make image UID=1001     # custom UID
```

The container user `claude` is created with your UID so mounted files
remain accessible with correct permissions.

## Install

```bash
make install            # installs dockbox to /usr/local/bin
```

## Usage

```bash
dockbox                           # current dir, runs claude
dockbox ~/wk/project              # mount project, runs claude
dockbox ~/wk/p1 ~/wk/p2           # mount multiple dirs
dockbox . -- bash                 # run bash instead
dockbox . -- claude --help        # pass args to claude
```

## Mounts

Automatic:
- `~/.claude` -> `/home/claude/.claude` (rw) - credentials and runtime data
- `~/.claude.json` -> copied at startup (fallback creates minimal file)
- `~/.dockbox_history` -> `/home/claude/.zsh_history` (rw)

Project dirs are mounted at exact paths with read-write access.

## Authentication

Uses `~/.claude/.credentials.json` from host (via the mounted `~/.claude` directory).

## Included Tools

- claude, codex, pi (AI coding agents)
- go (via g version manager)
- rust (via rustup)
- node (npm, pnpm, bun, nvm)
