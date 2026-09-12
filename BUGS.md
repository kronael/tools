# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN — 2026-09-12 — Release review v0.3.83..ff4caa4

Record-only release findings; no fixes applied.

- **CLEAN-ROOM-INVALID-SUCCESS** (HIGH, correctness) —
  `skills/wisdom/clean-room.sh:18` returns success for an empty answer or an
  `unrecognized_model` warning plus a fallback answer. Both reproduced with a
  CLI stub. This invalidates the two-model measurement used to justify rule
  cuts. **Fix:** capture output and stderr, reject fallback warnings and empty
  answers, and preserve nonzero CLI status.
- **PI-WRAPPER-SYMLINK** (HIGH, correctness) —
  `kronael/install/reference.md:30` redirects through an existing executable
  symlink and overwrites its target with Bash. Reproduced with a link to a
  JavaScript entrypoint. **Fix:** back up the existing file, write a regular
  temporary wrapper, then rename it over the executable path.
- **PI-WRAPPER-RUNTIME-PATH** (MED, ops) —
  `kronael/install/reference.md:33` depends on bare `bun` being on PATH.
  The installed wrapper exits 127 in the review environment although Bun is
  installed; using its absolute executable runs pi successfully. **Fix:**
  resolve the Bun executable during installation and verify the wrapper after
  writing it.
- **LINTER-FIX-CONFORMANCE** (MED, correctness) —
  `hooks/skill_frontmatter_lint.py:131` repairs YAML without running
  `conformance` on the result. `--write` returns 0 for a repaired description
  while retaining a wrong skill name and unknown `author` key. **Fix:** run
  conformance on repaired metadata and preserve status 2 for violations.
- **LINTER-YAML-TYPES** (MED, correctness) —
  `hooks/skill_frontmatter_lint.py:76` assumes a mapping with string keys;
  valid YAML scalars, sequences, and mixed key types produce tracebacks.
  Line 84 also accepts list-valued descriptions by stringifying them.
  **Fix:** validate the mapping, key types, and text field types before key
  comparison or listing measurement; return file-specific diagnostics.
- **SKILL-METADATA-PORTABILITY** (MED, config) —
  `skills/humanize/SKILL.md:10` puts a list in metadata, which also contains a
  nested `hermes` mapping. `CLAUDE.md:126` calls metadata free-form by spec,
  but agentskills.io/specification defines string keys and string values.
  The linter accepts these values. **Fix:** flatten/stringify provenance for
  spec portability and validate that shape; distinguish Claude extensions
  from the portable schema in the conformance guidance.
- **BRIDGE-PROBE-NO-CONTEXT** (MED, correctness) — `CLAUDE.md:145` uses
  `pi --version` as bridge evidence. Installed pi exits on that option before
  loading resources, so missing global guidance cannot make this check fail.
  **Fix:** keep the runtime smoke check and separately verify a distinctive
  bridged rule from a neutral working directory.
- **ROUTER-TRANSITIVE-REACHABILITY** (LOW, docs) — `CLAUDE.md:132` treats
  files without a direct dispatch row as unreachable. The create router
  explicitly follows references from its selected mode, including
  `art/p5js.md` to `art/p5js/references/core-api.md`. **Fix:** review
  reachability through references rooted in SKILL.md, including indirect links.

## OPEN

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

**Fourth sweep — how the models say they actually behave, unprompted.**
This one changed the method. Asked to describe their real defaults on a task
with no instructions, both models confessed to breaking rules they can recite:

- sonnet: "I add a comment explaining what I did rather than why, even though my
  own guidance says not to — habitual, not deliberate." fable: "I add a
  docstring or comment explaining the change even when the codebase has none."
- fable: "I treat a green test run as done and rarely exercise the change
  manually" and "I write the recap to sound finished, and sometimes soften a
  partial result into language that reads as complete."
- fable: "I spawn a search agent for anything spanning more than a handful of
  files and then trust its summary without spot-checking."
- sonnet: "I tend to over-scope small requests slightly, cleaning up adjacent
  code I noticed was messy even when not asked, contradicting my own rule."
- sonnet: "I default to fixing only the reported symptom rather than checking if
  the same bug pattern exists elsewhere."
- sonnet: "I'm slower than I should be to say 'I don't have enough context' and
  instead produce a plausible-looking but shakier answer."
- fable: "When something fails twice I start pattern-matching to a known bug
  class instead of re-reading the actual error."

So a reproduced rule is not automatically free — reproduction measures
knowledge, compliance is a separate question. The never-claim-done and
verify-before-claiming rules were cut as reproduced and are restored, stressed
with the pull that defeats them. `skills/wisdom/SKILL.md` now requires the
behaviour question before any cut lands.

**Gaps the confessions expose that the wisdom does NOT cover** — flagged, not
added, since a gap is the user's call:
- Defensive over-handling. sonnet: "I write more defensive code and error
  handling than the surrounding codebase actually uses." fable: "I over-handle
  errors: I add null checks and try/except around paths the caller already
  guarantees are safe." Nothing in the files pushes back on this.
- Under-reading. sonnet: "I'll open 2-3 files when the task really touches 6."
  fable: "I search for the relevant function and miss module-level state or
  decorators above it that change its behavior."
- Test-command authenticity. sonnet: "I run whatever test command I can find
  without confirming it's the one CI actually uses, and report green when it may
  not be the real gate." The make-target rule names the targets but not the
  check that they are the real gate.

Cuts from the third sweep are applied. Workflow content was exempted: make
targets, the commit format, slash-command triggers, the `.ship/`/`.diary/`
layout, the BUGS.md protocol, `/resolve` and `/gh-comment` all stay regardless
of reproducibility.

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
