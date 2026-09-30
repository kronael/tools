# qemubox

Real isolation with zero ceremony — **security that gets out of your way.**

A throwaway QEMU VM where a coding agent works on your project behind a full
hardware-virt boundary, driven by one command that feels exactly like running
the agent bare. Because the VM *is* the perimeter, the agent runs at full tilt —
no permission prompts, no babysitting — while your `~/.ssh`, your other repos,
and the rest of your machine stay untouchable. Your project edits, agent config,
session history and shell history persist to the host; everything else evaporates
when the box shuts down (which it does on its own). You get the safety for free
and stop thinking about it.

## ELI13

Picture a second computer that lives inside your computer, built fresh every
time you start it. You hand it just the one folder to work on and your coding
agent's settings — nothing else, not your SSH keys, not your other projects.
Inside, the agent (Claude Code or Codex) installs packages, runs builds, edits
files — whatever it needs. Close it and that whole inner computer is thrown
away; your real machine's files were never touched.

**qemubox vs dockbox** — same idea, different wall between guest and host:

- **[dockbox](../dockbox/)** uses a Docker container: lighter, faster, shares
  the host kernel. The everyday default for code you trust.
- **qemubox** uses a full VM with its own kernel and hardware-level isolation:
  heavier, but the guest can't reach the host filesystem through a container
  escape. Use it for a stronger wall around what the agent can touch on disk.

Neither is a jail for genuinely hostile code — see **Security posture** below.

## Install

```sh
cd qemubox
make install
```

`make install` copies the script to `~/.local/bin`, then runs `qemubox
build-base` once to bake the guest's apt packages into a reusable base image
(`provisioned.qcow2`) so every later box boots in seconds instead of spending
1-2 min on first-boot `apt-get`. The prebuild needs `/dev/kvm` and network; if
either is missing it is skipped with a warning and the binary still installs —
the first box then provisions lazily. Rebuild with `qemubox build-base --force`.

System packages:

```sh
# Debian / Ubuntu
sudo apt install qemu-system-x86 qemu-utils cloud-image-utils openssh-client curl tar
# Arch
sudo pacman -S qemu-base cloud-image-utils openssh curl tar
# Fedora
sudo dnf install qemu cloud-utils-cloud-localds openssh-clients curl tar
```

KVM acceleration needs `/dev/kvm`. Without it qemubox falls back to slow
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
through untouched, so a command taking a path argument stays intact. The default VM name is the project dir
basename; `-n name` gives a separate box.

Management:

```sh
qemubox ls               # list NAME STATUS USE RAM DISK PATH
qemubox status repo      # readiness of one VM (process/ssh/boot) without a shell
qemubox rm repo          # remove one VM by exact name
qemubox rm 'repo-*'      # remove by glob (only * or ? trigger glob matching)
qemubox rm -a            # remove all VMs (bare `rm` refuses; -a or '*' means all)
qemubox prune [hours]    # remove old stopped VMs and running idle VMs past 4h
qemubox build-base       # (re)bake the prebuilt base image
```

## Lifecycle

A box starts on first use and powers off when the **last** session exits
(counted by session markers). The disk stays on the host; the next launch
boots that disk and keeps files in the guest home. `qemubox rm` deletes it.
A missing recorded base image refuses launch with a `qemubox rm` hint.
Re-entering a running box from a second terminal
joins the live VM; it stays up until every session has exited, so concurrent
sessions don't tear it down under each other. The tool/model applies to the
new session, but mount flags (`-v`, dirs, network) are fixed at boot and are
ignored on re-entry — use `-n <name>` for a separately-mounted box.

The per-VM lock covers setup, session markers, shutdown and removal.
A new session waits for full guest readiness before it runs.
`QEMUBOX_READY_TIMEOUT` sets the wait limit in seconds (default 180);
a timeout prints the serial log tail. HUP and TERM remove the session marker.
A failed marker listing keeps the VM up and reports an error.

`ls` shows busy/idle from session markers, QEMU resident RAM, and the overlay
space allocated on the host (both sizes in KiB). `rm` accepts several names
or globs, with or without the `qemubox-` prefix, and fails if removal fails.
`prune [hours]` removes stopped VMs after that many hours (default 2160).
Running VMs need four hours since readiness and no sessions before pruning.

## Build directories

`node_modules`, `.next`, `.turbo` and `.cache` directories found under each
project become empty tmpfs mounts owned by the guest user. Discovery stops at
depth 4 and prunes each match, so nested dependency trees get one mount.
Only directories present at launch are overmounted.

`-P` / `--no-ephemeral` keeps project build directories on the host.
`-T` mounts directories backed by the guest disk over those paths.
Both modes keep `/tmp` and `/tmp/cargo-target` on tmpfs, with
`CARGO_TARGET_DIR=/tmp/cargo-target` in each session. Guest disk build data
and tmpfs data disappear when the VM is removed. A failed mount stops launch.

## What crosses into the VM

qemubox mounts two things and nothing else from your home:

1. **Your project dir(s)** — 9p-mounted at their real host paths, read-write,
   including `.git`. `-v path` adds an extra read-only mount, `-v path:rw` a
   read-write one. `-N` runs an empty VM with no project mount.
2. **Your agent config** — `~/.claude`, `~/.codex`, `~/.agents` (settings,
   credentials, skills, plugins, all project histories) are mounted read-write
   at their host paths. Guest edits reach the host, and absolute skill links
   resolve because the guest has the host username, UID, GID and home path.

The rest of `$HOME` is never mounted: no `~/.ssh`, no cloud credentials, no
other projects. `~/.gitconfig` and gpg **public** keyrings are staged read-only.
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
and forces the network off, while still mounting the project dir(s), so you can
shell in and build/test code you don't trust. The agent can't authenticate with
no credentials, so `-U` is for `bash`/build/test, not for running the agent.

## Security posture

What qemubox gives you:

- **Host-filesystem confinement.** The guest is a real VM with its own kernel;
  it can only touch the project dir(s) you mount and its own disposable disk.
  Your `~/.ssh`, cloud creds, and other repos are never mounted.
- **Disposability.** The disk is a throwaway qcow2 overlay; builds, installs,
  and guest files vanish when `qemubox rm` removes the VM.

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

So the honest claim: qemubox confines **host-filesystem blast radius** and gives
a **disposable, no-pollution** environment. For code you actively distrust,
combine `-U` (no credentials injected) with the disposable VM — but note the
in-guest agent can't authenticate without credentials, so that mode is for
shelling in and building/testing, not for running the agent.

## Configuration

State lives in `~/.local/share/qemubox` (override with `QEMUBOX_HOME`). The base
image is kept for reuse; `rm` deletes a box's overlay, seed, key, known-hosts,
pid, and serial log. `QEMUBOX_BASE_URL` picks a different base image.

```sh
QEMUBOX_MEM=8192 QEMUBOX_CPUS=4 qemubox -n big .   # bigger VM
```
