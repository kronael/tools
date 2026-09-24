# BUGS

## Bundle

- **WISDOM-FILE-OVER-LINE-CAP** (MED, design) — CONFIRMED at HEAD 2026-09-18.
  `skills/global/SKILL.md` is 302 lines against the 200-line cap
  `skills/wisdom/SKILL.md` states with "no exceptions — overflow goes to
  sibling files". It is the one file loaded in every session, so the cap bites
  hardest here. Reproduce: `wc -l skills/global/SKILL.md`. **Fix:** the router
  pattern — always-true rules stay inline, a themed block moves to a sibling
  loaded on demand. That changes what is guaranteed present in every session,
  so it needs sign-off.

- **DOC-SHAPE-NOT-IN-BUNDLE** (LOW, design) — CONFIRMED at HEAD 2026-09-21.
  `skills/doc-topology/SKILL.md` routes to `doc-shape` twice — a `NOT for ...
  (use doc-shape)` clause in its description and a pointer in the body — but
  `skills/doc-shape/` does not exist in this source tree. It is installed-only
  (`~/.claude/skills/doc-shape`), so anyone installing from a clone gets a
  skill that names a sibling they do not have. Reproduce:
  `grep -c doc-shape skills/doc-topology/SKILL.md` → 2, `ls skills/doc-shape`
  → no such directory. **Fix:** the maintainer's call, and the install
  protocol forbids deciding it here — an installed-only skill is captured into
  source ONLY on an explicit ask, since it may be org-local. Either add
  `doc-shape` to the bundle, or drop the two references.

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
