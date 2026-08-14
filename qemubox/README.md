# qemubox

Disposable QEMU VM for inspecting untrusted repos before running build tools.

It uses a Debian cloud image, a throwaway qcow2 overlay, cloud-init SSH keys,
and localhost-only SSH forwarding. No host directories are shared into the VM.
Guest networking is restricted by default: SSH works through the forwarded port,
but the guest cannot initiate normal outbound connections.

## Install

```sh
cd qemubox
make install
```

System packages on Debian:

```sh
sudo apt install qemu-system-x86 qemu-utils cloud-image-utils openssh-client curl
```

## Use

```sh
qemubox                    # copy current dir, open bash in the VM
qemubox ~/src/repo         # copy a repo, open bash there
qemubox cargo test .       # run a command in the copied current dir
qemubox sh                 # re-enter the project VM
qemubox ssh                # raw SSH into the project VM
qemubox ls
qemubox rm repo
```

Like `dockbox`, the default VM name keys off the project directory basename;
use `-n name` for a separate box. Unlike `dockbox`, source is copied over SSH
instead of bind-mounted, so untrusted code cannot write back to the host tree.
Use `-N` for an empty VM with no project copy.

State lives in `~/.local/share/qemubox` unless `QEMUBOX_HOME` is set. The base
image is kept for reuse; `rm` deletes the named VM overlay, seed, SSH key,
known-hosts file, pid file, and serial log.

Useful knobs:

```sh
QEMUBOX_MEM=8192 QEMUBOX_CPUS=4 qemubox -n big
QEMUBOX_BASE_URL=https://.../image.qcow2 qemubox -n other
qemubox -H .               # allow outbound network for apt/cargo downloads
```
