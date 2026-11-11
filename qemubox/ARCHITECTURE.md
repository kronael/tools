# qemubox architecture

How a VM boots, where the boot time goes, and how `-K` signing reaches the
guest. Usage and flags: [README](README.md).

## Boot path

```
┌──────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│ qemubox launcher ├────►│ systemd user units   ├────►│ QEMU q35 with KVM    │
│ start_box        │     │ one virtiofsd/share  │     │ pinned kernel+initrd │
└──────────────────┘     └──────────────────────┘     └──────────┬───────────┘
         ▲                                                       │
         │                                            ┌──────────▼───────────┐
         │                                            │ initrd-init          │
         │                                            │ tini                 │
         │                                            │ guest-init           │
         │                                            │ sshd                 │
         │                                            └──────────┬───────────┘
         │  SSH: ready poll, env file, session                   │
         └───────────────────────────────────────────────────────┘
```

- `qemubox` starts one virtiofsd per share, then QEMU, as systemd user units.
- `Dockerfile.kernel` builds a pinned Linux with every needed driver built in;
  `kernel.fragment` holds the options. The initrd needs no modules.
- `initrd-init` mounts the base image read-only over virtiofs, overlays the
  persistent ext4 disk on it, and runs `tini`, which runs `guest-init`.
  The guest has no systemd.
- `guest-init` sets up the user, swap, `/tmp` and the shares, starts Docker and
  sshd, then writes `/run/qemubox/ready`.
- The launcher polls that file over SSH, asks QMP for the rest of the RAM,
  sends the session variables over SSH, then opens the session over SSH.

## Boot time

Full cold boot on the host, 2026-10-25, before the cuts below. Host KVM, QEMU
11.1, full image, 2 GiB boot RAM. Times count from QEMU start.

| Phase | Time |
|---|---:|
| Firmware and early setup, before Linux, inferred | about 0.8 s |
| Linux to `/init` | 1.99 s |
| `guest-init` to the ready file | about 1.0 s |
| Ready file to an authenticated SSH session | 0.76 s |
| Total to the ready file, best run | 3.79 s |

The ready file came at 3.8–5.5 s over all runs.

Cuts in place, measured 2026-11-11 in nested KVM: QEMU 11.1.2, the pinned
Linux 6.12.114, 4 vCPUs, a static test init with no disks, shares or network.
Time from QEMU start to the first output of init, median of 3 runs.

| Configuration | Median |
|---|---:|
| 2 GiB boot RAM | 1.93 s |
| Add `pci=lastbus=0` | 1.31 s |
| And 1 GiB boot RAM, as shipped | 1.10 s |

- `pci=lastbus=0` stops the kernel probing 255 absent PCI buses. That probe took
  448 ms in `pci_subsys_init`. ACPI and bridge enumeration still find every device.
- The VM boots with 1 GiB. After SSH starts, the launcher asks virtio-mem for
  the rest of `QEMUBOX_MEM` in 128 MiB blocks.
- `guest-init` creates only an Ed25519 SSH host key on a new disk: 7 ms,
  against 147 ms for `ssh-keygen -A`.

Not adopted:

| Option | Measured | Why not |
|---|---|---|
| qboot firmware | 95 ms faster | One more pinned build artifact for under 0.1 s |
| Direct `vmlinux` boot, PVH | 125 ms faster | Skips kernel address randomization |
| `microvm` machine | 2.5–2.8 s against 0.65–1.06 s for q35 to init, distro kernel, 2026-10-20 | QEMU did not exit at guest power-off; the shares and RAM growth use PCI devices |
| Swap set up beside user setup | not measured | Adds a background step to `guest-init` |
| Snapshot and restore | not measured | A restore can replay stale share state over newer host files |

A cold boot at about 1 s is not reachable with this design. A minimal guest
with the real devices took 2.19 s to a device-ready marker, before guest setup and SSH. Re-entering a
running VM skips the boot; `QEMUBOX_LINGER` sets how long a VM waits for the
next session.

Open cuts, largest first by the 2026-10-25 phases:

- SSH: the launcher opens at least three connections in sequence — ready
  poll, env file, session.
- `guest-init`: user and group setup, about 0.39 s, and swap, about 0.49 s,
  run on every boot.
- Before Linux: launcher, virtiofsd start, QEMU start and firmware are not
  timed apart.

## gpg signing with `-K`

```
host                                       guest
┌──────────────────────┐   ssh -R   ┌───────────────────────────┐
│ gpg-agent            │◄───────────┤ ~/.gnupg/S.gpg-agent      │
│ extra socket         │            │ gpg, git commit -S        │
└──────────────────────┘            └─────────────▲─────────────┘
┌──────────────────────┐  virtiofs  ┌─────────────┴─────────────┐
│ gpg --export         ├───────────►│ ~/.gnupg/pubring.kbx      │
│ hostcfg/.gnupg/      │  ro mount  │ link to /mnt/qemubox-home │
└──────────────────────┘            └───────────────────────────┘
```

- The forward uses the agent's restricted extra socket. The guest can sign and
  decrypt; the agent refuses secret-key export.
- The guest has no systemd, so `/run/user/<uid>` does not exist and guest gpg
  looks for its agent in `~/.gnupg`, where the forward lands.
- The launcher stages public keys with `gpg --no-armor --output - --export`.
  The export reads any host store, keyboxd included, and ignores `armor` and
  `output` in `gpg.conf`. Guest gpg detects the OpenPGP format under the
  keybox name.
- Signing also needs the host's `~/.gitconfig`; the launcher stages it beside
  the keys.
