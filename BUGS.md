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

## Install protocol

- **INSTALL-LEAVES-STALE-HOOK-DOCS** (LOW, ops) — CONFIRMED at HEAD
  2026-09-29. Install copies only `hooks/*.py`, `*.sh` and `lib/`
  (`kronael/install/SKILL.md:138`), and its prune step names only renamed
  and orphan scripts (`:141-151`). So `README.md`, `ARCHITECTURE.md`,
  `TEST.md` and `Makefile` in `~/.claude/hooks/`, left by an earlier install,
  stay out of date forever (`diff -q hooks/README.md
  ~/.claude/hooks/README.md`). **Fix:** add them to the prune step; no test —
  ops.

## Codex bridge

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

- **LEARN-HOOK-WIRED-NOWHERE** (LOW, dead code) — CONFIRMED at HEAD 2026-09-25.
  `hooks/learn.py` is a complete lifecycle hook that no event invokes:
  `settings-recommended.json` wires `local.py`, `prompt_nudge.py`,
  `pretool_nudge.py`, `post_tool_nudge.sh`, `stop.py`, `memory_nudge.py` and
  `reclaude.py`, and none of them is it. Reproduce:
  `grep -c learn.py settings-recommended.json` → 0. **Fix:** the maintainer's
  call — wire it to an event, or drop it.

- **SMOKE-SUITE-TESTS-THE-INSTALL** (LOW, tests) — CONFIRMED at HEAD 2026-09-25.
  `hooks/test_hooks.py` resolves its subjects under `Path.home()/'.claude'/
  'hooks'` (`:20`), so it exercises whatever is installed rather than the tree
  it ships in, and its docstring and cases name `nudge.py`, which no longer
  exists — the file split into `prompt_nudge.py` and `pretool_nudge.py`. It is
  also absent from the Makefile's `TEST_FILES`, and pytest collects nothing from
  it (`pytest -q test_hooks.py` → "no tests ran"), so nothing runs it either
  way. Reproduce: `ls hooks/nudge.py` → no such file. **Fix:** the maintainer's
  call — point it at the repo tree and rename the subjects, or drop it.

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
  `hooks/stop.py:134` suppresses the commit/diary block when `CLAUDE_EVAL` is
  set. Nothing sets it: its only other hit is `hooks/test_stop.py:16`, which
  strips it from the test env — not `Makefile`, `.github/`, `evals/`, or any
  `settings*.json` env block. Effect is the opposite of the intent: eval runs
  get the block messages injected into their transcripts. **Fix:** one line
  either way — set it in the eval runner, or delete the clause — but which
  one is a scope call; no test — config.

- **HOOK-STATE-STAMPS-ACCUMULATE** (LOW, design) — needs sign-off.
  `hooks/lib/state.py:30` names four stamps per session — `local-`
  (`local.py:36`), `solve-nudge-` (`prompt_nudge.py:152`),
  `memory-nudge-start-` and `memory-nudge-done-` (`memory_nudge.py:110-118`)
  — and no hook deletes one or expires a session id, so `~/.claude/state`
  gains up to four files per session. Harmless in bytes; the question is
  whether stamps should self-prune on write past N days; no test — design.

- **STOP-DUPLICATES-HOOK-EVENT-READER** (LOW, duplication) — CONFIRMED at HEAD
  2026-09-29. `hooks/stop.py:50-58` defines its own `hook_event`: the same
  three-key loop as `hooks/lib/state.py:33-42`, behind a `KRONAEL_HOOK_EVENT`
  override (`:51-53`, set by `post_tool_nudge.sh:20`). `stop.py` imports
  nothing from `lib.state`, so a spelling added to one reader misses the
  other. **Fix:** import `hook_event` from `lib.state` and keep the override
  in `stop.py`, or fold the override into the shared reader; no test —
  duplication.

## dockbox

- **DOCKBOX-IO-URING-AND-CAPS** (MED, design) — needs sign-off. Docker's
  default seccomp profile denies `io_uring_setup` (EPERM in the dockbox image,
  Docker 29.6.2; the host kernel allows it, `io_uring_disabled=0`), so Agave's
  `solana-test-validator` cannot start in a box. `--cap-add` alone does not
  reach the session: dockbox runs it as the host UID (`docker exec -u`), which
  clears effective caps — `SYS_NICE` raised priority for root only, `CapEff`
  was 0 for UID 1000. **Fix:** (1) `--security-opt seccomp=<profile>`: Docker's
  default profile plus `io_uring_setup`/`io_uring_enter`/`io_uring_register`,
  installed next to the script; (2) `--cap-add SYS_NICE,IPC_LOCK,SYS_PTRACE`,
  with sessions started through `setpriv --ambient-caps` so the caps reach the
  user's processes; (3) on by default, no new flag. `seccomp=unconfined` does
  (1) in one line but also lifts the user-namespace and other syscall blocks;
  no test — design.

- **DOCKBOX-LIFECYCLE-UNSERIALIZED** (MED, design) — needs sign-off. Nothing
  serializes creating, entering and removing a box, so two invocations for
  the same project can remove each other's box. (a) A leaving session drops
  its marker and lists the marker dir (`dockbox/dockbox:417-418`), then
  force-removes the box on an empty listing (`:419-420`). A second invocation
  that passed the running check (`:430`) and writes its marker (`:401`)
  between that listing and the removal has its box removed under it; one
  that writes it just after the removal exits with no message, since `:401`
  discards the error. (b) Two launchers for a project with no box both pass
  the same check (`:430`), and the second's pre-run `docker rm -f -v`
  (`:592`) removes the box the first just started (`:597`), with any session
  already in it. `prune` probes an idle box and removes it in two steps
  (`:177-181`), so a session entering between them is removed the same way.
  **Fix:** a per-box host lock (e.g. `flock`) held across marker
  registration, the empty-listing-to-removal step, and creation — a new
  lifecycle contract; no test — design.

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
