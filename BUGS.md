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

- **SOCIAL-REFS-NARRATE-HISTORY** (LOW, docs) — CONFIRMED.
  `skills/create/social/references/research-social-meme.md:196-217` carries a
  "Corrections (post-codex)" section narrating what the document itself changed
  ("Modes collapsed 4 → 3", "Folklore cut", "Transferability test added"), and
  `references/codex-critique.md` is framed as a verbatim audit trail. Both are
  the prior-version narration the wisdom file bans in permanent content. They
  are cold provenance files nothing reads by accident. **Fix:** the maintainer's
  call — keep them as attribution, or move them to `.diary/`. Not a silent
  rewrite.

- **GO-CONCURRENCY-EXAMPLE-TRAILING-COMMENTS** (LOW, docs) — CONFIRMED at HEAD
  2026-09-21. `skills/go/concurrency.md:33-63` teaches by an example carrying 7
  trailing inline comments inside a function body
  (`s.Dropped.Add(1)                 // count drops; never stall the caller`).
  `skills/go/SKILL.md` § Comments states "ALWAYS put a comment on its own line
  ABOVE the code it describes; NEVER trail it inline", and `code.md:84` bans a
  comment inside a body outright. An example teaches by demonstration, so the
  file argues against the rule its own skill states. Reproduce:
  `grep -cE '[^[:space:]]+[[:space:]]+//' skills/go/concurrency.md`. **Fix:**
  the maintainer's call — move the annotations above their lines, or drop the
  ones the code already says. The annotations carry the lesson here, so this is
  not a silent rewrite.

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

## Codex bridge

- **CODEX-KRONAEL-BLOCK-NEVER-INSTALLED** (MED, design) — CONFIRMED at HEAD
  2026-09-18. The Kronael block in `codex/AGENTS.md` has never reached global
  Codex guidance: `grep -c kronael:start ~/.claude/CLAUDE.md` → 0, and every
  backup under `~/.claude/backup/*/CLAUDE.md` is 0 too. The repo `CLAUDE.md`
  § Conformance makes quoting that block the test of a working Codex bridge,
  so the bridge fails its own check while the symlink looks healthy. Cause:
  install step 5 merges the block into `~/.codex/AGENTS.md`, which is a
  symlink to `~/.claude/CLAUDE.md` — writing there puts Codex-only
  instructions in the always-loaded Claude wisdom file, and the next install's
  two-way sync reverse-syncs them into `skills/global/SKILL.md`. **Fix:** needs
  a design call — give Codex its own file (`AGENTS.override.md`, or a real
  `~/.codex/AGENTS.md` that reads the wisdom file) rather than appending to the
  symlink target. Do NOT append to the wisdom file.

## dockbox

- **DOCKBOX-CREDS-MOUNTED-RW** (MED, hardening) — CONFIRMED. dockbox bind-mounts
  all of `~/.claude` and `~/.codex` **rw** into the container, at
  `dockbox/dockbox:12,18`. The guest needs `~/.claude/skills` and `~/.agents`
  editable; it does not need read/write on the API tokens sitting beside them.
  Lower priority — dockbox's README already discloses it is not a boundary for
  hostile code. **Fix:** keep the skill dirs rw while the credentials go ro,
  redacted, or unmounted — not a full config copy-in, which is not needed.

## Ruled not a defect

- **QEMUBOX-DOCKBOX-UX-DUP** (LOW, duplication) — not a defect. The two tools
  duplicate flag parsing, the tool/model table, `ls`/`rm`/`prune`, and the
  lifecycle block. A shared sourced file would violate the repo's "tools are
  independent, no imports" rule (`CLAUDE.md`); `tests/drift_test.sh` is the
  accepted lightweight guard instead.
