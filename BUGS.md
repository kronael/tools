# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN

### dockbox: mirror qemubox's config copy-in (TODO)

dockbox still bind-mounts the whole `~/.claude` / `~/.codex` **rw** into the
container (`dockbox:12,18`), so guest edits reach the host. qemubox got the
two-layer treatment in v0.3.72+ (agent config copied read-only → guest-writable;
only the active project's session data mounted rw). Mirror it in dockbox: its
home is already a fresh tmpfs, so copy config into the tmpfs home in
`dockbox-init` while keeping the session-data dirs as live rw binds. Lower
priority — dockbox's README already discloses it is not a boundary for hostile
code.

### Deferred — need sign-off

- **Port auto-reallocation.** qemubox uses a stateless name-hash port plus a
  bind-test (v0.3.75). True reallocation on collision needs persisting
  `$dir/port`, which changes `port_for`'s contract. Do only if collisions
  actually bite.
- **qemubox / dockbox shared-UX de-dup.** The two tools duplicate flag parsing,
  the tool/model table, `ls`/`rm`/`prune`, and the lifecycle block. A shared
  sourced file would violate the repo's "tools are independent, no imports"
  rule (`CLAUDE.md`); `tests/drift_test.sh` is the accepted lightweight guard
  instead. Revisit only with sign-off.

## ACCEPTED — won't fix

- **`rm` / `prune` with no pattern matches all boxes.** Bulk-clear is intended;
  owner accepts. No `--all` guard.

---

Resolved items are pruned to `.diary/` (20260818–20260821) and `CHANGELOG.md`
(v0.3.72–v0.3.75): the 2026-08-18 qemubox security audit (whole-`$HOME` mount,
`-H` egress, gpg opt-in, `-n` traversal, port entropy, `flock`, start-orphan /
wedged-`rm`, base checksum, `copy_arg`), the mount-confinement redesign (curated
staging + config copy-in + per-slug session data), the 9p/genericcloud boot
fixes, the ref-counted-lifecycle audit, the CEO/CTO follow-ups (honest READMEs,
`-U` untrusted mode, behavioral tests + CI, `status`), and the robustness
backlog (`a2d0537..43467d0`, `91f91a8`). The install/skill items (trufflehog
release binary, `/hacker-eval`→`/red-eval`, prune list) shipped in `ce7c39a`.
