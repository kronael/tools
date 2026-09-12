# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN

### proposed: wisdom minimization sweep — cut what a blank-context model reproduces

Method: for each normative (not workflow) block, a fresh sonnet and a fresh
fable with no repo access were asked to write that guidance from scratch.
Anything both reproduced is costing always-loaded context to say what the model
already does. Anything neither reproduced — especially anything that
CONTRADICTS what both defaulted to — is the guidance actually earning its
place. Round 1 covered two blocks.

**Round 1a — `skills/global/SKILL.md` § Response Style (lines 48-82).**
Both models independently reproduced: lead with the answer; ~12 default and
hard cap 20 lines; one-sentence replies are fine; last line is the bottom line
(fable gave the phone rationale unprompted); no headers/tables; never restate
the request; never close with "let me know"; don't narrate what the diff shows;
cut padding; act without asking on anything reversible and state the
assumption; ask only when irreversible or genuinely ambiguous; say done only
for work verified this turn; correct without apologising; the cap lifts for
specs/plans/walkthroughs. Fable also reproduced the ~5-item list cap and, near
verbatim, "a subagent's report is a claim, not evidence — check its diff".

That is the whole section. Cut proposal: reduce § Response Style to the pointer
at `output-styles/caveman.md` plus only what neither model produced — the
keep-the-full-analysis guard, simple words, restate progress on multi-turn
work, minute-level effort estimates, one thread at a time, the first/last-line
pre-send check, and numbered one-action-per-item steps. Every one of those
survivors already lives in `caveman.md`, so the section may collapse to the
pointer alone.

Load-bearing survivor worth naming: "ALWAYS keep the full analysis and
verification; brevity applies to the reply". NEITHER model produced any guard
against terseness degrading the thinking — they optimised the reply and left
the reasoning unprotected. That is the rule holding the whole style together.

**Round 1b — `skills/software/code.md` §§ Naming, Layout, Comments.**
Reproduced by both, so dead weight: shorter names / no scope repetition; the
80-100 column range; "comment the WHY never the WHAT"; "never restate what the
code does". The wisdom file's "NEVER reference an earlier version in a comment"
was also reproduced by both, in `code.md`'s neighbourhood — check
§ Documentation before keeping it there.

Not in `code.md` and reproduced by both, so correctly absent — do not add:
file/function length caps, formatter deference, import grouping, nesting-depth
caps, blank-line and trailing-whitespace rules, no-commented-out-code, no
section banners, TODO-needs-an-owner.

Earning their place, because neither model produced them: the entrypoint is
always `main`; short file extensions and short CLI flags; the permissive
single-letter list with the `o O l I` ban; never rename something that already
has a name; discard with a bare `_`; never write under `/tmp`; lowercase info
and Capitalized errors with the Unix log format; stdout/stderr only, never file
log handlers.

Earning their place HARDER, because both models actively defaulted the other
way — these override a strong prior and are the highest-value lines in the
file: ZERO comments by default (both treated comments as normal and mandated a
doc comment on every exported symbol); at most ONE line (both wanted more);
NEVER a multi-line block, no `///` or `/** */` (both mandated exactly those);
NEVER a ticket or issue ID in a comment (both wanted issues linked); and the
redundancy test's clause about a log or error message on a neighbouring line.

One conflict to settle, not a cut: `code.md` mandates `*_utils.*` filenames
while both models ban `utils`/`helper`/`manager` as names that say nothing.
Either the rule is wrong or it needs the reason it overrides that default.

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
