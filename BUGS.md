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
  — plus in-container overlay needs CAP_SYS_ADMIN. So a two-layer split: **config** (`~/.claude`/`~/.codex`/`~/.agents` —
  settings, credentials, skills, plugins) is mounted read-only at
  `/mnt/qemubox-cfg` and copied into the guest's own home at startup
  (`setup_guest_runtime`), so guest edits to config never reach the host;
  **session data** (`~/.claude/projects` incl. auto-memory, `~/.claude/todos`,
  `~/.codex/sessions`) is mounted **rw** so recall/history persist past the
  disposable VM. The copy excludes the data dirs (they mount rw on top) and
  bulky indexes (sqlite, logs). Tools find everything at the normal paths.
  **dockbox TODO:** same shape — its home is already a fresh tmpfs, so copy
  config into the tmpfs home in `dockbox-init` while keeping the session-data
  dirs as live rw binds (today it binds whole `~/.claude`/`~/.codex` rw —
  `dockbox:12,18`).
- **DEFER — network confinement (`-H`).** The `restrict=on` path exists but no
  flag wires it (`qemubox:240,426`); `-H` is a no-op. Not needed for v1 per owner.

Fable review + owner live-run (2026-08-20) surfaced three real defects, all fixed:
- **9p modules not auto-loaded** — first `mount -t 9p` failed on real hardware
  with "unknown filesystem type '9p'". Debian cloud images ship but don't load
  them; `mount_host_paths` now `modprobe 9p 9pnet_virtio` before mounting.
- **`setup_guest_runtime` aborted on every fresh VM** — `sudo mkdir -p
  /usr/local/bin ~/.gnupg && chmod 700 ~/.gnupg` created `~/.gnupg` as root, so
  the un-sudo'd `chmod` hit EPERM under `set -e`. Split so `~/.gnupg` is made by
  the sandbox user.
- **cross-project auto-memory poisoning** (Fix B residual) — mounting all of
  `~/.claude/projects` rw let guest code plant a `projects/<other-slug>/memory/
  MEMORY.md` a future host session auto-trusts. Now scoped to the active
  project's slug only, matching the "only what's mounted, this project" promise.

## Status — 2026-08-21 — qemubox ref-counted lifecycle audit (commit 9299ba0)

Read-only trace, no VM boot available in this environment (no /dev/kvm, no
qemu). Scoped to `9299ba0` (dockbox-style auto-shutdown + exact-match `rm`)
plus a sanity check of `dockbox`'s sibling `rm` fix (`40ed352`).

- **QB-REMOVE-BOX-ORPHANS-LIVE-VM** (HIGH, correctness/resource) — `remove_box`
  (`qemubox:439`) does `stop_box "$name" || true` then unconditionally deletes
  `disk.qcow2`/`seed.iso`/keys/`pid`/the box dir (`qemubox:441-445`), even when
  `stop_box` confirmed via `kill -0` (`qemubox:430`) that the qemu process is
  still alive. Before `9299ba0`, `stop_box` did `exit 1` on that path, which
  killed the whole script before reaching the destructive `rm`s — the `|| true`
  was dead code. Now it actually executes: a stop timeout silently orphans a
  live, unreachable `qemu-system-x86_64` process (holding RAM/CPU/rw 9p mounts)
  invisible to `ls`/`rm`/`prune` since the bookkeeping dir is gone. Reachable on
  ordinary exit, not just manual `rm` — the automatic last-session teardown
  (`qemubox:728-730`) hits this same path every time. `stop_box`'s 30s grace
  (`qemubox:426`) is shorter than systemd's typical shutdown timeout (~90s), so
  a normal slow shutdown (dpkg mid-run, large rw 9p writeback) can trigger it,
  not just a hung guest. **Fix:** on `stop_box` failure, print the still-running
  PID and return before the destructive `rm`s — leave state so the leak is
  discoverable and killable, matching what `build_base`'s bare (unguarded)
  `stop_box` call already does (`qemubox:479`, aborts loudly instead).
  **[resolved 2026-08-21, 12b0cf5: `stop_box` escalates poweroff→SIGTERM→SIGKILL
  (90s systemd wait) so a wedged VM is killed not orphaned; `remove_box` returns
  without deleting if it still cannot die.]**
- **QB-SESSION-MARKER-RACE-ON-REENTRY** (HIGH, correctness) — re-entering an
  already-running box re-runs `mount_host_paths` / `provision_guest_packages` /
  `setup_guest_runtime` / `setup_guest_auth` (`qemubox:692-696`, several
  un-multiplexed SSH round-trips each) *before* dropping its ref-count marker
  (`qemubox:717-718`). A concurrent sibling session that exits during this
  multi-second window computes `left=0` (the new session hasn't registered
  yet) and tears the VM down mid-provision — exactly the concurrent-session
  case the ref-count design exists to protect. dockbox's `enter_session`
  (`dockbox:299-306`) drops its marker as the literal first step, before any
  work; qemubox has no equivalent ordering. **Fix:** move the
  `/run/qemubox/sess/$sid` marker creation to immediately after `start_box`,
  before `mount_host_paths`.
  **[resolved 2026-08-21, 12b0cf5: marker now dropped right after `start_box`,
  before provisioning.]**
- **QB-RM-REENTRY-NEW-MOUNT-TAG-MISMATCH** (MED, correctness — pre-existing,
  not introduced by `9299ba0`) — `mount_host_paths` reruns every invocation and
  `add_mount` assigns 9p tags fresh each run (`qemubox:250`), but a running
  qemu instance's `-virtfs` device set is fixed at whatever `start_box`
  originally launched with. A second invocation against the same running box
  that adds a new `-v` path or a different dir gets a tag the guest kernel has
  no channel for; the guest-side mount (`qemubox:358`, bare statement under
  `set -e`) fails hard with a low-level 9p error and aborts the script.
  `usage()` has no "re-entry" section documenting this, unlike dockbox's.
  **Fix:** document the constraint, or detect/warn when this invocation's
  mount set differs from what a running box was created with.
- **QB-REFCOUNT-SSH-FLAKE-ASSUMES-ZERO** (LOW, design — shared with dockbox,
  not a regression) — `left=$(ssh_plain_box ... || echo 0)` (`qemubox:727`)
  treats any ssh failure while counting remaining sessions as "0 remaining."
  Same pattern as `dockbox:308-309`, but riskier here since it crosses a real
  network/SSH hop to the VM rather than a local `docker exec`.

Checked and confirmed correct (not bugs): `stop_box`'s `exit 1`→`return 1`
composes fine syntactically with both its callers (`qemubox:439`, `:479`) — the
real defect is what `remove_box` does with a caught failure, not the
return-vs-exit change itself. `rm`'s exact-match/glob split (`qemubox:582-588`)
does not reproduce the old `staking-rewards`/`staking-rewards-facade`
over-match — `base` and dot-prefixed `.build` are correctly excluded (bash `*`
doesn't glob dotfiles) and never reach the session-tail lifecycle code, since
`build-base` exits before falling through to it. `build_base`/`ensure_box`
prebuilt-base selection (`backing_override` vs `provisioned.qcow2`) is
correctly guarded under `set -u` and doesn't interact badly with `rm`/lifecycle.
`note()`/`ssh_stream_box` output styling keeps every control-flow-relevant ssh
call (mount checks, 9p preflight, package marker, the `left` count) on
`ssh_plain_box`, unpiped — and `pipefail` in fact preserves exit status through
`ssh_stream_box`'s gutter pipe anyway (rightmost-nonzero rule), so the
"corrupts exit status" comment is overcautious but harmless. `dockbox`'s
`rm` fix (`40ed352`) is correct: exact match by bare-or-`dockbox-`-prefixed
name, glob only on `*`/`?`, `matched` bookkeeping and the "no match" message
all check out.

## Product audit follow-ups — 2026-08-21 (CEO + CTO evals)

Both audits: dockbox is production-sound for its honest scope; qemubox is a
stronger (hardware-virt) boundary but must NOT be trusted with genuinely hostile
code until the guest→host / egress channels close. New items beyond those
already listed above (network `-H`, gpg opt-in, `rm --all`, port entropy,
`flock`, base checksum, start-path orphan-kill):

- **Positioning, not a bug (fixed in docs):** the qemubox README oversells
  "inspecting untrusted repos." Both tools must inject real `~/.claude`/`~/.codex`
  credentials to work, so hostile guest code can exfiltrate tokens (worse with
  always-on network). README reworded to claim host-filesystem confinement +
  disposability, not credential-safety.
- **Credential-minimized `--untrusted` mode (proposal, sign-off).** A path that
  runs the box WITHOUT copying real API credentials (or with a scoped short-lived
  token) AND drops the rw auto-memory slug mount. This is what would actually make
  "look at a repo I don't trust" safe; today that use case leaks tokens and leaves
  a `projects/<slug>/memory/MEMORY.md` write channel the next host session trusts.
- **No behavioral tests on the security-load-bearing matrix.** `make test` is
  `bash -n` only; dockbox has no test target or CI. A one-line edit can silently
  flip a ro mount to rw with nothing to catch it. Proposal: a `bats` harness
  asserting the per-flag mount + forward matrix; wire dockbox into `make test`/CI.
- **qemubox duplicates dockbox's UX and is drifting.** Two `apply_flag`,
  `tool_cmd`, ls/rm/prune, lifecycle blocks kept in lock-step by hand; default
  model aliases already diverge. Proposal: factor the shared UX, or at least a
  test that diffs the two tool tables.
- **Observability: `qemubox status <name>`** reporting boot/SSH/9p readiness from
  the serial log without a shell (a wedged VM currently shows "running").

## Status — 2026-08-21 — robustness backlog shipped (a2d0537..43467d0)

Serial C1→C4 execution of the approved minimal plan. All code-verified
(`bash -n`, `make test`); live VM behavior still needs owner verification on
leto (no /dev/kvm here). Resolved:

- **`-H` egress kill-switch** (finding #2) — `-H` now sets `network=""`, wiring
  the existing `restrict=on` path. [b26dc50]
- **gpg opt-in `-K`** (finding #3) — `detect_gpg` (qemubox) and the gpg-agent
  socket mount (dockbox) fire only on `-K`; off by default. Public keyrings
  stay (not credentials). [b26dc50]
- **`-n` traversal guard** (finding #4) — `apply_flag n)` rejects
  `. .. base .build "" */*` in the main shell so `exit` stops the run. [b26dc50]
- **`copy_arg` colon truncation** (finding #9) — strips only a trailing
  `:rw`/`:ro`, so `-v` paths with a colon survive (matches dockbox). [b26dc50]
- **`--untrusted` / `-U` mode** (product follow-up) — injects no host
  config/credentials, forces network off, keeps project mounts; agent-can't-auth
  warned. [b26dc50]
- **port entropy + bind-test** (finding #6) — range widened to 10000-59999 and a
  connect-probe fails loud on a foreign listener. [0bbae8e]
- **`flock` + `prune` stat tolerance** (finding #7) — per-box `flock` around
  ensure/boot; prune skips a dir that vanishes mid-loop. [0bbae8e]
- **start-timeout orphan-kill** (finding #8) — a boot that never reaches SSH
  kills its daemonized qemu instead of orphaning it. [0bbae8e]
- **re-entry mount-tag mismatch** (QB-RM-REENTRY) — re-provisioning is skipped on
  re-entry (mounts fixed at boot, documented). [0bbae8e]
- **refcount ssh/exec flake** (QB-REFCOUNT / dockbox) — teardown only when the
  remaining-session count SUCCEEDS and is 0; an error keeps the box up. [0bbae8e]
- **base image checksum** (finding #9) — verify against Debian SHA512SUMS or a
  pinned `QEMUBOX_BASE_SHA512`; mismatch aborts. [43467d0]
- **`qemubox status <name>`** (product follow-up) — process/ssh/boot readiness
  from pidfile/port/serial without a shell. [43467d0]
- **behavioral tests + no-drift guard** (product follow-up) — sourceable helpers
  behind `QEMUBOX_LIB`/`DOCKBOX_LIB`; `qemubox/test.sh` (37), `dockbox/test.sh`
  (11), `tests/drift_test.sh`; both tools wired into `make test` + CI. [a2d0537]

Still open (out of scope this pass):
- **`rm`/`prune` with no pattern matches all boxes** (finding #5) — owner accepts
  leaving it; no `--all` guard added.
- **Deferred, need sign-off:** stateful `$dir/port` persistence for auto
  port-reallocation (changes `port_for`'s contract); a shared sourced tool table
  (violates the "tools are independent, no imports" rule) — the drift *test* is
  the accepted guard instead.
