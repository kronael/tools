# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN

### proposed: wisdom minimization sweep — void a second time, prompt leaked

Both attempts measured nothing. The first asked subagents, which are handed
`~/.claude/CLAUDE.md` before their first token. The second used an isolated
clean room — that part worked, and the probe proved it — but the prompts named
our own rules as the topics to cover, so the models were completing a list I
had copied out of the files.

The `p-sys` prompt asked the model to cover "adding a mechanism when a similar
one may already exist; how errors on a user-facing path must behave; when
retrying is legitimate and when it is not; whether to address a symptom or its
cause; and how to handle a fix that turns out to require a redesign" — the five
System-change bullets in order. The `p-design` prompt asked for "how to decide
between adding a branch or reshaping the problem so the edge case disappears",
which is the reframe rule verbatim, and "what to do with code you do not
understand", which is Chesterton's fence. Every "both models reproduced it"
verdict rests on that.

Cuts made on this evidence are reverted: `skills/global/SKILL.md` and
`skills/software/code.md` are back to their pre-sweep content, minus the
separately-requested `./tmp` removal.

A valid rerun needs a prompt that names only the domain — "the software-design
section", "the section on changing a system you did not write" — with NO list
of sub-topics, because any such list is our table of contents. Ask for whatever
the model thinks belongs there, then compare. A rule the model never thought to
mention is the finding; the earlier design measured only whether it could write
to a spec.

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
