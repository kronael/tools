# BUGS

## Bundle

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

- **DOC-SHAPE-NOT-IN-BUNDLE** (LOW, design) — CONFIRMED at HEAD 2026-09-24.
  `skills/readme/topology.md:27` points at `doc-shape`, but `skills/doc-shape/`
  does not exist in this source tree. It is installed-only
  (`~/.claude/skills/doc-shape`), so anyone installing from a clone gets a
  data file that names a sibling they do not have. Reproduce: `grep -c
  doc-shape skills/readme/topology.md` → 1, `ls skills/doc-shape` → no such
  directory. **Fix:** the maintainer's call, and the install protocol forbids
  deciding it here — an installed-only skill is captured into source ONLY on
  an explicit ask, since it may be org-local. Either add `doc-shape` to the
  bundle, or drop the reference.

- **DIAGRAMS-NO-SEQUENCE-SWIMLANE-STATE** (LOW, design) — open (record only).
  `skills/diagrams/SKILL.md` (52 lines) teaches only box-and-arrow component
  layout. It carries no pattern for the three other shapes that come up
  constantly: sequence (message order and who waits), swimlane (step ownership
  and the handoffs between actors), and state (the legal transitions of one
  entity). Each needs its own ASCII template plus a one-line rule for when to
  reach for it, in the same shape as the existing layout pattern. Reproduce:
  `grep -i 'sequence\|swimlane\|state' skills/diagrams/SKILL.md` → no hits.

- **HUMANIZE-OVER-LINE-CAP** (LOW, design) — needs sign-off. `make
  skills-frontmatter` warns: `skills/humanize/SKILL.md` has a 629-line body, 3.1x
  the 200-line cap, and `humanize` is not in the linter's `LONG_SKILLS` allowance
  (`{install, ship}`). Skills persist in context all session, so this is a
  standing context cost on every session. It is an external skill vendored
  intact (it ships its own LICENSE and Attribution section) and has no sibling
  files. **Fix:** split the pattern catalogs into on-demand siblings — a
  restructuring of imported content, not a one-line fix.

- **LINT-PACK-NOT-INSTALLABLE** (MED, design) — needs sign-off. The lint pack
  (`skills/<lang>/lints/`, aggregated by `sgconfig.yml`, proven by
  `make lints`) enforces code rules only in THIS repo. Getting it into a user's
  project is a new install contract. Options (see
  `.ship/plan-skills-as-lints.md` § Distribution): **A (recommended)** an
  opt-in install step — "wire kronael lints into this repo?" writes/updates the
  project's `sgconfig.yml` + `.pre-commit-config.yaml` and references the pack,
  matching the opt-in-skills posture; **B** publish the pack as a standalone
  `pre-commit` repo referenced by URL; **C** document a `sgconfig.yml`
  reference only, no installer. Also: CI enforcement here needs an
  ast-grep-provisioned job (`make lints` is not in pre-commit because the lint
  CI runner has no ast-grep).

## Hooks

- **HOOKS-ARCH-CLAIMS-PUSH-BLOCK** (LOW, docs) — CONFIRMED at HEAD 2026-09-24.
  `hooks/ARCHITECTURE.md:95` lists `push` among the commands
  `pretool_nudge.py` blocks. It does not: `UNSAFE_COMMAND_PATTERNS` has no push
  pattern, and `hooks/README.md:43` states push is deliberately left
  unblocked. A reader trusting the doc believes a guard exists that does not.
  Reproduce: `grep -c push hooks/pretool_nudge.py` → 0. **Fix:** drop `push`
  from the ARCHITECTURE list, or add the pattern — which of the two is the
  maintainer's call, since the README documents the omission as deliberate.

- **PROMPT-NUDGE-FIRST-KEYWORD-WINS** (MED, correctness) — needs sign-off.
  `explicit_route` returns the route of the first `AGENT_KEYWORDS` word in
  prompt order. Measured over every session transcript (2026-09-05): of 51
  user-typed prompts that say "ship it" / "and ship" / "then ship" / "ship the
  …", 18 route to `/ship` and 30 route elsewhere (`/specs` 7, `/fable` 6,
  `/fix` 4, `/create` 3, `/opus` 2, `/review` 2, `/merge` 2, one each
  `/continue` `/eye-13yo` `/codex` `@improve`) because an earlier word matched.
  "spec this and build it" is in ship's own `when_to_use` and still routes
  `/specs`. Reproduce: `echo '{"prompt":"spec this and ship it"}' | python3
  hooks/prompt_nudge.py`. **Fix:** a precedence rule (workflow verbs before
  nouns, or all matches listed) — a routing redesign.

- **PROMPT-NUDGE-DEAD-ROUTES** (MED, correctness) — CONFIRMED at HEAD
  2026-09-24. `AGENT_KEYWORDS` maps `test`/`testing` → `/testing`,
  `ux`/`novice`/`usability`/`walkthrough` → `/eye-13yo`, `security`/`pentest`
  → `/hacker-eval`. None of the three is a skill or agent (`software/testing.md`,
  `13yo-eval`, `red-eval` are the nearest). The nudge tells the model to invoke
  a command the Skill tool rejects, and the real skill stays unreached.
  Reproduce: `grep -oE "'/[a-z0-9-]+'" hooks/prompt_nudge.py | tr -d "'" |
  while read t; do [ -d skills/${t#/} ] || echo $t; done`.

- **HOOKS-SYSTEMMESSAGE-NEVER-REACHES-MODEL** (MED, correctness) — CONFIRMED.
  `local.py`, `reclaude.py` and `memory_nudge.py` emit `systemMessage`, the
  channel defect `prompt_nudge` had. `hook_system_message` maps to no API
  message in Claude Code 2.1.261 (`hook_system_message:()=>[]` in the
  attachment table; the docs define `systemMessage` as "a message shown to the
  user in the transcript"). Measured: 2409 `hook_system_message` attachments
  across all transcripts, 0 model-visible copies. So `local.py`'s LOCAL.md
  injection and its RULES re-injection on UserPromptSubmit never reach the
  model. The PreCompact paths (`local.py`, `reclaude.py`, `memory_nudge.py`)
  are the same field; whether Claude Code carries a PreCompact `systemMessage`
  across compaction is not measured. **Fix:** for UserPromptSubmit,
  `hookSpecificOutput.additionalContext` as in `prompt_nudge.emit`; PreCompact
  needs its own measurement first.

- **STOP-CLAUDE-EVAL-NO-PRODUCER** (LOW, config) — needs sign-off.
  `hooks/stop.py:321` suppresses the commit/diary block when `CLAUDE_EVAL` is
  set. Nothing sets it: one hit in the whole repo, the consumer itself — not in
  `Makefile`, `.github/`, `evals/`, or any `settings*.json` env block. Effect
  is the opposite of the intent: eval runs get the block messages injected into
  their transcripts. **Fix:** one line either way — set it in the eval runner,
  or delete the clause — but which one is a scope call.

- **HOOK-STATE-STAMPS-ACCUMULATE** (LOW, resource) — needs sign-off.
  `hooks/lib/state.py:30` writes five stamps per session (`local-`,
  `diary-nudge-`, `solve-nudge-`, `memory-nudge-start-`, `memory-nudge-done-`)
  and nothing ever expires a session id; `~/.claude/state` holds dozens of
  files. Harmless in bytes; the question is whether stamps should self-prune
  on write past N days.

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

## qemubox

- **QEMUBOX-KVM-CHECK-EXISTENCE-NOT-ACCESS** (MED, ops) — CONFIRMED 2026-09-05.
  `qemubox:343` passes `-enable-kvm` when `/dev/kvm` exists. On a host where the
  device is `root:kvm 0660` and the user is not in `kvm`, QEMU exits with
  "Could not access KVM kernel module: Permission denied" instead of the
  documented software-emulation fallback; `make install` prints its warning and
  `build-base` is skipped. Reproduce: `make -C qemubox install` as a user
  outside the `kvm` group. **Fix:** test `[ -r /dev/kvm ] && [ -w /dev/kvm ]`.

- **QEMUBOX-NO-EGRESS-FILTER** (HIGH, hardening) — needs sign-off.
  `qemubox/README.md:145-150` states the gap plainly — live `~/.claude` /
  `~/.codex` tokens are copied into the guest, outbound is open unless `-H`,
  and "the path for exfiltration is open". `-H` is all-or-nothing: an agent
  that needs `api.anthropic.com` gets the whole internet with it. An in-guest
  sandbox cannot close this: the guest copies agent config into its own
  writable home (`qemubox/README.md:108-110`) and the guest user has
  passwordless sudo (`:153`), so anything in the guest can widen its own
  limits. Only a host-side wall holds, and qemubox already sits on one: slirp,
  with `restrict=on` at `qemubox:344`. **Fix (proposal):** a fixed-at-boot
  flag `-p host1,host2` alongside `-H`: start a host proxy on
  `127.0.0.1:$pport` with the allowlist, add
  `,restrict=on,guestfwd=tcp:10.0.2.100:3128-tcp:127.0.0.1:$pport` to the
  `-nic` at `qemubox:362`, and put `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` into
  `envs` so the `exec env$remote` line (`qemubox:876-880`) carries them.
  Claude Code honours those variables. `stop_box` kills the pid, `remove_box`
  removes the files. Roughly 40-60 lines of shell plus docs and three parse
  assertions in `test.sh`. Under `restrict=on` the guest cannot reach slirp's
  DNS, so the host proxy resolves names and there is no UDP/53 side channel.
  Unmeasured: that slirp actually drops guest DNS under `restrict=on` — the
  documentation says the guest is "not able to contact the host", and no one
  has tested it here, because this box has no `/dev/kvm` access (see the KVM
  entry above).

## Ruled not a defect

- **QEMUBOX-DOCKBOX-UX-DUP** (LOW, duplication) — not a defect. The two tools
  duplicate flag parsing, the tool/model table, `ls`/`rm`/`prune`, and the
  lifecycle block. A shared sourced file would violate the repo's "tools are
  independent, no imports" rule (`CLAUDE.md`); `tests/drift_test.sh` is the
  accepted lightweight guard instead.
