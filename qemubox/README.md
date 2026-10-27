# qemubox

Real isolation with zero ceremony — **security that gets out of your way.**

A QEMU VM runs a coding agent with its own kernel. Project files and agent
config are shared with the host. The VM powers off twenty minutes after its
last session exits; its disk and guest home survive the next launch.
`qemubox rm` deletes the disk.
Build tmpfs mounts last for one boot. Files written to host shares remain.

## Install

```sh
cd qemubox
make install
```

`make install` builds the `vm` target from [Dockerfile](Dockerfile), exports it
into a rootfs directory named by its Docker image ID, then installs the script.
The pinned kernel and initrd use a separate cache named by the hash of
`Dockerfile.kernel`, `kernel.fragment` and `initrd-init`.
`qemubox build-base -f` or `--force` refreshes the agent CLI build layer.
`build-base` and `rm` remove each base that is not current and that no VM uses.

System packages:

```sh
# Debian
sudo apt install qemu-system-x86 virtiofsd openssh-client tar python3 \
    e2fsprogs docker.io docker-cli
# Arch
sudo pacman -S qemu-base virtiofsd openssh tar python e2fsprogs docker
# Fedora
sudo dnf install qemu virtiofsd openssh-clients tar python3 e2fsprogs moby-engine docker-cli
```

The build needs Docker and GNU tar. It streams the Docker export directly to
the state filesystem and preserves file modes. All files in the rootfs belong
to the host user; the read-only root share maps that user to guest root in both
directions. The build checks free space against the merged rootfs size plus
1 GiB before export.
Published rootfs directories stay immutable; only their root share uses permanent
virtiofs caching. Project and config shares keep automatic caching.
Debian installs `mkfs.ext4` in `/usr/sbin`; the launcher adds that directory to PATH.

KVM acceleration needs read and write access to `/dev/kvm`. Without it qemubox falls back to slow
software emulation.

Each VM is a systemd user unit. A launch needs systemd 254 or newer,
`systemctl --user` to answer,
`ss` from iproute2, and lingering, without which the user manager stops every
VM at your last logout. A launch refuses to start without lingering; enable it
once with `loginctl enable-linger $(id -un)`.
The launcher finds `virtiofsd` in PATH, `/usr/lib/virtiofsd`, or
`/usr/libexec/virtiofsd`. The daemon must support `--readonly` and
`--translate-uid`/`--translate-gid` with `map:` mappings.

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
`claude` (default, opus @ high), `haiku` / `sonnet` / `opus` / `fable` for
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
SSH readiness admits the agent while Docker continues starting in parallel.
Docker startup failure shuts down the guest and appears in the journal.
Each directory share has a user unit, `qemubox-fs@<name>-<tag>.service`,
including the read-only `cfg` and root shares. QEMU starts after these units and waits
for their sockets. Stopping the VM stops its share units, including after
a failed boot. If a share daemon exits, systemd stops the VM and its other
share daemons. The next launch boots the persistent disk.

After an `io-error` pause, the timer resumes the VM when the state filesystem
has at least `QEMUBOX_RESUME_FREE` MiB free, default 2048. The setting applies
at boot; zero disables recovery. Manual pauses stay paused.
The readiness loop also checks free space during startup, within its timeout.
Session SSH disables application keepalive timeouts so a pause can preserve the
running command. Control probes retain their timeouts.

Sessions are the established SSH connections to the box's forwarded port.
Running containers on the native guest Docker daemon also keep the VM busy.
An idle daemon does not count. A failed container probe preserves the VM and reports an error.
Boot and every session exit stamp the box's `idle` file with `QEMUBOX_LINGER`
(default 1200, twenty minutes). The timer `qemubox-check@<name>.timer` stops
the VM once no session or container runs and the stamp is older than the seconds
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
if paused and receives TERM through its init process. The init stops services,
syncs disk writes and powers off. Systemd kills qemu after 10 s.
If a share daemon exits, shutdown skips guest commands and terminates qemu.
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

`/tmp` is a tmpfs capped at 75% of guest RAM and active guest swap combined.
Without `-B`, the build directories, `/tmp/cargo-target` and every other file
in `/tmp` share that cap. A full `/tmp` fails with ENOSPC.
Process memory also needs RAM or swap, so the cap does not prevent every OOM.
Each session sets `CARGO_TARGET_DIR=/tmp/cargo-target` and
`CODEX_SQLITE_HOME=/tmp/codex-sqlite`. Codex keeps its SQLite databases in
guest `/tmp` to keep its SQLite locks separate from the host.
A `sqlite_home` key in `~/.codex/config.toml` overrides the
variable. At shutdown the databases disappear with any prompts still queued in
them; Codex rebuilds its thread index from `~/.codex/sessions` at the next
start.

The guest Codex wrapper sets `--no-daemon` to avoid the host's shared background
server. The wrapper cannot run `codex agents`, `codex queue`, or `--remote` sessions.

Guest disk build data survives boots until removal. `/tmp` data disappears at
shutdown. A failed mount stops launch.

## What crosses into the VM

Default host access includes:

1. **Your project dir(s)** — virtiofs-mounted at their real host paths, read-write,
   including `.git`. `-v path` adds an extra read-only mount, `-v path:rw` a
   read-write one. `-T` mounts no project dir.
2. **Your agent config** — `~/.claude`, `~/.codex`, `~/.agents` (settings, credentials, skills,
   all project histories) are mounted read-write at their host paths; `~/.claude/plugins`
   read-only; `~/.claude/sessions` is a private guest tmpfs, so VMs and the host never list or
   message each other's Claude sessions. Guest edits reach the host. The guest has the host
   username, UID, GID and home path, so an absolute skill link resolves when its target is
   mounted too.
3. **Your agent tokens** — `CLAUDE_CODE_OAUTH_TOKEN`, `OPENAI_API_KEY` and `CODEX_API_KEY`,
   when set on the host, reach each session's environment.

Every session variable — the agent tokens, `-g`'s `GH_TOKEN`/`GITHUB_TOKEN`, `-D`'s
`DOCKER_HOST`, each `-e VAR` — travels over SSH stdin into a per-session file in the guest's
`/dev/shm` (mode 0600, guest tmpfs outside every virtiofs mount). The session sources and deletes it
before it starts the tool, so no value reaches an SSH command line, which every host user can
read in `/proc`.

Other home paths require an explicit mount or forwarding flag.
`~/.gitconfig` and gpg **public** keyrings are staged read-only.
The Dockerfile's Claude wrapper reads the staged, read-only
`/tmp/host-claude.json` and writes a private writable `~/.claude.json`.
It passes `--settings '{"sandbox":{"enabled":false}}'` in the VM so the
shared `~/.claude/settings.json` needs no edit or overlay.
`~/.qemubox_history` backs both shell history files through a writable share.
That share uses a hard link; `QEMUBOX_HOME` and the history file must be on
the same filesystem. A failed link stops launch.

At boot the launcher writes `/etc/claude-code/CLAUDE.md` in the guest.
Claude Code reads the sandbox, shared mount and disk lifetime details there.
Every session gets `CLAUDE_SANDBOX=qemubox`.

Docker starts inside the VM before the guest becomes ready. Images and containers
use direct ext4 directories on the guest disk. Container networking
stays inside the VM; `docker run --network host` uses the guest's network.

Each VM gets its own SSH key on a localhost-only forwarded port, so guests can't reach or
log into each other. `-A` forwards your SSH agent, `-D` the Docker socket (and with it
access to host containers), `-K` the gpg-agent (commit signing; off by
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
- **Persistent guest storage.** The ext4 upper keeps installs and guest
  files across boots. `qemubox rm` deletes it.

What it does **not** give you — do **not** run genuinely hostile code here:

- **Your real agent credentials are shared read-write.** Qemubox
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
The project `.qemuboxrc` applies its safe flags after command-line parsing.
It ignores `-A`, `-D`, `-K`, `-S`, `-T`, `-n`, `-d` and `-x`.
Files contain whitespace-separated tokens, never shell code. Project rc files
are masked read-only inside the guest.

Git worktrees also mount their common git directory at its host path.
Claude opens its session selector when the project has JSONL history
(`-N` skips it);
the project slug maps every non-alphanumeric character to `-`.
Codex defaults to `gpt-6.1-sol`/`high`. A `--model` or Codex `-m` after
the tool name replaces the alias's model and effort. SSH allocates a tty only
if stdin and stdout are terminals.

`-e NAME=value` passes the literal value, including empty values and newlines.
`-e NAME` reads the host environment. SSH agent forwarding requires `-A`, even when
the host SSH configuration enables forwarding.
Codex connects `.agents/skills` to `.claude/skills` when the skills exist.
The bridge preserves custom `.codex/AGENTS.md` files and unrelated symlinks.

When `/tmp/capture.png` exists at boot, the VM reads that file through a private
read-only share. Writes to the same host inode appear in guest `/tmp/capture.png`.
The VM does not share the host `/tmp` directory. Creation or inode replacement
after boot requires a new boot.

The guest gets UTC time from QEMU's host-backed real-time clock.
PAM limits grant nice -20, rtprio 99 and unlimited locked memory to the user.
New mount parent directories belong to the user; existing parents keep their owner.

State lives in `~/.local/share/qemubox` (override with `QEMUBOX_HOME`). Each box pins
a base image ID and has a sparse `upper.raw` ext4 disk, sized by `QEMUBOX_DISK`
(default 40G). The guest combines the read-only rootfs lower with that disk
through overlayfs. Writes allocate host disk blocks; ext4 discard releases
deleted blocks. The base image stays while current or referenced.
`rm` deletes a box's upper, key, config, known-hosts,
port, network mode and idle and stopped stamps. `QEMUBOX_SOURCE` selects the tools source repository.
`QEMUBOX_QEMU` selects the qemu binary, default `qemu-system-x86_64`.

## Memory

A VM has a 24 GiB RAM ceiling, set by `QEMUBOX_MEM=24576` in positive decimal MiB.
Images with memory hotplug support boot with 2 GiB plus any remainder below 128 MiB.
Memory growth requires QEMU 8.2 or newer.
After SSH starts, the launcher requests the remaining RAM in 128 MiB blocks.
RAM grows in the background. The launcher does not wait for all RAM to come online.
For ceilings below 2176 MiB, all configured RAM is present at boot.
Boxes pinned to images without memory hotplug support boot with all configured RAM.
The launcher accepts one to nine decimal digits and preserves the exact ceiling.
`QEMUBOX_SWAP=16384` requests 16 GiB of guest swap in MiB. Set `QEMUBOX_SWAP=0`
to disable swap on the next boot. The launcher accepts one to nine decimal digits.
Boot settings apply when the box starts; joining a running box keeps its settings.

The guest allocates `/.qemubox/swap` on direct ext4 storage with mode 0600.
The guest formats the file once and reactivates the file on later boots.
A different nonzero size fails boot with the stored and requested sizes.
Choose a matching size or zero. A request at least as large as the filesystem
fails before allocation. Insufficient free space fails with the allocation error.
Swap consumes guest filesystem capacity shared with persistent files and Docker.
Disabling swap keeps its file and allocated extents.

The guest activates swap before mounting `/tmp`. The tmpfs cap is
`3 * (QEMUBOX_MEM * 1024 + SwapTotal) / 4` in whole KiB.
The guest reads active `SwapTotal` from `/proc/meminfo` and sets the cap once at boot.
Only active swap counts toward this cap. Swap can hold cold tmpfs and process pages.
The guest swap file has allocated extents. The host disk stays sparse, with physical
host allocation dependent on writes.

Every 60 seconds, the guest checks memory use under the `/qemubox` workload cgroup.
This cgroup contains SSH sessions, Docker services and containers.
Init and the reclaim loop stay outside it.
Each check reads the RAM currently online. Above half of this RAM,
the loop requests the excess through `memory.reclaim`,
up to 1 GiB per check. No hard memory limit or balloon reduction applies.
The console records partial reclaim with before and after usage and retains stderr.
A control-file error stops the loop and triggers guest shutdown.

KVM backs guest pages when the guest touches them. The virtio-balloon device
reports free pages to the host. Host RAM release depends on QEMU and virtiofs support;
guest reclaim alone does not prove a reduction in host RAM use.
If the host has swap, the host can also swap cold guest pages.

For an 8 GiB VM: `QEMUBOX_MEM=8192 qemubox -n small .`.

## Native checks

`make test` runs the unit suite. `make test-native` starts disposable actual VMs.
The native checks require the production base with the current VM helpers and a
disk-backed fixture directory. The harness uses fixture guidance and signing keys.
It retains its private run directory for inspection and stops only its own VMs.
The screenshot check requires `/tmp/capture.png` to be absent before the run.

```sh
QEMUBOX_NATIVE=1 QEMUBOX_NATIVE_BASE="$HOME/.local/share/qemubox" \
  QEMUBOX_NATIVE_DIR="$HOME/native-fixtures" make -C qemubox test-native
```

Create the fixture directory first. `QEMUBOX_NATIVE_DOCKER` selects a host Docker
client executable with socket access. The default is `docker`.
Authenticated Codex turns and Claude/pi startup checks use existing authorized
credentials in a separate controller check. The harness does not copy those credentials.
