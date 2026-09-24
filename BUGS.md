# BUGS

## Bundle

- **WISDOM-FILE-OVER-LINE-CAP** (MED, design) — CONFIRMED at HEAD 2026-09-18.
  `skills/global/SKILL.md` is 302 lines against the 200-line cap
  `skills/wisdom/SKILL.md` states with "no exceptions — overflow goes to
  sibling files". It is the one file loaded in every session, so the cap bites
  hardest here. Reproduce: `wc -l skills/global/SKILL.md`. **Fix** (proposed,
  needs sign-off — it changes what every session is guaranteed to see).
  Safety rules stay inline: push/PR/force, no recursive rm, detached HEAD, no
  amend/squash, commit format, fail loud, record-don't-fix, verify before
  claiming. Activity-scoped blocks move to the skill that owns the activity,
  each leaving a one-line pointer (302 → ~200):
  - Documentation (44): keep the no-claude.ai and no-history bans inline;
    root-file naming, `specs/`, `.ship/`, `.diary/`, `docs/` layout →
    `readme/` router. ~−30
  - Response Style (35): the caveman output style already carries lead-first,
    mobile length, bottom line; keep the style pointer, the question-spending
    rule and verify-before-claiming. ~−20
  - Cross-component refinement pattern (10) → `refine`. ~−10
  - Session History (9): duplicates Startup Protocol step 2 — merge. ~−8
  - Subagent briefing shape (8) → `dispatch`. ~−8
  - Testing layout/naming (6) → `software/testing.md`; pre-commit rules stay.
    ~−6
  - Worktree placement detail (6) → `worktree`; detached-HEAD rule stays. ~−6
  - Startup Protocol and Think-with-user tightening. ~−11
  - Docker (4) → `ops`. ~−4

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
