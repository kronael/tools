# BUGS

## Bundle

- **INSTALL-SKILLS-OVER-LINE-CAP** (LOW, docs) — CONFIRMED at HEAD 2026-09-24.
  `kronael/install/SKILL.md` is 232 lines and
  `plugins/kronael/skills/kronael-install/SKILL.md` is 238, against the
  repo's 200-line rule (`CLAUDE.md:107`, `skills/wisdom/SKILL.md:60`).
  **Fix:** move cold detail to `kronael/install/reference.md`.

- **CODEX-SKILL-FAILS-FRONTMATTER-LINT** (LOW, config) — CONFIRMED at HEAD
  2026-10-02. `plugins/kronael/skills/kronael-install/SKILL.md:1-4` has no
  `when_to_use`, and the `skill-frontmatter` hook (`.pre-commit-config.yaml:9-15`)
  lints every `SKILL.md`, so `pre-commit run --files` on it exits 2
  (`[skill-keys] missing ... when_to_use`); CI's `pre-commit/action` runs all
  files. **Fix:** add a `when_to_use`, or exclude `plugins/` from the hook if
  the Codex bridge follows Codex's frontmatter rules instead.


- **HOOKS-LEARN-ROUTE-CONTRADICTS-DOCS** (LOW, docs) — CONFIRMED at HEAD
  2026-09-24. `hooks/prompt_nudge.py:74` routes the prompt word `learn` to
  `@learn`, while `hooks/README.md:21-23` and `skills/learn/SKILL.md:3,34`
  state that word is deliberately not a route, so `/learn` fires only when
  invoked or through `memory_nudge.py`. The skill description preloads that
  claim, so the model is told one thing and the hook does the other.
  **Fix:** drop the route, or drop the claim from both docs; which is the
  maintainer's call.

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

## Hooks

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

- **DOCKBOX-CREDS-MOUNTED-RW** (MED, hardening) — not a defect. dockbox mounts
  `~/.claude` and `~/.codex` rw, API tokens included (`dockbox/dockbox:12,18`).
  Claude Code and Codex both rewrite their token files on login refresh, so a
  ro or redacted token breaks auth inside the box. The README already says
  dockbox is not a boundary for hostile code.
