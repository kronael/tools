# dockbox

A sandbox that is actually useful — full credentials, no permission prompts,
mounts whatever you point at. Docker provides working directory scoping and a clean
environment. The boxed agent has full access to your tools, config, and
credentials — treat it as yourself in a container.

## ELI13

A container is a lightweight box around a program: it gets its own filesystem
view and process space but shares your computer's kernel. dockbox puts a coding
agent (Claude Code or Codex) in one of those boxes, pointed at the folder you
name, with your real tools and credentials handed in so it can actually work.
It's fast and convenient, and it keeps builds and mess out of your host workdir
— but because your live credentials are inside and the box shares your kernel,
it is **not** a wall against hostile code. Treat the boxed agent as *yourself*
working in a container. If you want a stronger host-filesystem wall — a full VM
with a persistent disk — use [qemubox](../qemubox/) instead.

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
make install            # image, dockbox and its seccomp profile
make seccomp            # the seccomp profile only, no image build
make clean              # remove binary, profile and docker image
```

dockbox goes to `~/.local/bin`, the profile to
`~/.local/share/dockbox/seccomp.json`. A new box does not start without the
profile; dockbox names `make seccomp` when it is missing.

## Usage

```bash
dockbox                           # current dir, runs claude
dockbox ~/wk/project              # mount project
dockbox ~/wk/p1 ~/wk/p2           # mount multiple dirs, work in last
dockbox -v ~/wk/lib               # extra mount at same path (ro, default)
dockbox -v ~/wk/lib:rw            # extra mount at same path (rw)
dockbox -P                        # persist host build dirs (no overmount)
dockbox -T                        # build-dir overmounts on anonymous Docker volumes (disk), not tmpfs
dockbox -e GH_TOKEN               # forward env var into container
dockbox -n mybox .                # key the box on mybox (dockbox-mybox)
dockbox bash .                    # run bash instead
dockbox exec make test            # run a command in the box
dockbox ls                        # list boxes: busy/idle, tmpfs use, disk (writable layer)
dockbox rm <name|glob|-a>...      # force-remove boxes and their volumes (-a = all)
dockbox prune [hours]             # remove idle boxes, and exited ones older than N hours (default: 2160)
```

Default command: claude. Use `-x` to override.

`dockbox ls` USE is `busy` while any session or command runs in the box and
`idle` when only its sleeper is left — a box no session holds, safe to remove.
TMPFS totals the tmpfs mounts of a running box (`/tmp`, `/tmp/cargo-target`,
`/dev/shm`, `$HOME` and the build-dir overmounts), each mount once; DISK is
the container's writable layer, volumes excluded. USE and TMPFS show `-` for
a stopped box and `?` when the probe fails. `dockbox prune` removes idle boxes
at least 4 hours old and never a busy one.

### Re-entry into a running box

If a dockbox for the project is already running, the next `dockbox`
invocation enters that live container (`docker exec`) and runs the
requested command there, rather than starting a second one:

```bash
dockbox ~/wk/project    # starts the box, runs claude
dockbox bash            # 2nd terminal: shell inside the same box
dockbox codex           # 3rd terminal: codex inside the same box
```

The entered session shares the container's `HOME`, mounts, and
processes, and runs as your host user (not root). The **command** —
tool, `--model`, `--effort`, args — takes effect, and **env flags**
(`-e`, `-g`) are forwarded into the session, so a box first started
without `-g` still gets the token when a later `dockbox -g` re-enters
it. **Mount/network flags** (`-v`, `-H`, `-D`) do not apply — they're
fixed when the container is created. Use `-n <name>` to key a
separate, fully-provisioned container instead.

## io_uring and capabilities

Docker's default seccomp profile denies io_uring, which Agave's
`solana-test-validator` needs. dockbox starts every box with
`--security-opt seccomp=~/.local/share/dockbox/seccomp.json`: the default
profile from moby/profiles with `io_uring_setup`, `io_uring_enter` and
`io_uring_register` added to its allow list. It is newer than the profile
Docker 29.6.2 builds in (moby/profiles v0.2.3) and also denies a few legacy
socket families (AX25, IPX, AppleTalk and others).

`seccomp.json` is `seccomp/default.json` from
[moby/profiles](https://github.com/moby/profiles) at commit `a21872828a8e`,
unchanged except for those three names after `io_submit`. It is Apache-2.0;
the license ships as `seccomp.LICENSE` and installs beside the profile. To
refresh it, fetch that file again and re-add them.

Boxes also get `SYS_NICE`, `IPC_LOCK` and `SYS_PTRACE`. A capability added
to the container does not reach a session started with `docker exec -u`, so
each session enters as root and `setpriv` drops it to your UID/GID with the
three held as ambient capabilities and the supplementary groups dockbox-init
registered. `nice`/`renice` to a negative value, realtime scheduling (`chrt`),
`mlock` past the memlock limit and ptrace attach to any process in the box
work as your user. A box started by an older dockbox holds none of the three,
and its sessions enter without them.
Realtime priority and locked memory draw on the host's CPU and RAM.

## Configuration

Extra docker args via `.dockboxrc` files (bash-style, `#` comments):

- `~/.dockboxrc` — global defaults (e.g. `--gpus all`)
- `.dockboxrc` in project dir — per-project overrides

Both are optional. Global applies first, project appends. The
project `.dockboxrc` is overmounted with `/dev/null` inside the
container so the boxed agent can't modify it.

## Roaming between networks

A bridge box does not resolve names through the host's resolver: Docker
copies nameservers into the box once, when the container is created. When
the host's `/etc/resolv.conf` is a loopback stub (systemd-resolved's
`127.0.0.53`), unreachable from the box, Docker substitutes the uplink
servers behind it — the DHCP servers of the network the laptop is on at that
moment, which usually answer only from that network. Move to another Wi-Fi
and every lookup in the box times out while the host, whose resolver
switched with the link, is fine. Docker never rewrites a running
container's `resolv.conf` (moby `libnetwork/sandbox_dns_unix.go`: written
at sandbox setup and endpoint join only).

dockbox therefore gives a new bridge box the resolver listening on the
bridge gateway when there is one (`--dns 172.17.0.1`); that resolver follows
the host across network changes. Expose systemd-resolved there:

```sh
# /etc/systemd/resolved.conf.d/docker.conf
[Resolve]
DNSStubListenerExtra=172.17.0.1
```

then `systemctl restart systemd-resolved`. resolved binds the extra address
with `IP_FREEBIND`, so it works before `docker0` exists at boot. Boxes
created before the change keep their copied servers until recreated
(`dockbox rm <name>`). Without a gateway resolver dockbox prints a one-line
note at creation and the box keeps Docker's copy. `-H` (host network) uses
the host's resolver and sockets directly and has neither problem; it also
has no NAT, so a box's connections survive a brief Wi-Fi drop exactly as the
host's do.

## Mounts

Automatic:
- `~/.claude` -> `/home/dockbox/.claude` (rw) - credentials, skills, settings
- `~/.claude/sessions` -> private tmpfs per box. Claude Code registers every
  live session there and lists them with `ListAgents`; the inbox sockets
  live in each box's own `/tmp`, so a private registry means boxes and the
  host neither see nor message each other's sessions, and two boxes' low
  container PIDs no longer overwrite each other's records.
- `~/.claude.json` -> copied at startup with `diffSidebarOpen` pinned off
  (fallback creates minimal file)
- `~/.gitconfig` -> `/home/dockbox/.gitconfig` (ro)
- `~/.gnupg/pubring.{kbx,gpg}` -> `/home/dockbox/.gnupg/` (ro)

Opt-in:
- `gpg-agent socket` -> `/home/dockbox/.gnupg/S.gpg-agent` — only with `-K`
  (commit signing; off by default)
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
keep toolchains, caches and dependency dirs out of your host workdir:

1. **Rust / Python uv state in `/opt`**: the image sets `CARGO_HOME`,
   `RUSTUP_HOME`, and `UV_TOOL_DIR` to `/opt/dev-tools/...`, so tool
   caches and toolchains live in the image, not your project. dockbox
   also sets `CARGO_TARGET_DIR=/tmp/cargo-target`, a dedicated tmpfs, so
   Cargo never writes `target/` to the workdir.

2. **Overmount by default** (Node, Bun, framework caches): for any
   ecosystem that hardcodes its output dir in CWD, dockbox walks the
   workdir, finds every matching directory (recursive, pruned so it
   doesn't recurse into matches), and replaces each with a fresh empty
   mount inside the container. Owned by the runtime user, removed with
   the box.

   Names overmounted by default:

   ```
   node_modules  .next  .turbo  .cache
   ```

   `dist` and `build` are not overmounted, so they land in the host
   workdir: build tools `rm -rf` them, which fails with EBUSY on a
   mountpoint.

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

- You want to share a single `node_modules/` across runs (and accept the
  cache-poisoning risk).
- You're debugging a build issue and need the artifacts to survive.

The Rust/Python auto-redirects still apply with `-P` — they're set in the
container env, not the overmount layer.

### Surprise on first run

If you already have a populated `node_modules/` on the host, the container
will see an empty one and re-install on the first command. This is the
sandbox working correctly. Later sessions in the same box reuse the mount;
the box, mounts included, is removed when its last session exits.

## Authentication

Uses `~/.claude/.credentials.json` from host (via mounted `~/.claude`).

## Permissions

All Claude Code permission prompts are bypassed two ways: `bypassPermissions`
mode injected via `settings.local.json`, and `--dangerously-skip-permissions`
passed by the `claude` wrapper in the image. This is intentional — the use
case is a trusted agent doing real work, not untrusted code execution. If you
need security isolation, this is not the tool.

Boxes are kept apart from each other and from the host's Claude sessions
(private `~/.claude/sessions`, own `/tmp`, so no shared inbox socket), and the
bundle's settings refuse inbound cross-session messages everywhere. `-D`
undoes that: it hands the box the host's Docker socket, so its agent can
`docker exec` into every other dockbox. Pass it only to a box you trust with
all the others.

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
