# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## OPEN

### prompt_nudge: the first keyword in the prompt wins, so `/ship` loses to `/specs`, `/fable`, `/fix`

`explicit_route` returns the route of the first `AGENT_KEYWORDS` word in prompt
order. Measured over every session transcript (2026-09-05): of 51 user-typed
prompts that say "ship it" / "and ship" / "then ship" / "ship the …", 18 route
to `/ship` and 30 route elsewhere (`/specs` 7, `/fable` 6, `/fix` 4, `/create`
3, `/opus` 2, `/review` 2, `/merge` 2, one each `/continue` `/eye-13yo` `/codex`
`@improve`) because an earlier word matched. "spec this and build it" is in
ship's own `when_to_use` and still routes `/specs`. Reproduce:
`echo '{"prompt":"spec this and ship it"}' | python3 hooks/prompt_nudge.py`.
Fix is a precedence rule (workflow verbs before nouns, or all matches listed),
which is a routing redesign — needs sign-off.

### prompt_nudge: `/testing`, `/eye-13yo`, `/hacker-eval` routes name skills that do not exist

`AGENT_KEYWORDS` maps `test`/`testing` → `/testing`, `ux`/`novice`/`usability`/
`walkthrough` → `/eye-13yo`, `security`/`pentest` → `/hacker-eval`. None of the
three is an installed skill (`13yo-eval`, `red-eval`, `security-review` are).
The nudge tells the model to invoke a skill the Skill tool rejects.

### local.py, reclaude.py, memory_nudge.py: `systemMessage` output is shown to the user, not the model

The same channel defect prompt_nudge had. `hook_system_message` maps to no API
message in Claude Code 2.1.261 (`hook_system_message:()=>[]` in the attachment
table; the docs define `systemMessage` as "a message shown to the user in the
transcript"). Measured: 2409 `hook_system_message` attachments across all
transcripts, 0 model-visible copies. So `local.py`'s LOCAL.md injection and its
RULES re-injection on UserPromptSubmit never reach the model. The PreCompact
paths (`local.py`, `reclaude.py`, `memory_nudge.py`) are the same field; whether
Claude Code carries a PreCompact `systemMessage` across compaction is not
measured. Fix for UserPromptSubmit is `hookSpecificOutput.additionalContext`,
as in `prompt_nudge.emit`; PreCompact needs its own measurement first.

### root Makefile: per-project `test-%` targets are silent no-ops

`make test-dockbox` (and every other `test-<project>`) prints "Nothing to be
done" and runs nothing, so root `make test` reports "all tests passed" while
executing only `tests/drift_test.sh`. The `test-%:` pattern rule at
`Makefile:59` matches but its recipe never fires. `make -C <project> test` works
and is what CI calls, so CI coverage is intact — the gap is local-only.
Reproduce: `make test-dockbox`, `make -C dockbox test`.

### dockbox: guest-editable skills without exposing credentials (TODO)

dockbox bind-mounts the whole `~/.claude` / `~/.codex` **rw** into the container
(`dockbox:12,18`). The intent is that the guest can edit **skills**
(`~/.claude/skills`, `~/.agents`) — but it does NOT need read/write to the
**sensitive config** (the API tokens in `~/.claude`/`~/.codex`). Scope: keep the
skill dirs editable while keeping credentials out of the guest's reach (mount
them ro / redacted / not at all) — not a full config copy-in (that isn't
needed). Lower priority — dockbox's README already discloses it is not a
boundary for hostile code.

### [proposal] wire the ast-grep lint pack into target repos (cross-repo install)

The lint pack (`skills/<lang>/lints/`, aggregated by `sgconfig.yml`, proven by
`make lints`) enforces code rules only in THIS repo. Getting it into a user's
project is a new install contract — a redesign needing sign-off before ship.
Options (see `.ship/plan-skills-as-lints.md` § Distribution):
- **A (recommended)**: opt-in install step — "wire kronael lints into this
  repo?" writes/updates the project's `sgconfig.yml` + `.pre-commit-config.yaml`
  and references the pack. Matches the opt-in-skills posture.
- **B**: publish the pack as a standalone `pre-commit` repo referenced by URL.
- **C**: document a `sgconfig.yml` reference only, no installer.
Also: CI enforcement here needs an ast-grep-provisioned job (`make lints` is not
in pre-commit because the lint CI runner has no ast-grep). Proposed 2026-08-20.

### skills/diagrams: no sequence, swimlane, or state diagram patterns

`skills/diagrams/SKILL.md` (52 lines) teaches only box-and-arrow component
layout. It carries no pattern for the three other shapes that come up
constantly: sequence (message order and who waits), swimlane (step ownership
and the handoffs between actors), and state (the legal transitions of one
entity). Each needs its own ASCII template plus a one-line rule for when to
reach for it, in the same shape as the existing layout pattern.
Reproduce: `grep -i 'sequence\|swimlane\|state' skills/diagrams/SKILL.md` → no hits.

### Deferred — need sign-off

- **qemubox / dockbox shared-UX de-dup.** The two tools duplicate flag parsing,
  the tool/model table, `ls`/`rm`/`prune`, and the lifecycle block. A shared
  sourced file would violate the repo's "tools are independent, no imports"
  rule (`CLAUDE.md`); `tests/drift_test.sh` is the accepted lightweight guard
  instead. Revisit only with sign-off.

---

Resolved items are pruned to `.diary/` (20260818–20260821) and `CHANGELOG.md`
(v0.3.72–v0.3.75): the 2026-08-18 qemubox security audit, the mount-confinement
redesign (curated staging + config copy-in + per-slug session data), the
9p/genericcloud boot fixes, the ref-counted-lifecycle audit, the CEO/CTO
follow-ups, the robustness backlog (`a2d0537..43467d0`, `91f91a8`), and the
install housekeeping (`ce7c39a`). This pass: `rm` now requires an explicit
pattern (`'*'` = all) and qemubox persists its SSH port in `$dir/port`
(`d80c486`); dockbox toolchain bumped (`c04c956`).

### [proposal] the CLAUDE_EVAL guard has no producer

`hooks/stop.py:120` suppresses the commit/diary block when `CLAUDE_EVAL` is
set. Nothing sets it: one hit in the whole repo, the consumer itself — not in
`Makefile`, `.github/`, `evals/`, or any `settings*.json` env block. Introduced
in `bfc2e0f` with no producer. Effect is the opposite of the intent: eval runs
get the block messages injected into their transcripts. Same shape as the
`KRONAEL_IN_CODEX` guard fixed in `0cb8b5a`. Fix is one line either way — set
it in the eval runner, or delete the clause — but which one is a scope call.

### [proposal] session state stamps accumulate forever

`hooks/lib/state.py:29` writes four stamps per session (`local-`,
`diary-nudge-`, `memory-nudge-start-`, `memory-nudge-done-`) and nothing ever
expires a session id. `~/.claude/state` holds 37 files today. Harmless in
bytes; the question is whether stamps should self-prune on write past N days.

### [proposal] humanize/SKILL.md is 629 lines against a 200-line cap

`make skills-frontmatter` warns: the body is 3.1x the cap, and `humanize` is
not in the linter's `LONG_SKILLS` allowance (`{install, ship}`). Skills persist
in context all session, so this is a standing context cost on every session.
It is an external skill vendored intact (it ships its own LICENSE and
Attribution section) and has no sibling files. Splitting the pattern catalogs
(lines 109-548) into on-demand siblings is a restructuring of imported content,
not a one-line fix.

### hooks/prompt_nudge.py: three keyword routes name skills that do not exist

`AGENT_KEYWORDS` sends `novice`/`ux`/`usability`/`walkthrough` to `/eye-13yo`,
`pentest`/`security` to `/hacker-eval`, and `test`/`testing` to `/testing`.
No skill or agent carries those names (`skills/13yo-eval`, `skills/red-eval`,
and `skills/software/testing.md` are the nearest). The nudge tells Claude to
invoke a command that fails, and the real skill stays unreached. Reproduce:
`grep -oE "'/[a-z0-9-]+'" hooks/prompt_nudge.py | tr -d "'" | while read t;
do [ -d skills/${t#/} ] || echo $t; done`.

### skills/README.md still names the router `resolve`

The workflow diagram and the orientation paragraph say `resolve`; the skill
directory is `skills/solve/`. A reader following the README looks for a skill
that is not there. Found 2026-09-05 while editing `solve`.

### skills/software: frontmatter is 1,697 chars, past the 1,536 listing cap

Claude Code lists `description - when_to_use` and cuts it at 1,536 chars
(`skillListingMaxDescChars` default; the binary's `BTo=1536`). The last ~160
chars of `software`'s `when_to_use` — the V8/js-perf and later keywords —
never reach the model. `make skills-frontmatter` now warns (`skill-budget`).
Fix is a trim of `when_to_use`, one anchor per folded mode.

### qemubox: KVM check tests existence, not access

`qemubox:343` passes `-enable-kvm` when `/dev/kvm` exists. On a host where the
device is `root:kvm 0660` and the user is not in `kvm`, QEMU exits with
"Could not access KVM kernel module: Permission denied" instead of the
documented software-emulation fallback; `make install` prints its warning and
`build-base` is skipped. Reproduce: `make -C qemubox install` as a user outside
the `kvm` group (2026-09-05). Fix: test `[ -r /dev/kvm ] && [ -w /dev/kvm ]`.
