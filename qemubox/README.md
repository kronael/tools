# qemubox

Real isolation with zero ceremony — **security that gets out of your way.**

A QEMU VM runs a coding agent with its own kernel. Project files and agent
config are shared with the host. The last session powers the VM off; its disk
and guest home survive the next launch. `qemubox rm` deletes the disk.
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

`make install` builds the `vm` target from `dockbox/Dockerfile`, exports it
into a qcow2 base named by its Docker image ID, then installs the script.
`qemubox build-base --force` refreshes the agent CLI build layer.

System packages:

```sh
# Debian
sudo apt install qemu-system-x86 qemu-utils openssh-client tar libarchive-tools e2fsprogs docker.io docker-cli
# Arch
sudo pacman -S qemu-base openssh tar libarchive e2fsprogs docker
# Fedora
sudo dnf install qemu openssh-clients tar bsdtar e2fsprogs moby-engine docker-cli
```

The build needs Docker, `bsdtar` from libarchive, and e2fsprogs ≥1.47 with
`mke2fs -d <tarball>` support. It probes that support before building. Allow
about 20 GB free in `/tmp` and 11 GB per base on the state filesystem.

KVM acceleration needs read and write access to `/dev/kvm`. Without it qemubox falls back to slow
software emulation.

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
qemubox -N bash            # empty VM, no project mount
```

`qemubox [tool] [dirs] [args]`. The first bare (non-path) argument is the tool:
`claude` (default, opus @ xhigh), `haiku` / `sonnet` / `opus` / `fable` for
Claude models, `codex` / `gpt` / `mini` / `spark` for Codex, `bash` / `zsh` for
a login shell, or any binary in the VM. `exec <cmd>` passes every later argument
through untouched. The default VM name is the project dir basename; `-n name` gives a separate box.

Management:

```sh
qemubox ls               # list NAME STATUS USE RAM DISK PATH
qemubox status repo      # readiness of one VM (process/ssh/boot) without a shell
qemubox rm repo          # remove one VM by exact name
qemubox rm 'repo-*'      # remove by glob (only * or ? trigger glob matching)
qemubox rm -a            # remove all VMs (bare `rm` refuses; -a or '*' means all)
qemubox prune [hours]    # remove old stopped VMs; stop running idle VMs past 4h
qemubox build-base       # (re)bake the prebuilt base image
```

## Lifecycle

A box starts on first use and powers off when the **last** session exits
(counted by session markers). The disk stays on the host; the next launch
boots that disk and keeps files in the guest home. `qemubox rm` deletes it.
A missing recorded base image refuses launch with a `qemubox rm` hint.
Each disk records trusted or `-U` mode. A mismatch or missing trust record
refuses launch; use `-n` for another box or `qemubox rm` to delete the disk.
Re-entering a running box from a second terminal joins the live VM; it stays up until every session has exited, so concurrent
sessions don't tear it down under each other. The tool/model applies to the
new session, but mount flags (`-v`, dirs, network) are fixed at boot and are
ignored on re-entry — use `-n <name>` for a separately-mounted box.

The per-VM lock covers setup, session markers, shutdown and removal.
A new session waits for full guest readiness before it runs.
`QEMUBOX_READY_TIMEOUT` sets the wait limit in seconds (default 180);
a timeout prints the serial log tail. HUP and TERM remove the session marker.
Dead host PID markers are removed under the lock. A failed marker listing
keeps the VM up and reports an error.

`ls` shows busy/idle from session markers, QEMU resident RAM, and the overlay
space allocated on the host (both sizes in KiB). `rm` accepts several names
or globs, with or without the `qemubox-` prefix, and fails if removal fails.
`prune [hours]` removes stopped VMs after that many hours (default 2160).
Running VMs with no sessions stop after four hours since readiness; their disks
stay until the stopped age rule applies. Prune also removes base sets that no
VM references, keeping the `current` base.

## Build directories

`node_modules`, `.next`, `.turbo` and `.cache` directories found under each
project become empty tmpfs mounts owned by the guest user. Discovery stops at
depth 4 and prunes each match, so nested dependency trees get one mount.
Only directories present at launch are overmounted.

`-P` / `--no-ephemeral` keeps project build directories on the host.
`-T` mounts directories backed by the guest disk, keyed by canonical path.
Both modes keep `/tmp` and `/tmp/cargo-target` on tmpfs, with
`CARGO_TARGET_DIR=/tmp/cargo-target` in each session. Guest disk build data
survives boots until removal; tmpfs data disappears at shutdown. A failed mount stops launch.

## What crosses into the VM

Default host access includes:

1. **Your project dir(s)** — 9p-mounted at their real host paths, read-write,
   including `.git`. `-v path` adds an extra read-only mount, `-v path:rw` a
   read-write one. `-N` runs an empty VM with no project mount.
2. **Your agent config** — `~/.claude`, `~/.codex`, `~/.agents` (settings,
   credentials, skills, all project histories) are mounted read-write
   at their host paths. `~/.claude/plugins` is mounted read-only. Guest edits reach the host, and absolute skill links
   resolve because the guest has the host username, UID, GID and home path.

Other home paths require an explicit mount or forwarding flag.
`~/.gitconfig` and gpg **public** keyrings are staged read-only.
The shared Dockerfile's Claude wrapper reads the staged, read-only
`/tmp/host-claude.json` and writes a private writable `~/.claude.json`.
It passes `--settings '{"sandbox":{"enabled":false}}'` in the VM so the
shared `~/.claude/settings.json` needs no edit or overlay.
`~/.dockbox_history` backs both shell history files through a writable share.
That share uses a hard link; `QEMUBOX_HOME` and the history file must be on
the same filesystem. A failed link stops launch.

Each VM gets its own SSH key on a localhost-only forwarded port, so guests can't
reach or log into each other. `-A` forwards your SSH agent, `-D` the Docker
socket, `-K` the gpg-agent (commit signing; off by default), `-G` mounts
`~/.config/gcloud` ro, `-g` forwards `GH_TOKEN`/`GITHUB_TOKEN`.

`-H` is an egress kill-switch: it disables the guest's outbound network. `-U`
(or `--untrusted`) goes further — it injects **no** host config or credentials
and forces the network off. Project dirs and explicit `-v` paths remain mounted,
so they must not contain credentials you want to withhold. The agent can't authenticate with
no credentials, so `-U` is for `bash`/build/test, not for running the agent.

## Security posture

What qemubox gives you:

- **Host-filesystem confinement.** The guest is a real VM with its own kernel;
  it can only touch the project dir(s) you mount and its own persistent disk.
  Host paths outside the shares stay inaccessible unless explicitly forwarded.
- **Persistent guest storage.** The qcow2 overlay keeps installs and guest
  files across boots. `qemubox rm` or age-based prune deletes it.

What it does **not** give you — do **not** run genuinely hostile code here:

- **Your real agent credentials are shared read-write.** Like dockbox, qemubox
  shares your live `~/.claude` / `~/.codex` (tokens included).
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
as dockbox does; it ignores `-A`, `-D`, `-K`, `-S`, `-n`, `-d` and `-x`.
Files contain whitespace-separated tokens, never shell code. Project rc files
are masked read-only inside the guest.

Git worktrees also mount their common git directory at its host path.
Claude opens its session selector when the project has JSONL history;
the project slug maps every non-alphanumeric character to `-`.
Codex defaults to `gpt-5.6-sol` with `xhigh` effort.
SSH allocates a terminal only when both stdin and stdout are terminals.

Guest setup disables guest NTP and syncs the clock from the host before
the first session of each boot. The guest also uses the host time zone.
PAM limits grant nice -20, rtprio 99 and unlimited locked memory to the user.
New mount parent directories belong to the user; existing parents keep their owner.

State lives in `~/.local/share/qemubox` (override with `QEMUBOX_HOME`). The base
image is kept while current or referenced; `rm` deletes a box's overlay, key, config, known-hosts,
pid, and serial log. `QEMUBOX_SOURCE` selects the tools source repository.

For an 8 GiB VM: `QEMUBOX_MEM=8192 qemubox -n small .`.
