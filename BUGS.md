# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN

### proposed: wisdom minimization sweep — § Response Style, measured clean

Method and harness: `skills/wisdom/minimize.md`. Isolation is a throwaway
`HOME` so no wisdom file loads and an empty cwd so no project `CLAUDE.md` is
discoverable; both models volunteered that no project conventions were
discoverable, and the verification probe returned `feature/add-login` and
"worktree as a sibling, not nested inside it" — the field defaults, and the
opposite of this repo's rules. The room is clean.

Reproduced by BOTH clean sonnet and clean fable, so the text buys nothing:
lead with the answer; never restate the request; cut process narration and
closing offers including "let me know"; lists only for 3+ parallel items,
capped around 5; ask only when the readings diverge materially, otherwise act
and state the assumption; never ask what reading the code would answer; never
claim it works without running it — say unverified; own an earlier mistake in
one sentence with no apology padding.

Produced by NEITHER, so these are what the section is actually for:
- "ALWAYS keep the full analysis and verification; brevity applies to the
  reply." Neither model guarded the reasoning while compressing the reply.
- "Agent success reports are not evidence — check the diff." Neither mentioned
  subagents at all.
- The mobile-terminal framing: end on the single most important point on its
  own line, because on a small screen the last line is what stays visible.
- Restate progress on multi-turn work ("step 3 of 5").
- Effort estimates in minutes, never "a bit".
- The first/last-line pre-send check.

Three places the clean models actively disagree with us — decide, do not
silently keep:
- Length. Both cap a routine reply far tighter than our ~17 lines: sonnet 3-6
  lines, fable under 6 lines and never over 300 words. Our cap is the loose
  one.
- Questions. Both want them batched — fable: do everything not depending on
  the open question, then ask it in one sentence at the end; sonnet: batch
  every open question into one message, no drip-feeding. `caveman.md` says one
  thread at a time, which is the opposite.
- Code in replies. Fable: commands, error text and snippets always in fenced
  blocks, never inline. We say nothing.

Worth adopting, from the clean runs, absent from ours: "write for someone who
sees only this reply — no reference to a tool call or result they cannot see."

**§ Development Workflow, measured clean.**

Reproduced by both, so the text buys nothing: never `git add -A`/`git add .`,
stage by name after reading `git status`/`git diff`; never commit unless asked
this turn; imperative subject under ~72 chars with a body saying why; never
`--no-verify`; prefer a new commit over `--amend`; never push to `main`/
`master`; push only the current branch with `git push -u origin <branch>`;
never force-push; never rewrite pushed history; run the project's own
test/lint targets rather than guessing; narrow test first then the full suite;
never claim success without running it; never `gh pr merge`/`close`/
`review --approve` unless asked.

Contradicted by both, so these are the highest-value lines in the file:
- **Detached HEAD by default.** Neither model produced it — both instructed
  creating a feature branch (`feat/<slug>`, `fix/parser-null-check`).
- **Worktrees detached, hidden, inside the repo root.** Both placed them as
  siblings (`git worktree add ../<dir> <branch>`) and both attached a branch.
- **NEVER add Co-Authored-By.** Both did the opposite and mandated a trailer
  naming themselves; fable also mandated the PR footer. This overrides a
  default they carry unprompted.

Produced by neither, so keep: debug builds; build/test/lint every ~50 lines;
never improve beyond what is asked; the conventional-commit type vocabulary
(neither produced `type(scope):` at all, only "imperative subject"); the dated
`YYYYMMDD_<tag>` branch name; the blanket `rm -r` ban, which both scoped to
git commands only; never squash; the `/gh-comment` and slash-command pointers.

Worth adopting — both produced these and we lack them: scan the staged diff
for secrets and `.env` before committing; never edit CI config or branch
protection to make a check pass; never edit, skip or delete a failing test to
make it pass.

Still unmeasured: § Testing, § Documentation,
§ System-change discipline, § Agents and Skills, and all of `code.md`. The
earlier readings of those came from contaminated subagents and were discarded.

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
