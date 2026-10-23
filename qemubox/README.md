# qemubox

Real isolation with zero ceremony — **security that gets out of your way.**

A QEMU VM runs a coding agent with its own kernel. Project files and agent
config are shared with the host. The VM powers off twenty minutes after its
last session exits; its disk and guest home survive the next launch.
`qemubox rm` deletes the disk.
Build tmpfs mounts last for one boot. Files written to host shares remain.

**qemubox vs dockbox** — same idea, different wall between guest and host:

- **[dockbox](../dockbox/)** uses a Docker container: lighter, faster, shares
  the host kernel. The everyday default for code you trust.
- **qemubox** uses a full VM with its own kernel and hardware-level isolation:
  heavier, but the guest can't reach the host filesystem through a container
  escape. Use it for a stronger wall around what the agent can touch on disk.

## Install

```sh
cd qemubox
make install
```

`make install` builds the `vm` target from [Dockerfile](Dockerfile), exports it
into a qcow2 base named by its Docker image ID, then installs the script.
`qemubox build-base -f` or `--force` refreshes the agent CLI build layer.
`build-base` writes the base zstd-compressed. `build-base` and `rm` remove each base that is not current and that no VM uses.

System packages:

```sh
# Debian
sudo apt install qemu-system-x86 qemu-utils openssh-client tar python3 libarchive-tools e2fsprogs docker.io docker-cli
# Arch
sudo pacman -S qemu-base openssh tar python libarchive e2fsprogs docker
# Fedora
sudo dnf install qemu openssh-clients tar python3 bsdtar e2fsprogs moby-engine docker-cli
```

The build needs Docker, `bsdtar` from libarchive, and an e2fsprogs whose
`mke2fs -d` accepts a tarball; Debian 12's 1.47.0 does not. The build probes
that support before it starts. Debian installs `mke2fs` in `/usr/sbin`, which a
non-root PATH omits, so the build adds it. Allow about 20 GB free in `/tmp` and 11 GB
per base on the state filesystem.

KVM acceleration needs read and write access to `/dev/kvm`. Without it qemubox falls back to slow
software emulation.

Each VM is a systemd user unit. A launch needs `systemctl --user` to answer,
`ss` from iproute2, and lingering, without which the user manager stops every
VM at your last logout. A launch refuses to start without lingering; enable it
once with `loginctl enable-linger $(id -un)`.

## Usage

```sh
qemubox                    # mount current dir, run claude in the VM
qemubox ~/src/repo         # mount a repo, run claude there
qemubox haiku ~/src/repo   # pick a Claude model alias
qemubox codex ~/src/repo   # run Codex instead
qemubox cargo test .       # run any command in the mounted dir
qemubox bash               # shell into the project's VM (-n name for a separate box)
qemubox exec make test     # run a command in the project's VM
qemubox -v ~/src/lib .     # extra read-only mount (:rw for read-write)
qemubox -T bash            # new scratch VM: no project mount, works in /tmp/work
qemubox -N                 # new Claude session, no resume picker
```

`qemubox [tool] [dirs] [args]`. The first bare (non-path) argument is the tool:
`claude` (default, opus @ xhigh), `haiku` / `sonnet` / `opus` / `fable` for
Claude models, `codex` / `gpt` / `mini` / `spark` for Codex, `bash` / `zsh` for
a login shell, or any binary in the VM. `exec <cmd>` passes every later argument
through untouched. The default VM name is the project dir basename; `-n name` gives a separate box.

`-T` starts a temporary session: qemubox mounts no project dir, and the
session starts in `/tmp/work` on the guest tmpfs, which power-off clears.
Each `-T` run gets a new random VM name, such as `qemubox-brave-turing`,
unless `-n` names it. `-v` still adds host paths, a dir argument is an error,
and `-T` implies `-N`. Scratch VMs stay on disk after power-off: `qemubox ls`
lists them and `qemubox rm` removes them.

qemubox does not mount a sensitive path: `/`, a top-level dir such as `/etc`
or `/home`, `$HOME`, an ancestor of `$HOME`, or a hidden dir directly in
`$HOME`. A project dir or `-v` path of that kind is an error. A run from such
a dir with no dir argument starts a scratch VM, as `-T` does. The guest home
then stays the guest's own, so the guest shell uses only the image's `/etc`
defaults and not the host dotfiles. `--mount-sensitive` mounts the path.

Management:

```sh
qemubox ls               # list NAME STATUS USE RAM DISK PATH
qemubox status repo      # one VM's unit, state, ssh and port without a shell
qemubox stop repo        # power one VM off, keep its disk (-f: SIGTERM qemu at once)
qemubox stop -a          # power every running VM off
qemubox rm repo          # remove one VM by exact name
qemubox rm 'repo-*'      # remove by glob (only * or ? trigger glob matching)
qemubox rm -a            # remove all VMs (bare `rm` refuses; -a or '*' means all)
qemubox rm --stopped 72  # remove VMs stopped for over 72 whole hours
qemubox prune            # stop running idle VMs past 4h; reclaim unused bases
qemubox build-base       # (re)bake the prebuilt base image
```

## Lifecycle

Each VM is the systemd user unit `qemubox@<name>.service`, which needs
lingering on (see Install). qemu runs in the foreground; its serial console
goes to `journalctl --user -u qemubox@<name>`. A box starts on first use and
the start waits for guest setup, at most `QEMUBOX_READY_TIMEOUT` seconds
(default 180); a failed boot stops the unit and prints the journal tail.

Sessions are the established SSH connections to the box's forwarded port.
Boot and every session exit stamp the box's `idle` file with `QEMUBOX_LINGER`
(default 1200, twenty minutes). The timer `qemubox-check@<name>.timer` stops
the VM once no session is connected and the stamp is older than the seconds
it holds; `QEMUBOX_LINGER=0` stops it as the last session exits. A launch that
dies before its session leaves the VM to the timer. The disk stays on the
host; the next launch boots that disk and keeps files in the guest home.
`qemubox rm` deletes it.
A missing recorded base image refuses launch with a `qemubox rm` hint.
Each disk records trusted or `-U` mode. A mismatch or missing trust record
refuses launch; use `-n` for another box or `qemubox rm` to delete the disk.
Re-entering a running box from a second terminal joins the live VM; a launch
during a boot waits on the per-VM lock, which covers the box files, the start
and removal. The tool/model applies to the
new session, but mount flags (`-v`, dirs, network) are fixed at boot and are
ignored on re-entry — use `-n <name>` for a separately-mounted box.

`qemubox stop <name>` stops the unit and keeps the disk: the guest is resumed
if paused, trimmed and powered off, and systemd sends qemu SIGTERM after 100 s.
`-f` sends SIGTERM at once. Every stop, a guest poweroff included, stamps the
box's `stopped` file. Names, globs and `-a` match as for `rm`; a stopped box
is reported and skipped.

`ls` shows busy/idle from the session count, the unit's memory, and the overlay
space allocated on the host (sizes in K, M or G); a VM waiting out
`QEMUBOX_LINGER` is `running idle`. qemu pauses a guest whose disk write fails
because the host filesystem under the overlay is full; other write errors go
to the guest. `ls` and `status` then show `paused:` and qemu's reason, such as
`paused:io-error`, and a launch into that VM fails with that state rather than
waiting. Free host space, then `qemubox stop` it. Each VM has a QMP control
socket, `qmp` in its state dir. The state dir is owner-only.

The overlay passes guest discards through, and `stop` trims the guest disk,
so space freed in the guest leaves the overlay on the host. A guest that
powers itself off skips the trim; the first `stop` after its next boot does it.

`rm` accepts several names or globs, with or without the `qemubox-` prefix,
and fails if removal fails.
`rm --stopped <hours>` lists the VMs stopped for over that many whole hours
(the `stopped` marker age, else the directory age), then removes them. `prune`
takes no argument and never removes a VM: it stops running VMs with no session
whose `idle` stamp is four hours old, and removes base sets that no VM references,
keeping the `current` base. Their disks stay until `rm`.

## Build directories

`node_modules`, `.venv`, `.next`, `.turbo` and `.cache` directories found under each
project become empty bind mounts owned by the guest user. Discovery stops at
depth 4 and prunes each match, so nested dependency trees get one mount.
Only directories present at launch are overmounted.

`-P` / `--no-ephemeral` keeps project build directories on the host.
`-B` backs them with the guest disk, keyed by canonical path. Without `-B`
they are backed by directories under `/tmp/qemubox-builds`, keyed the same way.

`/tmp` is a tmpfs capped at 75% of guest RAM, 18 GiB at the default 24 GiB.
Without `-B`, the build directories, `/tmp/cargo-target` and every other file
in `/tmp` share that cap. A full `/tmp` fails with ENOSPC, not an out-of-memory
guest. Process memory is not counted against the cap.
Each session sets `CARGO_TARGET_DIR=/tmp/cargo-target` and
`CODEX_SQLITE_HOME=/tmp/codex-sqlite`. Codex keeps its SQLite databases in
guest `/tmp`, because 9p gives the guest no shared mmap and no lock shared
with the host. A `sqlite_home` key in `~/.codex/config.toml` overrides the
variable. At shutdown the databases disappear with any prompts still queued in
them; Codex rebuilds its thread index from `~/.codex/sessions` at the next
start.

The guest Codex wrapper sets `--no-daemon` to avoid the host's shared background
server. The wrapper cannot run `codex agents`, `codex queue`, or `--remote` sessions.

Guest disk build data survives boots until removal. `/tmp` data disappears at
shutdown. A failed mount stops launch.

## What crosses into the VM

Default host access includes:

1. **Your project dir(s)** — 9p-mounted at their real host paths, read-write,
   including `.git`. `-v path` adds an extra read-only mount, `-v path:rw` a
   read-write one. `-T` mounts no project dir.
2. **Your agent config** — `~/.claude`, `~/.codex`, `~/.agents` (settings, credentials, skills,
   all project histories) are mounted read-write at their host paths; `~/.claude/plugins`
   read-only; `~/.claude/sessions` is a private guest tmpfs, so VMs and the host never list or
   message each other's Claude sessions. Guest edits reach the host. The guest has the host
   username, UID, GID and home path, so an absolute skill link resolves when its target is
   mounted too.
3. **Your agent tokens** — `CLAUDE_CODE_OAUTH_TOKEN`, `OPENAI_API_KEY` and `CODEX_API_KEY`,
   when set on the host, reach each session's environment, as in dockbox.

Every session variable — the agent tokens, `-g`'s `GH_TOKEN`/`GITHUB_TOKEN`, `-D`'s
`DOCKER_HOST`, each `-e VAR` — travels over SSH stdin into a per-session file in the guest's
`/dev/shm` (mode 0600, guest tmpfs outside every 9p mount). The session sources and deletes it
before it starts the tool, so no value reaches an SSH command line, which every host user can
read in `/proc`.

Other home paths require an explicit mount or forwarding flag.
`~/.gitconfig` and gpg **public** keyrings are staged read-only.
The shared Dockerfile's Claude wrapper reads the staged, read-only
`/tmp/host-claude.json` and writes a private writable `~/.claude.json`.
It passes `--settings '{"sandbox":{"enabled":false}}'` in the VM so the
shared `~/.claude/settings.json` needs no edit or overlay.
`~/.dockbox_history` backs both shell history files through a writable share.
That share uses a hard link; `QEMUBOX_HOME` and the history file must be on
the same filesystem. A failed link stops launch.

At boot the launcher writes `/etc/claude-code/CLAUDE.md` in the guest.
Claude Code reads the sandbox, shared mount and disk lifetime details there.
Every session gets `CLAUDE_SANDBOX=qemubox`.

Docker runs inside the VM. Its socket starts the guest daemon on the first
Docker command. Images and containers use the guest disk. Container networking
stays inside the VM; `docker run --network host` uses the guest's network.

Each VM gets its own SSH key on a localhost-only forwarded port, so guests can't reach or
log into each other. `-A` forwards your SSH agent, `-D` the Docker socket (and with it
`docker exec` into every dockbox on the host), `-K` the gpg-agent (commit signing; off by
default), `-G` mounts `~/.config/gcloud` ro, `-g` forwards `GH_TOKEN`/`GITHUB_TOKEN`.

`-H` is an egress kill-switch: it disables the guest's outbound network. `-U`
(or `--untrusted`) goes further — it injects **no** host config or credentials
(the agent tokens and `GH_TOKEN`/`GITHUB_TOKEN`/`DOCKER_HOST` are dropped, even from
a `.qemuboxrc` `-e`) and forces the network off. Project dirs and explicit `-v` paths
remain mounted, so they must not contain credentials you want to withhold. The agent can't authenticate with
no credentials, so `-U` is for `bash`/build/test, not for running the agent.

## Security posture

What qemubox gives you:

- **Host-filesystem confinement.** The guest is a real VM with its own kernel;
  it can only touch the project dir(s) you mount and its own persistent disk.
  Host paths outside the shares stay inaccessible unless explicitly forwarded.
- **Persistent guest storage.** The qcow2 overlay keeps installs and guest
  files across boots. `qemubox rm` deletes it.

What it does **not** give you — do **not** run genuinely hostile code here:

- **Your real agent credentials are shared read-write.** Like dockbox, qemubox
  shares your live `~/.claude` / `~/.codex` (tokens included) and the agent
  token variables.
  Guest code can read, change and exfiltrate those tokens and config files.
- **Outbound network is on by default.** Pass `-H` (egress kill-switch) to
  disable it, or `-U` for a credential-free, network-off inspection mode.
  Without either, the path for exfiltration is open.
- **In-guest agents run with permission checks bypassed**
  (`--dangerously-skip-permissions` / `--dangerously-bypass-approvals-and-sandbox`)
  and the guest user has passwordless sudo.

## Configuration

`~/.qemuboxrc` supplies default flags, one per line, with blank lines and
`#` comments ignored. Command-line flags override these defaults.
The project `.qemuboxrc` applies its safe flags after command-line parsing,
as dockbox does; it ignores `-A`, `-D`, `-K`, `-S`, `-T`, `-n`, `-d` and `-x`.
Files contain whitespace-separated tokens, never shell code. Project rc files
are masked read-only inside the guest.

Git worktrees also mount their common git directory at its host path.
Claude opens its session selector when the project has JSONL history
(`-N` skips it);
the project slug maps every non-alphanumeric character to `-`.
Codex defaults to `gpt-6.1-sol`/`xhigh`. A `--model` or Codex `-m` after
the tool name replaces the alias's model and effort. SSH allocates a tty only
if stdin and stdout are terminals.

Guest setup disables guest NTP and syncs the clock from the host before
the first session of each boot. The guest runs in UTC.
PAM limits grant nice -20, rtprio 99 and unlimited locked memory to the user.
New mount parent directories belong to the user; existing parents keep their owner.

State lives in `~/.local/share/qemubox` (override with `QEMUBOX_HOME`). The base
image is kept while current or referenced; `rm` deletes a box's overlay, key, config, known-hosts,
port, network mode and idle and stopped stamps. `QEMUBOX_SOURCE` selects the tools source repository.
`QEMUBOX_QEMU` selects the qemu binary, default `qemu-system-x86_64`.

## Memory

A VM starts with 24 GiB (`QEMUBOX_MEM=24576`). KVM backs a guest page with
host memory only once the guest touches it, and the VM's virtio-balloon
device reports freed pages back to the host, so a VM costs what the guest
holds, not its size: a `cargo clean` or a removed tmpfs file returns its
pages. If the host has swap, cold guest pages go there when host RAM runs
short. The guest itself has no swap, so the `/tmp` cap under Build directories
keeps a large build from exhausting guest memory.

The guest boots with `noresume`. A Docker-built initramfs can detect host
swap, and the VM must not wait for it.

For an 8 GiB VM: `QEMUBOX_MEM=8192 qemubox -n small .`.
