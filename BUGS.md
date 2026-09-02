# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN

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

### [proposal] wire the ast-grep lint pack into target repos (cross-repo install)

The lint pack (`skills/<lang>/lints/`, aggregated by `sgconfig.yml`, proven by
`make lints`) enforces code rules only in THIS repo. Getting it into a user's
project is a new install contract — a redesign needing sign-off before ship.
Options (see `.ship/plan-skills-as-lints.md` § Distribution):
- **A (recommended)**: opt-in install step — "wire kronael lints into this
  repo?" writes/updates the project's `sgconfig.yml` + `.pre-commit-config.yaml`
  and references the pack. Matches the opt-in-skills posture.
- **B**: publish the pack as a standalone `pre-commit` repo referenced by URL.
- **C**: document a `sgconfig.yml` reference only, no installer.
Also: CI enforcement here needs an ast-grep-provisioned job (`make lints` is not
in pre-commit because the lint CI runner has no ast-grep). Proposed 2026-08-20.

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

### [proposal] redirect.py rewrites commands on a bare substring match

`hooks/redirect.py:56-67` searches `\be2e\b`, `\bintegration\b`, `\bsmoke\b`,
`\bplaywright\b`, `\bcypress\b` anywhere in a Bash command and replaces the
whole command via `updatedInput`, with `permissionDecision: "allow"` so the
substitution skips the prompt. Executed in a uv project: `cat
docs/integration.md` becomes `uv run pytest tests/`; `grep -rn smoke .` becomes
`uv run pytest --smoke`; `pytest tests/test_x.py -k boom -x` becomes `uv run
pytest`, dropping every argument so a targeted test runs the whole suite.
`hooks/lib/toolchain.py:93` compounds it: `.PHONY:` plus the word "test"
anywhere in a Makefile — a comment counts — returns `make test`. The documented
escape hatch (`redirect.py:33`, prefix `!`) does not work: `bash -c '!make
test'` is `bash: !make: command not found`.

Currently inert: registered in no settings file. It is still copied to
`~/.claude/hooks/` by the install, and `specs/0-committer.md` proposes building
on it. Redesign, needs sign-off: anchor the detectors to the command head,
preserve arguments, fix or drop the escape hatch — or drop the file.

### [proposal] learn.py has written 1807 reports that all say "unknown"

`hooks/learn.py:21` reads `data.get("hook_event", "unknown")`, but Claude Code
sends `hook_event_name`, so every report is named `*-unknown.md`:
`~/.claude/flow-reports` holds 1807 files and 1807 of them end in `unknown.md`
(7.0 MB), never pruned. `:22` names files at one-second resolution, so two
invocations in the same second overwrite each other — reproduced. `:17` runs
`os.makedirs` at import with no guard, so an unwritable HOME is a traceback
before the `except OSError` at `:58` can run.

The hook is registered in no settings file, and the body it writes is a
constant template that records nothing about the session beyond timestamp,
session id and cwd. Redesign, needs sign-off: wire it and fix the key, or
remove it.

### [proposal] the CLAUDE_EVAL guard has no producer

`hooks/stop.py:120` suppresses the commit/diary block when `CLAUDE_EVAL` is
set. Nothing sets it: one hit in the whole repo, the consumer itself — not in
`Makefile`, `.github/`, `evals/`, or any `settings*.json` env block. Introduced
in `bfc2e0f` with no producer. Effect is the opposite of the intent: eval runs
get the block messages injected into their transcripts. Same shape as the
`KRONAEL_IN_CODEX` guard fixed in `0cb8b5a`. Fix is one line either way — set
it in the eval runner, or delete the clause — but which one is a scope call.

### [proposal] session state stamps accumulate forever

`hooks/lib/state.py:29` writes four stamps per session (`local-`,
`diary-nudge-`, `memory-nudge-start-`, `memory-nudge-done-`) and nothing ever
expires a session id. `~/.claude/state` holds 37 files today. Harmless in
bytes; the question is whether stamps should self-prune on write past N days.

### [proposal] humanize/SKILL.md is 629 lines against a 200-line cap

`make skills-frontmatter` warns: the body is 3.1x the cap, and `humanize` is
not in the linter's `LONG_SKILLS` allowance (`{install, ship}`). Skills persist
in context all session, so this is a standing context cost on every session.
It is an external skill vendored intact (it ships its own LICENSE and
Attribution section) and has no sibling files. Splitting the pattern catalogs
(lines 109-548) into on-demand siblings is a restructuring of imported content,
not a one-line fix.
