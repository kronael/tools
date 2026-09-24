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
  repo's 200-line rule (`CLAUDE.md:106`, `skills/wisdom/SKILL.md:60`).
  **Fix:** move cold detail to `kronael/install/reference.md`.

- **RIG-PUSH-BYPASSES-ASK-RULE** (MED, config) — open (record only). The
  `Bash(git push*)` ask rule (`settings-recommended.json:19`) matches the
  command string, so it never matches `rig push`, `rig p` or the `rip`
  symlink, though each runs `git push origin …` (`rig/rig:146`, dispatch at
  `rig/rig:226`). An unlisted command still gets the default prompt, but an
  allow rule that admits them pushes with no ask gate left. **Fix:** an ask
  rule for the rig push forms; which forms, and whether to gate them at all,
  is the maintainer's call.

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
