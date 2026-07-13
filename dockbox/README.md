# dockbox

A sandbox that is actually useful — full credentials, no permission prompts,
mounts whatever you point at. Docker provides working directory scoping and a clean
environment. The boxed agent has full access to your tools, config, and
credentials — treat it as yourself in a container.

## Build

```bash
make image              # builds the (UID-agnostic) image with host TZ
make image TZ=EST       # custom timezone (default: host TZ or UTC)
```

The image has no baked user. At runtime, dockbox passes your host UID/GID
to the container and `dockbox-init` registers you in `/etc/passwd` before
dropping privilege. One image works for every host user — alice, bob, ondra
can share it.

Tools (cargo, nvm, bun, rustup, sdkman, go, uv, nushell, etc.) live in
`/opt/dev-tools/` inside the image, world-readable. Each runtime user gets
a fresh tmpfs `$HOME` at `/home/dockbox` with bind mounts (`~/.claude`,
`~/.gitconfig`, etc.) nested in.

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
dockbox -P                        # persist host build dirs (no overmount)
dockbox -T                        # tmpfs backend for ephemeral dirs
dockbox -e GH_TOKEN               # forward env var into container
dockbox -n mybox .                # custom container name
dockbox -x bash .                 # run bash instead
dockbox ls                        # list dockbox containers
dockbox rm [pattern]              # remove containers
dockbox prune [hours]             # remove exited containers older than N hours (default: 2160)
```

Default command: claude. Use `-x` to override.

### Re-entry into a running box

If a dockbox for the project is already running, the next `dockbox`
invocation enters that live container (`docker exec`) and runs the
requested command there, rather than starting a second one:

```bash
dockbox ~/wk/project    # starts the box, runs claude
dockbox sh              # 2nd terminal: shell inside the same box
dockbox codex           # 3rd terminal: codex inside the same box
```

The entered session shares the container's `HOME`, mounts, and
processes, and runs as your host user (not root). The **command** —
tool, `--model`, `--effort`, args — takes effect, and **env flags**
(`-e`, `-g`) are forwarded into the session, so a box first started
without `-g` still gets the token when a later `dockbox -g` re-enters
it. **Mount/network flags** (`-v`, `-H`, `-D`) do not apply — they're
fixed when the container is created. Use `-n <name>` to force a
separate, fully-provisioned container instead.

## Configuration

Extra docker args via `.dockboxrc` files (bash-style, `#` comments):

- `~/.dockboxrc` — global defaults (e.g. `--gpus all`)
- `.dockboxrc` in project dir — per-project overrides

Both are optional. Global applies first, project appends. The
project `.dockboxrc` is overmounted with `/dev/null` inside the
container so the boxed agent can't modify it.

## Mounts

Automatic:
- `~/.claude` -> `/home/dockbox/.claude` (rw) - credentials, skills, settings
- `~/.claude.json` -> copied at startup (fallback creates minimal file)
- `~/.gitconfig` -> `/home/dockbox/.gitconfig` (ro)
- `gpg-agent socket` -> `/home/dockbox/.gnupg/S.gpg-agent`
- `~/.gnupg/pubring.{kbx,gpg}` -> `/home/dockbox/.gnupg/` (ro)
- `~/.dockbox_history` -> `/home/dockbox/.zsh_history` (rw)
- `/etc/localtime` -> `/etc/localtime` (ro)
- `/tmp/capture.png` -> `<workdir>/capture.png` (ro)

Project dirs are mounted at exact paths with read-write access.

### Git worktrees

A worktree's `.git` is a gitlink into the main repo's
`.git/worktrees/<name>`, which lives **outside** the worktree dir. If that
backing store isn't mounted, `git` is dead in the box.

When the worktree is the **project dir**, dockbox handles this
automatically — it detects the gitlink and also mounts the backing common
`.git` at its own path. A broken gitlink (missing backing store) is
reported and the launch continues without git.

Auto-detect runs on project dirs only, not `-v` mounts. So to work across a
repo and its worktrees, keep the real `.git` in a mount yourself — run
dockbox at the **repo root**, or add the **root as a `-v`**:

```bash
dockbox ~/wk/repo          # root mount: .git plus every worktree under it
dockbox -v ~/wk/repo .     # carry the root while working in another dir
```

Worktrees created under the root (e.g. `<repo>/.<name>`) come along for
free either way — the root mount already holds both them and `.git`.

`~/.claude` is rw so the boxed agent can update skills, settings, and
memory just like a normal session. This is intentional — treat the
container as a full peer that should continuously improve shared config.

## Ephemeral builds

Build artifacts are an attack surface, not state to persist. Two layers
work together so builds never touch your host workdir:

1. **Rust / Python uv state in `/opt`**: the image sets `CARGO_HOME`,
   `RUSTUP_HOME`, and `UV_TOOL_DIR` to `/opt/dev-tools/...`. Builds
   produce artifacts in the workdir as usual; tool caches and toolchains
   live in the image, not your project.

2. **Overmount by default** (Node, Bun, framework caches): for any
   ecosystem that hardcodes its output dir in CWD, dockbox walks the
   workdir, finds every matching directory (recursive, pruned so it
   doesn't recurse into matches), and replaces each with a fresh empty
   mount inside the container. Owned by the runtime user, gone when
   the container exits.

   Names overmounted by default:

   ```
   node_modules  .next  dist  build  .turbo  .cache
   ```

   Monorepo workspaces are handled automatically — every match under
   the workdir gets its own mount.

   ### Ownership flow (same for both backends)

   The container always starts as root via `--user 0:0`. The
   `dockbox-init` entrypoint:

   1. Registers the host invoker in `/etc/passwd` and `/etc/group`
      using `DOCKBOX_USER`, `DOCKBOX_UID`, `DOCKBOX_GID` env vars
      (so `whoami`, `ls -l`, prompts all work).
   2. `chown`s `$HOME` (`/home/dockbox`, a tmpfs) and every overmount
      listed in `DOCKBOX_EPH_PATHS` to the runtime UID/GID.
   3. `exec gosu UID:GID "$@"` to drop privilege before your command.

   The image has no baked user — one image works for every host UID.
   Bind mounts of `~/.claude`, `~/.gitconfig`, etc. nest into
   `/home/dockbox` and keep host ownership.

   ### Backends

   - **tmpfs** (default): kernel `tmpfs` per path. RAM-backed (pages out
     to swap under pressure). Fast for many-small-file workloads.
     Cost: RAM. 1 GB `node_modules` ≈ 1 GB RAM unless swapped.
   - **volume** (`-T`): anonymous Docker volume per path. Disk-backed.
     Pick this when you don't want to pay RAM for the artifact dirs.

**Trade-off**: every fresh session re-installs and re-builds. Intentional —
no stale artifacts persist, only source code is long-lived. A warm cache
is a liability; the source tree is the truth.

**Opt out** (`dockbox -P` / `--no-ephemeral`):

- You've committed `dist/` or `build/` and need the container to see it.
- You want to share a single `node_modules/` across runs (and accept the
  cache-poisoning risk).
- You're debugging a build issue and need the artifacts to survive.

The Rust/Python auto-redirects still apply with `-P` — they're baked into
the image's env, not the overmount layer.

### Surprise on first run

If you already have a populated `node_modules/` on the host, the container
will see an empty one and re-install on the first command. This is the
sandbox working correctly. Subsequent commands in the same container reuse
the mount; exiting the container discards it.

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
