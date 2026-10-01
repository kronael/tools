# BUGS

## Bundle

- **REFINE-PUBLIC-REPLIES-EXCEED-LOCAL-SCOPE** (MED, design) — proposed,
  needs sign-off. Step 4 of `skills/refine/SKILL.md:32-42` skips unless an
  open PR whose head is an ancestor of HEAD exists, and step 11
  (`:75-86`) already posts each reply through `gh-comment`'s sign-off gate.
  The gap: while such a PR is open, step 11's completion line
  needs every unfixed triaged thread replied to, so refine cannot complete
  for a local-only delivery unless the owner approves or declines the
  replies. **Proposal:** let a reply the owner declined, or a delivery the
  owner kept local, close step 11 as an outstanding thread action listed in
  the report. Keep approval gates in `gh-comment`. No new review mode,
  skill, saved plan or hook. No test — design.

- **REFINE-CLEANUP-EXCEEDS-WORKTREE-OWNERSHIP** (MED, design) — proposed,
  needs sign-off. Step 12 of `skills/refine/SKILL.md:87-89` runs
  `git worktree remove --force` on each stale entry under
  `.claude/worktrees/`. A single `--force` removes an unlocked entry even
  when it holds another task's unreconciled work, which
  `skills/worktree/SKILL.md:54-55` forbids. **Proposal:** make step 12
  apply the existing orphan test in `skills/commit/SKILL.md:68-74` —
  remove only an entry superseded by HEAD whose lock pid is dead, and
  surface unique work to the user. Rule text only, no enforcement
  machinery. No test — design.

- **SOCIAL-REFS-NARRATE-HISTORY** (LOW, docs) — CONFIRMED.
  `skills/create/social/references/research-social-meme.md:196-217` carries a
  "Corrections (post-codex)" section narrating what the document itself changed
  ("Modes collapsed 4 → 3", "Folklore cut", "Transferability test added"), and
  `references/codex-critique.md` is framed as a verbatim audit trail. Both are
  the prior-version narration the wisdom file bans in permanent content. They
  are cold provenance files nothing reads by accident. **Fix:** the maintainer's
  call — keep them as attribution, or move them to `.diary/`. Not a silent
  rewrite.

- **SYNC-BRIDGE-OVER-LINE-CAP** (LOW, docs) — CONFIRMED at HEAD 2026-10-01.
  `plugins/kronael/skills/kronael-sync/SKILL.md` has a 239-line body against the
  repo's 200-line rule (`CLAUDE.md:115`, `skills/wisdom/SKILL.md:65`); the
  canonical `kronael/sync/SKILL.md` is at 199. **Fix:** cut the bridge to its
  Codex-only deltas, or move detail to `kronael/sync/reference.md`.
- **WISDOM-OVER-LINE-CAP** (LOW, docs) — proposed, needs sign-off. 2026-10-01:
  `skills/global/SKILL.md` has a 224-line body against the 200-line cap
  (`awk 'n>=2; /^---$/{n++}' skills/global/SKILL.md | wc -l`); it loads in
  every session. v0.4.8 was at 200: the local rules this release ships
  (`/pr-draft`, the negative-claim and swallowing extensions, the fable and
  sonnet bullets) added the overflow. § Git's two-phase GitHub-text rule stays:
  `pr-draft`, `gh-comment`, `gh-issue` and `release` cite it. **Proposal** (~24
  lines): move the doc-topology bullets (`UPPERCASE at root`, `specs/`/`.ship/`)
  to `readme`; the worktree bullet to `worktree`; the tracking-refs bullet to
  `merge` § Sync; merge the two negative-claim bullets in § Response style; cut
  the `/pr-draft` bullet to its pointer; fold the § Agents fable and sonnet
  bullets into one.


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

- **REFINE-IMPROVE-NO-MODEL** (LOW, docs) — CONFIRMED 2026-10-01. Refine step 8
  dispatches `Task(agent="improve")` with no model
  (`skills/refine/SKILL.md:106`), and `agents/improve.md` pins none, so the
  writer runs on the parent's model and effort. **Fix:** the owner picks the
  model for refine's writing subs.

- **GLOBAL-COMMIT-TYPES-DISAGREE** (LOW, docs) — CONFIRMED 2026-10-01.
  `skills/global/SKILL.md:120-121` § Git lists
  fix/feat/docs/test/chore/refactor; the `commit` skill uses `refa`/`splx`
  (`skills/commit/SKILL.md:31-32`) and refine `refa`
  (`skills/refine/SKILL.md:124`). **Fix:** one list, owned by `commit`.

- **DOCKBOXRC-NO-EPHEMERAL-IGNORED** (LOW, correctness) — CONFIRMED 2026-10-01.
  `--no-ephemeral` in a project `.dockboxrc` becomes `--` in the claude
  arguments with a misleading "ignoring -n" warning (`dockbox/dockbox` rc
  parsing `:330-390`). **Fix:** honour it, or list it among the ignored flags.

- **DOCKBOX-HELP-RC-FLAGS** (LOW, docs) — CONFIRMED 2026-10-01. dockbox help
  (`dockbox/dockbox:311`) says a project `.dockboxrc` ignores `-A/-D/-S`; the
  code (`:387`) also ignores `K`, `n`, `d`, `x`. **Fix:** make the help list
  match.

- **QEMUBOX-E2FSPROGS-VERSION** (LOW, docs) — CONFIRMED 2026-10-01.
  `qemubox/README.md:40` says e2fsprogs ≥1.47; Debian 12's 1.47.0 has no
  `mke2fs -d` tarball support (`strings /usr/sbin/mke2fs | grep -ci archive`
  → 0), so the build probe (`qemubox/qemubox:780-782`) fails after the
  README's apt install. **Fix:** state the version that adds tarball support
  once confirmed (unverified: 1.47.1).

- **TWFETCH-SWALLOWS-DRIVER-ERRORS** (LOW, correctness) — CONFIRMED 2026-10-01.
  `tw-fetch/main.py:184-185` catches `WebDriverException` (a superclass of
  `NoSuchElementException`) around the Following-tab click and passes, so a
  failed click silently archives the default tab; `parse_tweet` drops a tweet
  on any `WebDriverException` (`:115`); `suppress(Exception)` at `:63` hides a
  rejected cookie. **Fix:** catch `NoSuchElementException` for an absent tab
  only, and let other driver errors surface.

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

- **RIG-DEMO-GIF-STALE** (LOW, docs) — CONFIRMED 2026-10-01. `rig/demo/demo.gif`
  still plays the removed `riq` section; `rig/demo/run.ts` no longer has it.
  `make -C rig demo` needs `asciinema` and `agg`, which this host lacks.
  **Fix:** re-record with `make -C rig demo` on a host that has both.
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
  `hooks/stop.py:149` suppresses the commit/diary block when `CLAUDE_EVAL` is
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
  2026-09-29. `hooks/stop.py:55-63` defines its own `hook_event`: the same
  three-key loop as `hooks/lib/state.py:33-42`, behind a `KRONAEL_HOOK_EVENT`
  override (`:56-58`, set by `post_tool_nudge.sh:20`). `stop.py` imports
  nothing from `lib.state`, so a spelling added to one reader misses the
  other. **Fix:** import `hook_event` from `lib.state` and keep the override
  in `stop.py`, or fold the override into the shared reader; no test —
  duplication.

## dockbox

- **DOCKBOX-LIFECYCLE-UNSERIALIZED** (MED, design) — needs sign-off. Nothing
  serializes creating, entering and removing a box, so two invocations for
  the same project can remove each other's box. (a) A leaving session drops
  its marker and lists the marker dir (`dockbox/dockbox:468-469`), then
  force-removes the box on an empty listing (`:470-471`). A second invocation
  that passed the running check (`:481`) and writes its marker (`:451`)
  between that listing and the removal has its box removed under it; one
  that writes it just after the removal exits with no message, since `:451`
  discards the error. (b) Two launchers for a project with no box both pass
  the same check (`:481`), and the second's pre-run `docker rm -f -v`
  (`:669`) removes the box the first just started (`:676`), with any session
  already in it. `prune` probes an idle box and removes it in two steps
  (`:198-201`), so a session entering between them is removed the same way.
  **Fix:** a per-box host lock (e.g. `flock`) held across marker
  registration, the empty-listing-to-removal step, and creation — a new
  lifecycle contract; no test — design.

- **BOXES-SHARE-CLAUDE-RUNTIME-STATE** (MED, design) — needs sign-off.
  Both boxes bind the whole `~/.claude` rw (`dockbox/dockbox:14`,
  `qemubox/qemubox` `assemble_mounts`), which holds persistent state the
  contract wants shared (`projects/`, `memory`, `skills`, `settings.json`,
  `.credentials.json`) and per-process runtime state it does not: besides
  `sessions/` (a private tmpfs per box) the installed Claude Code
  2.1.286 keeps `tasks/`, `session-env/`, `bridge-spawn/`, `ccr/`,
  `server.lock`, `server-sessions.json` and `ide/*.lock` there (names from
  the binary's config-dir list). Through those, one box's agent can read
  another box's or the host's background-task outputs and IDE lock files
  (port and auth token of a host IDE server, reachable from a `-H` box),
  and the host's `claude agents` daemon state mixes with box state.
  **Proposal:** split the bind — persistent dirs stay shared, runtime dirs
  become per-box tmpfs like `sessions/` — in both tools. Tradeoffs: the
  host's agent view stops listing box background sessions (it already
  cannot attach to them: their sockets are box-private), `tasks/` output of
  a box's subagents dies with the box, and the list is version-bound, so it
  needs re-checking on Claude Code upgrades. A contract change; not shipped.

- **DOCKBOX-NAT-FLOWS-ON-CARRIER-BLIP** (LOW, design) — open (unverified).
  The journal shows the Wi-Fi link dropping and re-acquiring the same DHCP
  lease within 2-5 s several times a day (`journalctl -u systemd-networkd`,
  "wlan0: Lost carrier" then "DHCPv4 address 192.168.0.153/24"). networkd
  removes the address on carrier loss; the kernel's MASQUERADE target then
  flushes every conntrack entry NATed to it (`nf_nat_masquerade.c`,
  `masq_inet_event`). A host socket survives the blip (TCP retransmits once
  the address is back); a bridge box's flow survives only if its next packet
  is outbound, so a fresh NAT entry with the same port is created. If the
  server speaks first — a streaming API response — the packet finds no entry
  and no local socket, the host answers RST and the box's connection dies.
  Reproducing needs a Wi-Fi toggle, which this audit did not do. `-H` has
  no NAT and none of this. **Fix:** none in dockbox short of host network;
  document, or test and close.

## qemubox

- **QEMUBOX-NO-EGRESS-FILTER** (HIGH, hardening) — needs sign-off.
  `qemubox/README.md:166-171` states the gap plainly — live `~/.claude` /
  `~/.codex` tokens are shared read-write with the guest, outbound is open unless `-H`,
  and "the path for exfiltration is open". `-H` is all-or-nothing: an agent
  that needs `api.anthropic.com` gets the whole internet with it. An in-guest
  sandbox cannot close this: the guest mounts agent config read-write at
  the host paths (`qemubox/README.md:127-131`) and the guest user has
  passwordless sudo (`:174`), so anything in the guest can widen its own
  limits. Only a host-side wall holds, and qemubox already sits on one: slirp,
  with `restrict=on` at `qemubox:592`. **Fix (proposal):** a fixed-at-boot
  flag `-p host1,host2` alongside `-H`: start a host proxy on
  `127.0.0.1:$pport` with the allowlist, add
  `,restrict=on,guestfwd=tcp:10.0.2.100:3128-tcp:127.0.0.1:$pport` to the
  `-nic` at `qemubox:613`, and put `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` into
  `envs` so the `exec env$remote` line (`qemubox:1283-1285`) carries them.
  Claude Code honours those variables. `stop_box` kills the pid, `remove_box`
  removes the files. Roughly 40-60 lines of shell plus docs and three parse
  assertions in `test.sh`. Under `restrict=on` the guest cannot reach slirp's
  DNS, so the host proxy resolves names and there is no UDP/53 side channel.
  Unmeasured: that slirp actually drops guest DNS under `restrict=on` — the
  documentation says the guest is "not able to contact the host", and no one
  has tested it here, because this box has no `/dev/kvm` access (see the KVM
  entry above).

- **QEMUBOX-POWEROFF-CLAIMS-RUNNING** (LOW, ux) — CONFIRMED 2026-10-01.
  `qemubox -n x -N exec sudo poweroff` ends with ssh's
  "kex_exchange_identification: Connection reset by peer" and
  `qemubox:322` "cannot remove session marker; keeping qemubox-x running",
  while `qemubox status x` already reports `process=stopped`. `running` at
  `:316` still sees the QEMU process during shutdown; the marker ssh then
  fails. **Fix:** re-check `running` before printing the note; say the VM is
  shutting down instead.
- **QEMUBOX-FIRST-BOOT-SYSTEMCTL-NOISE** (LOW, ux) — CONFIRMED 2026-10-01.
  First boot prints systemctl's two "Removed '/etc/systemd/system/...
  systemd-timesyncd.service'" lines into the user's terminal from
  `sync_guest_clock` (`qemubox:524`). **Fix:** `systemctl disable --now
  --quiet`.

## Ruled not a defect

- **QEMUBOX-DOCKBOX-UX-DUP** (LOW, duplication) — not a defect. The two tools
  duplicate flag parsing, the tool/model table, `ls`/`rm`/`prune`, and the
  lifecycle block. A shared sourced file would violate the repo's "tools are
  independent, no imports" rule (`CLAUDE.md`); `tests/drift_test.sh` is the
  accepted lightweight guard instead.

- **DOCKBOX-PROJECT-ENV-REACHES-ROOT** (MED, security) — not a defect. A
  project `.dockboxrc` `-e` variable reaches root in the box (dockbox-init runs
  as root with the container env, and sessions enter as root before `setpriv`),
  so `-e LD_PRELOAD=<repo file>` runs code as root there. dockbox is a decently
  isolated env, not a jail: root inside the box is within its design.

- **BOXES-DOCKER-SOCKET-CROSSES-BOXES** (MED, isolation) — not a defect. `-D`
  binds `/var/run/docker.sock` into a dockbox and forwards it into a qemubox
  over SSH; either agent can then `docker exec` into every dockbox on the
  host. That is the flag's purpose (building images, running containers)
  and the project `.dockboxrc`/`.qemuboxrc` cannot set it, so it is an
  explicit per-box grant. Both READMEs say it crosses the box wall.

- **DOCKBOX-CREDS-MOUNTED-RW** (MED, hardening) — not a defect. dockbox mounts
  `~/.claude` and `~/.codex` rw, API tokens included (`dockbox/dockbox:14,20`).
  Claude Code and Codex both rewrite their token files on login refresh, so a
  ro or redacted token breaks auth inside the box. The README already says
  dockbox is not a boundary for hostile code.
