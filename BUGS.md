# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN

### dockbox repoints the host's `~/.codex/AGENTS.md` at the container home

The dockbox entrypoint symlinks `~/.codex/AGENTS.md` → `$HOME/.claude/CLAUDE.md`
with the container's `HOME=/home/dockbox`. `~/.codex` is bind-mounted from the
host, so the symlink is written on the HOST and dangles the moment the container
exits — the host's Codex loses its global guidance silently, with no error at
any point. Seen after a dockbox run on 2026-09-15; the install step repaired it.

The cause fix is for the entrypoint to write the link only inside a
container-private `~/.codex`, or to skip it when the directory is bind-mounted.
Reproduce: run dockbox, then `readlink -f ~/.codex/AGENTS.md` on the host.

### proposed: split `skills/global/SKILL.md` — 238 lines against a 200 cap

`skills/wisdom/SKILL.md` sets the cap at 200 with "no exceptions — overflow
goes to sibling files". The wisdom file is the one file loaded in every
session, so the cap matters here most. The measured cuts took it from 270 to
234, stressing the rules models state and break put it back to 248, and the
refine pass trimmed the duplication with `caveman.md` to reach 238.

The fix is the router pattern: keep the always-true rules inline and move a
themed block to a sibling loaded on demand. That changes what is guaranteed
present in every session, so it needs sign-off. Reproduce:
`wc -l skills/global/SKILL.md`.

### wisdom minimization sweep — rerun, and the answer is "cut almost nothing"

Fourth and final run, under the corrected method: clean room falsified first
(the same probe returns `YYYYMMDD_<tag>` and `<repo-root>/.<name>` without
isolation, `feature/add-login` and "sibling, not nested" with it, so it can
detect a leak), domain-only prompts, two models, and the behaviour question
asked PER TOPIC instead of once.

The cuts are reverted and should stay reverted. Every rule the earlier sweep
marked reproducible is confessed-violated by at least one model on its own
topic:

- Fail loud. sonnet: "I default to logging-and-swallowing when I'm not sure
  what the right recovery is, which is usually wrong." fable: "I log and
  continue, and I know this quietly swallows bugs that should have crashed",
  and "when I must choose between failing loudly and degrading gracefully, I
  lean toward graceful, which is the wrong default."
- No duplication. sonnet: "I check whether the codebase already has an
  error-reporting convention... but only after being told once that I'd
  invented a parallel logging path."
- Fix causes. sonnet: "I over-index on the specific input that triggered the
  bug report and under-cover the sibling cases that fail the same way."
- Mock boundaries. fable: "I sometimes over-mock to the point where the test no
  longer proves anything."
- Never skip the checks. fable: "my default impulse when a test I broke is
  annoying is to reach for editing the assertion."
- The make-target names. sonnet: "I assume the test command is whatever the
  README implies, without checking if that's actually how CI runs it."
- Zero comments, never restate WHAT. fable: "I write a comment above almost
  every non-trivial block, and about half of them just restate the code; I know
  this and still do it on the first pass."

The lesson is not that the measurement was contaminated this time — it was
clean. It is that "both models produce this rule" was never a sufficient
criterion. Knowing a rule and following it are different properties, and only
the second one decides whether a file needs to carry it.

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

### create/social references narrate their own edit history

`skills/create/social/references/research-social-meme.md:196-217` carries a
"Corrections (post-codex)" section describing what the document itself changed
("Modes collapsed 4 → 3", "Folklore cut", "Transferability test added"), and
`references/codex-critique.md` is framed as a verbatim audit trail of a review
pass. Both are the pattern the wisdom file bans: prior-version narration inside
permanent content. They are cold provenance files, not instructions, so nothing
reads them by accident — the call is whether they stay as attribution material
or move to `.diary/`. Needs the maintainer's decision, not a silent rewrite.

### hooks/Makefile: the comment above `TEST_FILES` states a fixed cause

The comment reads "Some hook scripts still read stdin at import time, so
collect only files known to be pytest-safe." That is no longer why the list is
narrow — `local.py` and `reclaude.py` both read stdin inside a function and
guard `main()` behind `__name__ == '__main__'`. They are absent from
`TEST_FILES` because no `test_local.py` or `test_reclaude.py` exists.

The comment sends a reader hunting an import-time bug that is not there, and
it hides the real trap: the list is explicit, so a new `test_*.py` is skipped
in silence until someone adds it. Reproduce: `grep -n '__main__' hooks/local.py
hooks/reclaude.py`.

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
