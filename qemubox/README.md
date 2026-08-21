# qemubox

A throwaway QEMU VM where a coding agent works on your project without writing
to the rest of your machine.

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
qemubox -v ~/src/lib .     # extra read-only mount (:rw for read-write)
qemubox -N bash            # empty VM, no project mount
```

`qemubox [tool] [dirs] [args]`. The first bare (non-path) argument is the tool:
`claude` (default, opus @ xhigh), `haiku` / `sonnet` / `opus` / `fable` for
Claude models, `codex` / `gpt` / `mini` / `spark` for Codex, `bash` / `zsh` for
a shell, or any binary in the VM. The default VM name is the project dir
basename; `-n name` gives a separate box.

Management:

```sh
qemubox ls               # list VMs (name, status, SSH port, path)
qemubox rm repo          # remove one VM by exact name
qemubox rm 'repo-*'      # remove by glob (only * or ? trigger glob matching)
qemubox prune [hours]    # remove stopped VMs older than N hours (default 2160)
qemubox build-base       # (re)bake the prebuilt base image
```

## Lifecycle

A box starts on first use and auto-shuts-down when the **last** session exits
(ref-counted, like dockbox). Re-entering a running box from a second terminal
joins the live VM; it stays up until every session has exited, so concurrent
sessions don't tear it down under each other.

## What crosses into the VM

qemubox mounts two things and nothing else from your home:

1. **Your project dir(s)** — 9p-mounted at their real host paths, read-write,
   including `.git`. `-v path` adds an extra read-only mount, `-v path:rw` a
   read-write one. `-N` runs an empty VM with no project mount.
2. **Your agent config** — `~/.claude`, `~/.codex`, `~/.agents` (settings,
   credentials, skills, plugins) are mounted read-only, then **copied** into the
   guest's own writable home, so guest edits to config never reach the host.

The rest of `$HOME` is never mounted: no `~/.ssh`, no cloud credentials, no
other projects. Only a few single files (`~/.claude.json`, `~/.gitconfig`,
`~/.dockbox_history`, gpg **public** keyrings) are staged into a per-box
read-only dir and linked in.

One thing persists past the throwaway VM: the **active project's**
`~/.claude/projects/<slug>` (transcripts + auto-memory) is mounted read-write so
recall survives. Only that one slug is mounted — the guest can't see or write
any other project's history.

Each VM gets its own SSH key on a localhost-only forwarded port, so guests can't
reach or log into each other. `-A` forwards your SSH agent, `-D` the Docker
socket, `-G` mounts `~/.config/gcloud` ro, `-g` forwards `GH_TOKEN`/`GITHUB_TOKEN`.

## Security posture

What qemubox gives you:

- **Host-filesystem confinement.** The guest is a real VM with its own kernel;
  it can only touch the project dir(s) you mount and its own disposable disk.
  Your `~/.ssh`, cloud creds, and other repos are never mounted.
- **Disposability.** The disk is a throwaway qcow2 overlay; builds, installs,
  and any mess vanish when the VM shuts down. No host pollution.

What it does **not** give you — do **not** run genuinely hostile code here:

- **Your real agent credentials are injected.** Like dockbox, qemubox copies
  your live `~/.claude` / `~/.codex` (tokens included) in so the agent can work.
  Hostile guest code can read and exfiltrate those tokens.
- **Outbound network is always on.** `-H` is currently a no-op (accepted for
  dockbox muscle-memory only) — there is no egress kill-switch today, so the
  path for exfiltration is open.
- **In-guest agents run with permission checks bypassed**
  (`--dangerously-skip-permissions` / `--dangerously-bypass-approvals-and-sandbox`)
  and the guest user has passwordless sudo.

So the honest claim: qemubox confines **host-filesystem blast radius** and gives
a **disposable, no-pollution** environment — not a boundary against code actively
trying to steal your credentials. Tracked hardening (network kill-switch, gpg
opt-in, a credential-minimized `--untrusted` mode) is in [`../BUGS.md`](../BUGS.md).

## Configuration

State lives in `~/.local/share/qemubox` (override with `QEMUBOX_HOME`). The base
image is kept for reuse; `rm` deletes a box's overlay, seed, key, known-hosts,
pid, and serial log. `QEMUBOX_BASE_URL` picks a different base image.

```sh
QEMUBOX_MEM=8192 QEMUBOX_CPUS=4 qemubox -n big .   # bigger VM
```
