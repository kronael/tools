# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## install: `go install ...trufflehog/v3@latest` fails (replace directives)

`kronael/install/reference.md` § "External tool commands" (Security audit)
installs `trufflehog` via `go install github.com/trufflesecurity/trufflehog/v3@latest`.
That fails: its `go.mod` contains `replace` directives, so `go install` refuses
("must not contain directives that would cause it to be interpreted differently
than if it were the main module"). Fix: install the release binary like gitleaks
— `linux_amd64.tar.gz` from github.com/trufflesecurity/trufflehog/releases into
`~/.local/bin`. Found 2026-07-21 during a full "install all tools" run; worked
around with the release binary (v3.95.9) so the install completed.

## install: prune list omits eye-13yo/hacker-eval/testing renames

The v0.3.67 renames — `eye-13yo`→`13yo-eval`, `hacker-eval`→`red-eval`,
`testing` folded into the `software` router — were never added to the
removed-skills prune list in `kronael/install/`. Reinstalls therefore leave the
old dirs as orphans in `~/.claude/skills/` (the descriptions keep preloading).
Per `skills/CLAUDE.md`, a removed/renamed dir MUST be added to that prune list.
Fix: add the three to the prune list. Found 2026-08-05 during "sync and install
all" (the three orphans were pruned by hand).

## install: reference.md security tools still cite /hacker-eval (now /red-eval)

`kronael/install/reference.md` security-audit table lists bandit, pip-audit,
semgrep, govulncheck, trufflehog, gitleaks as serving `/hacker-eval`, but that
skill was renamed to `red-eval` in v0.3.67. Fix: update the Skills column to
`/red-eval`. Found 2026-08-05.

## qemubox: security + robustness audit (2026-08-18, fable, all lines verified)

`qemubox` is sold as a disposable sandbox for untrusted repos, but its mount
contract makes it a non-boundary. Ranked; not fixed (record-don't-fix). Each
line ref checked against the source.

1. **CRITICAL — host secrets exposed + guest→host persistence.** `qemubox:538-542`
   mounts the whole `$HOME` ro at `/mnt/qemubox-home` and `~/.claude`, `~/.codex`,
   `~/.agents` **rw**, unconditionally, every run. `security_model=none`
   (`qemubox:223`) means guest file ops use the *host* UID, so guest writes land
   as the host user. Guest has passwordless root (`:148`), the in-guest
   `claude`/`codex` run with `--dangerously-skip-permissions` /
   `--dangerously-bypass-approvals-and-sandbox` (`:337,341`), and outbound
   network is always on (see #2). Result: untrusted guest code reads
   `~/.ssh/*`, `.aws/credentials`, every project's `.env`, and can plant a
   malicious hook/`settings.json`/`CLAUDE.md` into the real `~/.claude` that the
   host Claude session later trusts and executes. Fix: never mount raw `$HOME`;
   symlink only the specific dotfiles; make `~/.claude`/`~/.codex`/`~/.agents` ro.
2. **HIGH — networking can't be disabled; `-H` is a no-op.** `network=1` default
   (`:14`), `restrict=""` only when `network` is empty (`:240`) — nothing ever
   empties it, so the `restrict=on` path is dead code. `-H` sets `network=1`
   (`:426`). Fix: make `-H` set `network=""`.
3. **HIGH — GPG agent forwarded on every run, no opt-out.** `detect_gpg`
   unconditional (`:555`); `ssh_box` forwards the socket whenever present
   (`:177`). Unlike `-A`/`-D`/`-G` (opt-in), GPG is always on. Fix: gate behind a
   flag, off by default.
4. **HIGH — `-n` path traversal.** `box_name` (`:88`) keeps `.` (only filters via
   `tr -c`), so `-n ..` → `box_dir` = `$ROOT/..` (`:92`), `-n .` → `$ROOT`. Writes
   key/seed.iso/multi-GB disk.qcow2 loose above/into `$ROOT`, invisible to
   `ls`/`rm`/`prune` (all require `[ -d ]`). Reachable by typo or CI deriving
   `-n` from repo data. Fix: reject `.`/`..`/empty explicitly.
5. **MEDIUM — `qemubox rm` with no pattern wipes ALL VMs** (incl. running).
   `:472` — empty `pat` short-circuits the skip. Fix: require `--all`.
6. **MEDIUM — predictable low-entropy SSH ports.** `2200 + cksum%1000` (`:95-98`)
   — 1000 ports, name-deterministic: collisions (~30 boxes) and local
   port-squatting DoS. No auth bypass (per-box key). Fix: wider range + bind-test.
7. **MEDIUM — no locking; `prune` crashes on a vanishing dir.** No `flock`
   anywhere; concurrent same-name runs race `ssh-keygen`/`qemu-img` (`:135,158`).
   In `prune`, if a dir disappears between glob and `stat`, both `stat`s fail and
   the plain assignment trips `set -e` (`:492`), aborting the whole prune. Fix:
   `flock` per-box + tolerate stat failure.
8. **MEDIUM — failed start orphans qemu; wedged VM can't be removed.** Start
   daemonizes then `exit 1` on SSH timeout leaving qemu running (`:259,268`);
   `stop_box` uses `exit 1` not `return 1` (`:361-364`), so `remove_box`'s
   `stop_box || true` (`:370`) can't catch it — `rm` aborts, files stay. Fix:
   `return 1` from `stop_box`; `kill "$pid"` on start timeout.
9. **LOW — base image has no checksum/GPG verification** (`:123`). **LOW —
   `copy_arg` truncates `-v` paths at the first colon** (`:407`).

Checked safe (not bugs): `%q` quoting is consistent (`:199,294,572`); `add_env`
`eval` is guarded by a strict charset check (`:398`); per-box `known_hosts`
(`:184`); `-A`/`-D` are disclosed opt-in trades.

## qemubox/dockbox: confine mounts to the dockbox contract (2026-08-19)

Plan for finding #1. dockbox already does this right: its guest `$HOME` is a
fresh tmpfs (`dockbox:410`) with only a curated bind list nested in
(`dockbox:11-18`) — it never mounts the whole host home. qemubox's
`add_mount "$HOME" "/mnt/qemubox-home" ro` (`qemubox:538`) is the sole
divergence, and it exists only to feed the 5 single-file configs the guest
links (`setup_guest_runtime:345-349`).

- **FIX A — curated host-home mount (implementing 2026-08-19, qemubox only).**
  Replace the blanket `$HOME` 9p mount with a per-box staging dir holding only
  `.claude.json`, `.gitconfig`, `.dockbox_history`, and the gpg public keyrings,
  9p-mounted ro at `/mnt/qemubox-home`. Mirrors dockbox's file set; the guest can
  no longer read `~/.ssh`, cloud creds, or other repos. Keeps `~/.claude` /
  `~/.codex` / `~/.agents` rw (matches current dockbox).
- **FIX B — config isolated via copy-in (DONE qemubox 2026-08-19; dockbox TODO).**
  Guest code must not persist a hook/`settings.json` back onto the host, but a
  *pure* read-only mount breaks codex (writes sqlite state at startup) and claude
  (token refresh, transcripts). Overlay copy-on-write was ruled out: the kernel
  overlayfs docs disallow network filesystems as the upper layer, and virtio-fs
  confirms overlay-on-9p/virtiofs fails ("upper fs does not support tmpfile/xattr")
  — plus in-container overlay needs CAP_SYS_ADMIN. So: mount `~/.claude`/`~/.codex`/
  `~/.agents` **read-only** at `/mnt/qemubox-cfg`, then copy into the guest's own
  writable home at startup (`setup_guest_runtime`), excluding bulky/other-context
  state (sqlite, `sessions/`, `projects/`, logs). Host stays read-only; guest
  writes stay in the disposable VM; tools find config at the normal paths.
  **dockbox TODO:** same shape — its home is already a fresh tmpfs, so mount the
  three dirs ro to a staging path and copy them into the tmpfs home in
  `dockbox-init` instead of the current live rw binds (`dockbox:12,18`).
- **DEFER — network confinement (`-H`).** The `restrict=on` path exists but no
  flag wires it (`qemubox:240,426`); `-H` is a no-op. Not needed for v1 per owner.
