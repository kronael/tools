# qemubox

Disposable QEMU VM for inspecting untrusted repos before running build tools.

It uses a Debian cloud image, a throwaway qcow2 overlay, cloud-init SSH keys,
localhost-only SSH forwarding, and QEMU 9p mounts for host-backed paths.
Guest networking is enabled so first-boot package provisioning and agent tools
work like they do in `dockbox`.

## Install

```sh
cd qemubox
make install
```

System packages:

```sh
# Debian / Ubuntu
sudo apt install qemu-system-x86 qemu-utils cloud-image-utils openssh-client curl tar

# Arch
sudo pacman -S qemu-base cloud-image-utils openssh curl tar

# Fedora
sudo dnf install qemu cloud-utils-cloud-localds openssh-clients curl tar

# openSUSE
sudo zypper install qemu qemu-tools cloud-utils openssh-clients curl tar

# Alpine
sudo apk add qemu qemu-img qemu-system-x86_64 cloud-utils-localds openssh-client curl tar
```

KVM acceleration needs `/dev/kvm` access. Without it, qemubox falls back to
software emulation.

## Use

```sh
qemubox                    # mount current dir, run claude in the VM
qemubox ~/src/repo         # mount a repo, run claude there
qemubox haiku ~/src/repo   # dockbox-style Claude model alias
qemubox codex ~/src/repo   # dockbox-style Codex entrypoint
qemubox cargo test .       # run a command in the mounted current dir
qemubox bash               # re-enter the project VM with bash
qemubox -n mybox bash      # named VM shell
qemubox -A bash            # forward SSH agent
qemubox -D docker ps       # forward Docker socket
qemubox ls
qemubox rm repo
```

The command interface mirrors `dockbox`: first positional arg is the tool,
`haiku` / `sonnet` / `opus` / `fable` select Claude models, and `gpt` / `mini`
/ `spark` select Codex models. The default VM name keys off the project
directory basename; use `-n name` for a separate box.

Project dirs are mounted into the VM with QEMU 9p at their original host paths,
read-write, including `.git`. Use `-v path` for extra read-only mounts and
`-v path:rw` for extra read-write mounts. Use `-N` for an empty VM with no
project mount.

qemubox mirrors dockbox's agent surface in two layers. `/opt/dev-tools` is
host-backed read-only. Agent **config** — `~/.claude`, `~/.codex`, `~/.agents`
(settings, credentials, skills, plugins) — is mounted read-only then copied into
the disposable guest's own home, so guest edits to config never touch the host.
Agent **session data** — `~/.claude/projects` (transcripts + auto-memory),
`~/.claude/todos`, `~/.codex/sessions` — is mounted read-write so recall and
history persist past the VM. Bulky indexes (sqlite logs) are neither copied nor
mounted. Single-file config (`~/.claude.json`, `~/.gitconfig`, gpg public
keyrings) is copied into a per-box read-only staging mount — the guest never
sees the rest of your home (no `~/.ssh`, cloud credentials, or other projects).
`-G` mounts `~/.config/gcloud` read-only.

SSH agent forwarding uses `ssh -A`. GPG uses SSH Unix-socket forwarding for
`~/.gnupg/S.gpg-agent`. `-D` forwards `/var/run/docker.sock` over SSH to a
user-owned socket in the VM and sets `DOCKER_HOST`.

On first boot, qemubox installs the base Debian packages needed for normal
shell/git/gpg/runtime work. Agent entrypoints such as `claude` and `codex` run
through guest wrappers that point at the host-mounted `/opt/dev-tools` tree.

State lives in `~/.local/share/qemubox` unless `QEMUBOX_HOME` is set. The base
image is kept for reuse; `rm` deletes the named VM overlay, seed, SSH key,
known-hosts file, pid file, and serial log.

Useful knobs:

```sh
QEMUBOX_MEM=8192 QEMUBOX_CPUS=4 qemubox -n big
QEMUBOX_BASE_URL=https://.../image.qcow2 qemubox -n other
qemubox -H .               # accepted for dockbox muscle memory
```
