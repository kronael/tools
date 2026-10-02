# Server memory — how an agent learns the machine it runs on

Design research, 2026-10-02. Not built. Question: replace the always-injected
`LOCAL.md` with something the agent builds on a prompt, loads on demand and
keeps current like memory; and let `dockbox` / `qemubox` tell the agent it is
in a sandbox.

## Recommendation

1. Replace `LOCAL.md` with a per-machine skill `~/.claude/skills/server/SKILL.md`:
   a fixed description (routing text) in context, the body loaded only on use.
   Keep `LOCAL.md` only for secrets pointers, imported from the body.
2. Build it with a bundle skill `/server-init` (read-only scan + ≤5 questions +
   write). The install questionnaire gets one more opt-in group that runs it.
3. Sandbox note: each launcher writes `/etc/claude-code/CLAUDE.md` inside the
   box — the documented managed-policy path, owned by the image/VM, never a
   host file. Plus one env var `CLAUDE_SANDBOX=dockbox|qemubox`.
4. Do not use `/CLAUDE.md` at `/`: the walk up to `/` itself is unverified, and
   the managed path exists for exactly this.
5. Fix first: `hooks/local.py` injects via `systemMessage`, which the model
   does not see (BUGS.md HOOKS-SYSTEMMESSAGE-NEVER-REACHES-MODEL). Today
   "LOCAL.md is always loaded" is "LOCAL.md is never loaded".

## Verified loading facts

Docs: https://code.claude.com/docs/en/memory.md unless noted.

- Precedence: managed policy "Linux and WSL: `/etc/claude-code/CLAUDE.md`" →
  `~/.claude/CLAUDE.md` → `./CLAUDE.md` or `./.claude/CLAUDE.md` →
  `./CLAUDE.local.md`. Managed content can also sit in `managed-settings.json`:
  "The `claudeMd` key lets you put managed CLAUDE.md content directly inside
  `managed-settings.json`" (managed-settings.md).
- Parents: "Claude Code loads `CLAUDE.md` and `CLAUDE.local.md` from your
  current working directory and every directory above it." Whether that
  includes `/` itself is not stated — unverified.
- Subdirectories: "Instead of loading them at launch, they are included when
  Claude reads files in those subdirectories."
- Imports: `@path`, "maximum depth of four hops", `@~/...` allowed.
- Auto-memory: `~/.claude/projects/<project>/memory/`; "The first 200 lines of
  `MEMORY.md`, or the first 25KB" load at start; topic files on demand.
- Skills (skills.md): "skill descriptions are loaded into context so Claude
  knows what's available, but full skill content only loads when invoked".
  `user-invocable: false` is for "background knowledge that isn't actionable
  as a command".
- SessionStart (hooks.md): matchers `startup|resume|clear|compact|fork`;
  plain-text stdout and `additionalContext` reach the model.
- `systemMessage` (hooks.md): "Warning message shown to the user." Not context.
- Env (env-vars.md): `CLAUDECODE=1` in subprocesses. Observed, undocumented:
  `CLAUDE_CODE_ENTRYPOINT=cli`, `AI_AGENT=claude-code_<ver>_agent`.

Experiment: claude 2.1.287, `--model haiku -p`, cwd `exp/a/b`, git root at `a`,
markers at 4 parent levels, `.claude/CLAUDE.md`, `CLAUDE.local.md`, a subdir, a
project skill, a user skill, 4 hooks, via `CLAUDE_CONFIG_DIR`.

- Seen: all 4 parent `CLAUDE.md` (two above the git root), `.claude/CLAUDE.md`,
  `CLAUDE.local.md`, user `CLAUDE.md`, both skill descriptions, SessionStart
  stdout and `additionalContext`, UserPromptSubmit stdout.
- Not seen: the subdir `CLAUDE.md`, both skill bodies, and UserPromptSubmit
  `{"systemMessage": ...}` (absent from the transcript JSONL too).
- Caveat: under the real `~/.claude` (89 skills) the project skill's
  description was not listed. Cause unverified; the listing budget is likely.

## Current bundle facts

- `hooks/local.py:49-61` reads `~/.claude/LOCAL.md` and `<cwd>/LOCAL.md` on the
  first prompt and on PreCompact; `:80` prints `{'ok': True, 'systemMessage':
  ...}`. Wired from `settings-recommended.json`.
- Install: `kronael/install/SKILL.md:81-104` asks a multiSelect of groups;
  `:147` step 3 writes `~/.claude/CLAUDE.md` and extracts local paths into
  `LOCAL.md`; `:241` NEVER touch `LOCAL.md`. No step scans the host.
- dockbox: `dockbox/dockbox:11-15` mounts `~/.claude` rw; `:361-378` writes a
  merged `settings.json`, bind-mounted ro; `:414-415` project dir at the same
  path, the workdir; `:452` tmpfs `$HOME`; `:515-529` `docker run`.
  `Dockerfile:199-257` `dockbox-init` runs as root, writes `/etc/passwd`,
  `/run/dockbox/ready`. The image owns `/`, `/etc`, `/run/dockbox`.
- qemubox: `qemubox/qemubox:730-731` mounts `~/.claude` ro; `:477-480` copies it
  into the guest home (minus `projects/`), so guest skill edits never reach the
  host; `:740` only `~/.claude/projects/<slug>` is rw; `:466` `sudo tee
  /usr/local/bin/claude` — the guest's `/etc` is ours. No env marker.

## Proposed layout

```
~/.claude/skills/server/SKILL.md      per machine, generic name, body grows
  name: server
  description: What runs on THIS machine and where things live — services,
    ports, data dirs, web roots, sync paths, publishing. Load before touching
    anything outside the project dir, or when a path/host/service is unknown.
  ## Identity     hostname, OS, role, last verified <date>, env
  ## Layout       /srv/data/<project>, web roots, where repos live
  ## Services     unit/container, port, restart, logs
  ## Publishing   what LOCAL.md holds today
  ## Secrets      @~/.claude/LOCAL.md (pointers only, gitignored)
  ## Upkeep       a fact is wrong or missing -> fix it HERE in the same turn;
                  never from inside a sandbox (the env note says which)
~/.claude/skills/server-init/SKILL.md  bundle skill, the builder
```

`/server-init`:

1. Read `hostname`, `/etc/os-release`, running systemd units, `docker ps`,
   `ss -ltnp`, `ls /srv /opt /home`, `df`, crontabs — read-only, no sudo.
2. Draft the body.
3. Ask ≤5 questions: role, what matters, off-limits, publishing, secrets.
4. Write the skill; move the non-secret lines of `LOCAL.md` into it.
5. `--refresh` re-scans and shows a diff instead of overwriting.

Install: add a group "Server memory (runs /server-init)" to the questionnaire
at `install/SKILL.md:88-99`; default off when `CLAUDE_SANDBOX` is set. Upkeep:
the body's rule plus one line in `/learn` ("a fact about the machine →
skills/server"), which `memory_nudge.py` already triggers.

## Launcher changes

- dockbox: generate the note beside the settings override (`dockbox:361-378`),
  mount it `-v "$note:/etc/claude-code/CLAUDE.md:ro"`, add
  `-e CLAUDE_SANDBOX=dockbox`. Content: box name; project dir rw at the same
  path; `HOME` is tmpfs; `~/.claude` is the HOST's, rw, edits persist; host
  paths from the `server` skill are absent unless listed; mounts.
- qemubox: in `setup_guest_runtime` (`:455-480`) `sudo tee
  /etc/claude-code/CLAUDE.md`; export `CLAUDE_SANDBOX=qemubox` (`:884-887`).
  Content: throwaway VM; `~/.claude` is a COPY, skill edits are lost; only
  `~/.claude/projects/<slug>` persists; mounts.
- Fallback if the managed path does not load: mount the same file at
  `$(dirname "$workdir")/CLAUDE.md` inside the box. The parent walk is
  verified, and that path is a mount-point parent, never a host file.
- Bundle: a ~20-line `hooks/env_note.py` on SessionStart printing one plain
  line: `environment: bare host <hostname>` or `sandbox: $CLAUDE_SANDBOX`,
  falling back to `/.dockerenv`, `/run/dockbox/ready`, `/run/qemubox/sess`,
  `systemd-detect-virt`.

## Test plan

Shape: `CLAUDE_CONFIG_DIR=<tmp> claude -p --model haiku "list every MARKER_
token"` with markers in the files under test; assert presence and absence.
From `make test-hooks`, `dockbox/test.sh`, `qemubox/test.sh`.

1. `server` skill: description marker seen at start; body marker absent until
   `Skill(server)`.
2. Managed note: inside `dockbox` and `qemubox` the `/etc/claude-code/CLAUDE.md`
   marker is seen. This also verifies the managed path.
3. `env_note.py`: the line is seen and matches the launcher.
4. Regression: a `systemMessage` marker is NOT seen.
5. Budget: with the full bundle the `server` description is still listed.

## Where the idea does not hold

- Keeping `LOCAL.md` as is keeps nothing. The honest one-line alternative is
  `@~/.claude/LOCAL.md` in `~/.claude/CLAUDE.md`: 41 always-loaded lines, no
  init, no sandbox story.
- Growth "like memory" has the wrong scope in both boxes: dockbox persists edits
  made from inside a container, qemubox discards them. The Upkeep rule must
  forbid edits from a sandbox.
- A skill description is not guaranteed in context at 89 skills. `/solve` scans
  frontmatter from disk, so routing survives; passive recall does not.
- On a bare host `/CLAUDE.md` and `/etc/claude-code/` are root-owned and shared
  by every user. Use the managed path only in boxes we build.
- Built-in `/init` is project-scoped; nothing builds a host memory. The scan
  reads `docker ps`, `ss`, crontabs — it needs the install's explicit consent.

## Open questions

1. One skill `server`, or `server-<hostname>` when `~/.claude` syncs between
   hosts?
2. Who owns the sandbox note: `env_note.py`, the launchers, or both?
3. `/server-init` read-only, or with sudo for `systemctl` / `ss -p` detail?
4. The managed note shows as policy in `/memory`. Acceptable, or prefer the
   parent-directory mount?
