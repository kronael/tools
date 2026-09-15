# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## Status — 2026-09-15 — standing queue, re-triaged after the v0.3.88 pass

Every item below is decision-gated: each needs a design call or a maintainer's
choice, not a patch. None is a correctness defect. Do NOT act without go.

- **WISDOM-FILE-OVER-LINE-CAP** (MED, design) — CONFIRMED. `skills/global/SKILL.md`
  is 297 lines against the 200-line cap `skills/wisdom/SKILL.md` states with "no
  exceptions — overflow goes to sibling files". It is the one file loaded in
  every session, so the cap bites hardest here. Measured cuts took it 270 → 234,
  stressing the rules models state-but-break put it back to 248, deduplicating
  against `caveman.md` reached 238, and the push-consent rules plus the two
  idiom paragraphs carried it to 297. Reproduce: `wc -l skills/global/SKILL.md`.
  **Fix:** the router pattern — always-true rules stay inline, a themed block
  moves to a sibling loaded on demand. That changes what is guaranteed present
  in every session, so it needs sign-off.

- **DOCKBOX-CREDS-MOUNTED-RW** (MED, hardening) — CONFIRMED. dockbox bind-mounts
  all of `~/.claude` and `~/.codex` **rw** into the container, at
  `dockbox/dockbox:12,18`. The guest needs `~/.claude/skills` and `~/.agents`
  editable; it does not need read/write on the API tokens sitting beside them.
  Lower priority — dockbox's README already discloses it is not a boundary for
  hostile code. **Fix:** keep the skill dirs rw while the credentials go ro,
  redacted, or unmounted — not a full config copy-in, which is not needed.

- **SOCIAL-REFS-NARRATE-HISTORY** (LOW, docs) — CONFIRMED.
  `skills/create/social/references/research-social-meme.md:196-217` carries a
  "Corrections (post-codex)" section narrating what the document itself changed
  ("Modes collapsed 4 → 3", "Folklore cut", "Transferability test added"), and
  `references/codex-critique.md` is framed as a verbatim audit trail. Both are
  the prior-version narration the wisdom file bans in permanent content. They
  are cold provenance files nothing reads by accident. **Fix:** the maintainer's
  call — keep them as attribution, or move them to `.diary/`. Not a silent
  rewrite.

- **QEMUBOX-DOCKBOX-UX-DUP** (design — not a correctness bug) — Deferred, needs
  sign-off. The two tools duplicate flag parsing, the tool/model table,
  `ls`/`rm`/`prune`, and the lifecycle block. A shared sourced file would
  violate the repo's "tools are independent, no imports" rule (`CLAUDE.md`);
  `tests/drift_test.sh` is the accepted lightweight guard instead.

---

Fixed bugs are pruned out of this file — they live in git and `CHANGELOG.md`,
with the longer write-ups in `.diary/`.
