# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN

### proposed: split `skills/global/SKILL.md` — 270 lines against a 200 cap

`skills/wisdom/SKILL.md` sets the cap at 200 lines with "no exceptions —
overflow goes to sibling files, never a longer SKILL.md". The wisdom file is
270 and is the one file always loaded in every session, so the cap matters
here most. `plugins/kronael/skills/kronael-install/SKILL.md` is 247.

The fix is the router pattern: keep the always-true rules inline and move a
themed block (the git/workflow rules are the largest candidate) to a sibling
loaded on demand. That changes what is guaranteed present in context for every
session, so it is a redesign, not an edit — needs sign-off before anyone ships
it. Reproduce: `wc -l skills/global/SKILL.md`.

### root Makefile: per-project `test-%` targets are silent no-ops

`make test-dockbox` (and every other `test-<project>`) prints "Nothing to be
done" and runs nothing, so root `make test` reports "all tests passed" while
executing only `tests/drift_test.sh`. The `test-%:` pattern rule at
`Makefile:59` matches but its recipe never fires. `make -C <project> test` works
and is what CI calls, so CI coverage is intact — the gap is local-only.
Reproduce: `make test-dockbox`, `make -C dockbox test`.

### dockbox: guest-editable skills without exposing credentials (TODO)

dockbox bind-mounts the whole `~/.claude` / `~/.codex` **rw** into the container
(`dockbox:12,18`). The intent is that the guest can edit **skills**
(`~/.claude/skills`, `~/.agents`) — but it does NOT need read/write to the
**sensitive config** (the API tokens in `~/.claude`/`~/.codex`). Scope: keep the
skill dirs editable while keeping credentials out of the guest's reach (mount
them ro / redacted / not at all) — not a full config copy-in (that isn't
needed). Lower priority — dockbox's README already discloses it is not a
boundary for hostile code.

### Deferred — need sign-off

- **qemubox / dockbox shared-UX de-dup.** The two tools duplicate flag parsing,
  the tool/model table, `ls`/`rm`/`prune`, and the lifecycle block. A shared
  sourced file would violate the repo's "tools are independent, no imports"
  rule (`CLAUDE.md`); `tests/drift_test.sh` is the accepted lightweight guard
  instead. Revisit only with sign-off.

---

Resolved items are pruned to `.diary/` (20260818–20260821) and `CHANGELOG.md`
(v0.3.72–v0.3.75): the 2026-08-18 qemubox security audit, the mount-confinement
redesign (curated staging + config copy-in + per-slug session data), the
9p/genericcloud boot fixes, the ref-counted-lifecycle audit, the CEO/CTO
follow-ups, the robustness backlog (`a2d0537..43467d0`, `91f91a8`), and the
install housekeeping (`ce7c39a`). This pass: `rm` now requires an explicit
pattern (`'*'` = all) and qemubox persists its SSH port in `$dir/port`
(`d80c486`); dockbox toolchain bumped (`c04c956`).
