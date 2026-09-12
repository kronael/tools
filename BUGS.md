# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN

### proposed: wisdom minimization sweep — measured clean, domain-only prompts

Third attempt, and the first valid one. Isolation: throwaway `HOME`, empty cwd
(`skills/wisdom/clean-room.sh`). Prompt: the domain name alone, no list of
sub-topics, so the model chooses what belongs in the section. Two models,
sonnet and fable. Far less is reproducible than the leaked run claimed.

**Reproduced by both — these buy nothing.**
- Git mechanics: never `git add -A`/`git add .`; never `--no-verify`; prefer a
  new commit over `--amend`; never force-push; never push without being asked;
  never merge a PR, approve a review or close an issue; scan the staged diff
  for secrets; run the project's own test target found in the Makefile.
  Fable produced `<type>(<scope>): <imperative summary>` unprompted.
- Response openings and closings: no "Great question"/"Got it"/"Sure", no
  closing offer of help, no "hope this helps", never claim done without naming
  what verified it, cap an option list at three.
- Subagents: cap concurrency (fable said 4, exactly ours); brief with goal,
  scope and return shape; don't re-run a delegated search; check the skill
  listing before improvising and never guess a skill name.
- Testing hygiene: never delete or skip a failing test to go green; mock only
  external boundaries, never the module under test; name tests for the
  scenario and outcome; a flake is a bug, not something to retry past.
- "Comment the why, never the what."

**Produced by neither — this is what the files are for.**
- "ALWAYS keep the full analysis and verification; brevity applies to the
  reply." Measured three times now, never volunteered. Both models optimise the
  reply and leave the reasoning unguarded.
- The whole mobile-terminal discipline: a line budget at all, ending on the
  single most important point, the first/last-line check, minute-level effort
  estimates, simple words. Neither model gave a length rule this time, and
  neither said "lead with the answer".
- Detached HEAD, the dated `YYYYMMDD_<tag>` branch, and worktrees — neither
  model mentioned worktrees at ALL. They appeared in the earlier run only
  because the prompt named them.
- `NEVER add Co-Authored-By`: fable mandated its own trailer as the last line
  of every commit.
- Debug builds; build/test/lint every ~50 lines; the blanket `rm -r` ban, which
  both scoped to git commands only; never squash.
- Error surfacing on a user-facing path and the retry-only-transient rule did
  NOT appear on the modify-existing-code topic, though both surfaced on the
  code-style topic as `_ = err`/empty-catch bans. The redesign-needs-sign-off
  rule appeared nowhere.
- `code.md` comments: no multi-line block, no `///` or `/** */` — fable
  mandates a doc comment on every exported symbol, the exact opposite; the
  ticket-ID ban — sonnet wants "no TODO without an owner or issue link"; the
  log-message redundancy clause; no source line numbers; ZERO comments by
  default, which only sonnet approached.
- `code.md` design: boring-over-clever, the reframe-so-the-edge-case-disappears
  move, the three innovation tokens, "a simple solution mostly right beats a
  complex one fully correct", the data-over-objects combinatorics, and matching
  tool to task weight. None of it volunteered.
- Locality of behavior is CONTRADICTED by both: they mandate layered
  `domain/app/infra` splits, one reason to change per file, a README per
  package. Ours overrides a strong prior.
- Documentation: no marketing language, no claude.ai publishing, the `.ship/`,
  `.diary/` and `.claude/` layout, the UPPERCASE root convention. On comments
  the two models split — sonnet independently produced our zero-comments,
  ticket-ban and no-history rules; fable produced their opposites.

**The one real conflict, found in both runs.** Our "test features, not fixes —
skip the test unless the feature lacks coverage" is contradicted by both models
every time: "every bug fix ships with a regression test that fails without the
fix". It is either wrong or it needs its reason written down.

Nothing has been cut on this evidence. The last two attempts both produced
confident verdicts that were artefacts of method, so the cuts are proposals
until signed off.

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
