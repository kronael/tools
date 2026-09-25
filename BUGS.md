# BUGS

## Bundle

- **WISDOM-FILE-OVER-LINE-CAP** (MED, design) — CONFIRMED at HEAD 2026-09-24.
  `skills/global/SKILL.md` is 302 lines against the 200-line cap
  `skills/wisdom/SKILL.md` states with "no exceptions — overflow goes to
  sibling files". It is the one file loaded in every session, so the cap bites
  hardest here. Reproduce: `wc -l skills/global/SKILL.md`. **Fix:** proposed,
  needs sign-off — it changes what every session is guaranteed to see.
  Safety rules stay inline: push/PR/force, no recursive rm, detached HEAD, no
  amend/squash, commit format, fail loud, record-don't-fix, verify before
  claiming. Activity-scoped blocks move to the skill that owns the activity,
  each leaving a one-line pointer. That takes 302 → ~218, still ~18 over the
  cap — the moves alone do not reach it:
  - Documentation (44, :223–266): keep the no-claude.ai and no-history bans
    inline. `specs/` → `specs`, `.ship/` and "NO plans/" → `ship`, `.diary/`
    → `diary`; each already owns its layout, and `specs` (numbered files) and
    `ship` (`.ship/NN-NAME/`) contradict this file's by-content `specs/` and
    flat `plan-*.md`. Root-file naming, "NO todos/" and `docs/` →
    `readme/topology.md`. ~−19
  - Response Style (35, :48–82): the caveman output style already carries
    lead-first, no recaps, mobile length and the bottom line (:53–71); keep
    the style pointer, the question-spending rule and verify-before-claiming.
    ~−19
  - Cross-component refinement pattern (10, :293–302): `refine` step 5
    already splits into ≤4 buckets. ~−10
  - Session History (9, :33–41): duplicates Startup Protocol step 2 — merge.
    ~−8
  - Subagent briefing shape (6, :278–283) → `dispatch`. ~−5
  - Testing layout/naming (3, :200–202) → `software/testing.md`, which already
    carries the capture-once rule (:207–208); pre-commit rules stay. ~−5
  - Worktree placement (3, :166–168) → `worktree`; detached-HEAD rule stays.
    ~−3
  - Startup Protocol and Think-with-user tightening. ~−11
  - Docker (4, :210–213) → `ops`, which already has multi-stage and layer
    order. ~−4

- **INSTALL-SKILLS-OVER-LINE-CAP** (LOW, docs) — CONFIRMED at HEAD 2026-09-24.
  `kronael/install/SKILL.md` is 232 lines and
  `plugins/kronael/skills/kronael-install/SKILL.md` is 238, against the
  repo's 200-line rule (`CLAUDE.md:107`, `skills/wisdom/SKILL.md:60`).
  **Fix:** move cold detail to `kronael/install/reference.md`.

- **HOOKS-LEARN-ROUTE-CONTRADICTS-DOCS** (LOW, docs) — CONFIRMED at HEAD
  2026-09-24. `hooks/prompt_nudge.py:74` routes the prompt word `learn` to
  `@learn`, while `hooks/README.md:21-23` and `skills/learn/SKILL.md:3,34`
  state that word is deliberately not a route, so `/learn` fires only when
  invoked or through `memory_nudge.py`. The skill description preloads that
  claim, so the model is told one thing and the hook does the other.
  **Fix:** drop the route, or drop the claim from both docs; which is the
  maintainer's call.

- **SUBAGENT-EFFORT-DOCS-DISAGREE** (LOW, docs) — CONFIRMED at HEAD
  2026-09-24. `skills/CLAUDE.md` § Subagent effort defaults says opus and
  fable subagents default to high and sonnet to high, but the agent
  definitions pin `agents/opus.md` at xhigh and `agents/sonnet.md` at medium,
  and `skills/opus/SKILL.md:19` quotes "/sonnet (medium)". A reader of the
  structure rules picks the wrong model tier. **Fix:** make one side match
  the other; which effort is intended is the maintainer's call.

- **RIG-PUSH-BYPASSES-ASK-RULE** (MED, config) — open (record only). The
  `Bash(git push*)` ask rule (`settings-recommended.json:19`) matches the
  command string, so it never matches `rig push`, `rig p` or the `rip`
  symlink, though each runs `git push origin …` (`rig/rig:146`, dispatch at
  `rig/rig:226`). An unlisted command still gets the default prompt, but an
  allow rule that admits them pushes with no ask gate left. **Fix:** an ask
  rule for the rig push forms; which forms, and whether to gate them at all,
  is the maintainer's call.

- **COMMIT-SUBJECT-CASE-RULE-UNFOLLOWED** (LOW, docs) — CONFIRMED at HEAD
  2026-09-25. `skills/commit/SKILL.md:42` says "capitalize first word after
  the colon", but 49 of the last 50 non-release subjects start lowercase
  (`e482962 chore(commit): drop …`). Every commit either breaks the rule or
  breaks the history's own idiom. **Fix:** drop the rule or start following
  it; which case is intended is the maintainer's call; no test — docs.

- **COMMIT-EVALS-BRACKET-FORMAT** (LOW, docs) — CONFIRMED at HEAD 2026-09-25.
  `evals/commit/0[1-5].json` `must_use_format` expects `[fix] …`-style
  subjects (`01.json:13`, `03.json:18`), and `research/eval-sets.md:196`
  shows the same, while `skills/commit/SKILL.md:25` prescribes
  `type(scope): …`. A run scores a skill-compliant commit as a format
  failure. **Fix:** rewrite the regexes and rubric lines to the
  `type(scope):` form; no test — docs.

- **SWEEP-READS-PRUNED-FIXED-ENTRIES** (LOW, docs) — CONFIRMED at HEAD
  2026-09-25. `/sweep` with no argument reads "the most recent `BUGS.md` ✅
  FIXED/Resolved entries" (`skills/sweep/SKILL.md:20`), but
  `skills/bugs/SKILL.md` § Pruning deletes an entry once its fix is
  committed, so a queue kept by that skill has none to read. **Fix:** take
  the fixed pattern from the latest fix commit (`git log`) and the diary;
  no test — docs.

## Ruled not a defect

- **QEMUBOX-DOCKBOX-UX-DUP** (LOW, duplication) — not a defect. The two tools
  duplicate flag parsing, the tool/model table, `ls`/`rm`/`prune`, and the
  lifecycle block. A shared sourced file would violate the repo's "tools are
  independent, no imports" rule (`CLAUDE.md`); `tests/drift_test.sh` is the
  accepted lightweight guard instead.

- **DOCKBOX-CREDS-MOUNTED-RW** (MED, hardening) — not a defect. dockbox mounts
  `~/.claude` and `~/.codex` rw, API tokens included (`dockbox/dockbox:12,18`).
  Claude Code and Codex both rewrite their token files on login refresh, so a
  ro or redacted token breaks auth inside the box. The README already says
  dockbox is not a boundary for hostile code.
