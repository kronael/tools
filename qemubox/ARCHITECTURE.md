# qemubox architecture

How a VM boots, where the boot time goes, and how `-K` signing reaches the
guest. Usage, flags and settings: [README](README.md).

## Boot runs launcher, systemd units, QEMU, then guest-init

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
  `kernel.fragment` holds the options. The initrd loads no modules.
- `initrd-init` mounts the base image read-only over virtiofs, overlays the
  persistent ext4 disk on it, and runs `tini`, which runs `guest-init`.
  The guest has no systemd.
- `guest-init` sets up the user, swap, `/tmp` and the shares, starts Docker and
  sshd, then writes `/run/qemubox/ready`.
- The launcher polls that file over SSH, asks QMP for the rest of the RAM,
  sends the session variables over SSH, then opens the session over SSH.
  The RAM split is in [README § Memory](README.md#memory).

## A cold boot took 3.8 s to the ready file

Measured 2026-10-25 on the host: KVM, QEMU 11.1, the full image, 2 GiB boot
RAM, no `pci=lastbus=0`. Times count from the start of the VM's systemd unit,
read from the host journal and the guest kernel log.

| Phase | Time |
|---|---:|
| Unit start to Linux start, inferred | about 0.8 s |
| Linux start to `/init` | 1.99 s |
| `guest-init` to the ready file | about 1.0 s |
| Ready file to an authenticated SSH session | 0.76 s |
| Unit start to the ready file, best run | 3.79 s |

The ready file came at 3.8–5.5 s over all runs.

## Three cuts shorten the boot

Measured 2026-11-11 in nested KVM: QEMU 11.1.2, the pinned Linux 6.12.114,
4 vCPUs, `-machine q35`, a static test init, no disks, shares or network.
Time from QEMU start to the first serial line of init, median of 3 runs.

| Configuration | Median |
|---|---:|
| 2 GiB boot RAM | 1.93 s |
| Add `pci=lastbus=0` | 1.31 s |
| Add 1 GiB boot RAM, as shipped | 1.10 s |

- `pci=lastbus=0` stops the kernel probing 255 absent PCI buses. With
  `initcall_debug`, that probe took 448 ms in `pci_subsys_init`. ACPI and
  bridge enumeration still find every device.
- `ensure_box` boots with 1 GiB when the image supports memory growth and the
  ceiling is 1152 MiB or more. The rest arrives after SSH starts.
- `guest-init` creates only an Ed25519 SSH host key, once per disk. Standalone,
  5 runs each in a qemubox guest: 7 ms, against 147 ms for `ssh-keygen -A`.

A cold interactive shell in about 1 s is unproven. In nested KVM, a minimal
guest with the real devices took 2.19 s to a device-ready marker, before
`guest-init` and SSH; one run, with qboot. Re-entering a running VM skips the
boot.

## Measured options not adopted

| Option | Measured | Why not |
|---|---|---|
| qboot firmware | 95 ms faster, nested KVM | One more pinned build artifact for under 0.1 s |
| Direct `vmlinux` boot, PVH | 125 ms faster, nested KVM | Skips kernel address randomization |
| `microvm` machine | 2.5–2.8 s to init against 0.65–1.06 s for q35, distro kernel, host, 2026-10-20 | QEMU did not exit at guest power-off; the shares and RAM growth use PCI devices |
| Swap set up beside user setup | not measured | Adds a background step to `guest-init` |
| Snapshot and restore | not measured | A restore can replay stale share state over newer host files |

## SSH round trips are the largest open cut

By the 2026-10-25 phases, largest first:

- SSH: the launcher opens at least three connections in sequence: the ready
  poll, the env file and the session.
- `guest-init`: user and group setup and swap setup run on every boot,
  about 1.0 s together with the rest of `guest-init`.
- Before Linux: launcher, virtiofsd start, QEMU start and firmware are not
  timed apart.

## `-K` forwards a restricted gpg-agent socket

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

- The forward uses the agent's extra socket. The guest can sign and decrypt;
  the agent refuses secret-key export.
- The guest has no systemd, so `/run/user/<uid>` does not exist and guest gpg
  looks for its agent in `~/.gnupg`, where the forward lands.
- The launcher deletes every staged `pubring.*`, then writes
  `gpg --no-armor --output - --export`. The export reads any host store,
  keyboxd included, and ignores `armor` and `output` in `gpg.conf`.
  Guest gpg reads the OpenPGP export under the keybox name.
- The launcher also stages the host `~/.gitconfig`, which carries git's
  signing settings.
