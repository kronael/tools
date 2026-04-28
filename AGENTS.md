# AGENTS.md

Instructions for Codex (and any non-Claude coding agent) working in this
repository. The same conventions live in `CLAUDE.md`; this file makes
them accessible to agents that don't pick up `CLAUDE.md` automatically.

## Startup

ALWAYS read before making changes:

1. Root `CLAUDE.md` — repo conventions and layout.
2. [`kronael/install/SKILL.md`](kronael/install/SKILL.md) — canonical install procedure (this file is the bash translation).
3. Nearest nested `CLAUDE.md` for the area being changed (if any).

NEVER ignore a `CLAUDE.md` because it says "Claude". These are project
conventions, not product-specific behavior.

## What this repo contains

1. **CLI tools** — `dockbox/`, `rig/`, `tw-fetch/`, `tg-fetch/`,
   `dc-fetch/`, `clp/`. Each is independent. Adding a new tool: own
   dir, own Makefile (or PEP 723 inline-deps script), entry in
   `README.md`.
2. **Claude Code plugin** — `.claude-plugin/` + `kronael/install/`.
   Only `/kronael:install` is exposed; running it copies the
   bundle into `~/.claude/`. **You can't run this from Codex** — it's
   a Claude Code slash command. Use the manual path below instead.
3. **Bundle** — `skills/`, `agents/`, `hooks/`, `settings-recommended.json`,
   `RECLAUDE.md`, and `skills/global/SKILL.md` (the wisdom file source).
   Source for both install paths.

## Installing the toolkit from Codex

The bundle is Claude Code config — the hooks fire on Claude Code
lifecycle events, the skills use Claude Code's auto-activation. Codex
itself doesn't use them; Codex is the installer, deploying the bundle
to `~/.claude/` for the user's Claude Code sessions.

Run from the repo root.

### 1. Verify source

```sh
test -d skills && test -d agents && test -d hooks \
  && test -f settings-recommended.json && test -f RECLAUDE.md \
  || { echo "wrong cwd: run from repo root"; exit 1; }
```

### 2. Backup current state

```sh
TS=$(date +%Y%m%d-%H%M%S)
BK=~/.claude/backup/$TS
mkdir -p "$BK"
for d in skills agents hooks; do
  [ -d ~/.claude/$d ] && cp -r ~/.claude/$d "$BK/$d"
done
for f in CLAUDE.md settings.json RECLAUDE.md; do
  [ -f ~/.claude/$f ] && cp ~/.claude/$f "$BK/$f"
done
echo "backup: $BK"
```

### 3. Replace skills, agents, hooks

```sh
mkdir -p ~/.claude/skills ~/.claude/agents ~/.claude/hooks
# Copy every skill except global/ — its body lands in ~/.claude/CLAUDE.md (step 4),
# copying it as a skill too would duplicate the always-loaded content.
for d in skills/*/; do
  [ "$(basename "$d")" = "global" ] && continue
  cp -r "$d" ~/.claude/skills/
done
cp skills/README.md ~/.claude/skills/ 2>/dev/null || true
cp -r agents/. ~/.claude/agents/
cp -r hooks/.  ~/.claude/hooks/
```

NEVER `rm -rf ~/.claude/skills/` first — the user may have org overlays
or personal skills there. `cp -r` overwrites matching files and leaves
others alone.

### 4. Install wisdom file

`skills/global/SKILL.md` body (minus YAML frontmatter) becomes
`~/.claude/CLAUDE.md`. Use awk so the frontmatter stripper actually
matches both fences:

```sh
awk 'BEGIN{n=0} /^---$/{n++; next} n>=2{print}' \
  skills/global/SKILL.md > ~/.claude/CLAUDE.md
```

If `~/.claude/CLAUDE.md` already exists with user content, `diff` it
against the new version first and ask the user before overwriting. Any
local paths, repo names, or secrets the user had go into
`~/.claude/LOCAL.md` (auto-injected by the `local.py` hook). NEVER
overwrite an existing `LOCAL.md`.

### 5. Install RECLAUDE.md

```sh
cp RECLAUDE.md ~/.claude/RECLAUDE.md
```

### 6. Merge settings

`settings-recommended.json` carries the recommended hook wiring,
permissions, and sandbox config. Don't blind-overwrite — the user may
have relaxed permissions or custom env vars.

If `~/.claude/settings.json` doesn't exist, copy:

```sh
cp settings-recommended.json ~/.claude/settings.json
```

Otherwise diff and merge with `jq`. Minimum required: the **hooks**
block (UserPromptSubmit, Stop, PreCompact, SessionEnd) — without it
the hook scripts you copied in step 3 won't fire.

```sh
jq -s '.[0].hooks = .[1].hooks | .[0]' \
   ~/.claude/settings.json settings-recommended.json \
   > ~/.claude/settings.json.new \
  && mv ~/.claude/settings.json.new ~/.claude/settings.json
```

For permissions and sandbox: show the diff to the user, ask which
restrictions to apply. NEVER touch `~/.claude/settings.local.json`.

### 7. Verify and report

```sh
ls ~/.claude/skills/ | wc -l       # should match: ls skills/ | wc -l
ls ~/.claude/agents/ | wc -l       # should be 6
ls ~/.claude/hooks/*.py | wc -l    # should be at least 5
test -f ~/.claude/CLAUDE.md
```

Report to the user: `X skills, Y agents, Z hooks installed. Backup at $BK.`

## Never-touch

- `~/.claude/settings.local.json`
- `~/.claude/LOCAL.md`
- `~/.claude/CLAUDE.local.md`
- Any file/dir in `~/.claude/` that's not in this source tree (org
  overlays, user customizations)
- `skipDangerousModePermissionPrompt` in settings — never sync from
  user back to template

## Conventions

- Boring linear code over clever code.
- Files under 200 lines.
- ALWAYS/NEVER statements in skill content.
- No secrets, no local paths, no org-specific references in source.
- Commit format: `[section] Message`.
- NEVER use `git add -A`, `git commit --amend`, or `git push`.
- NEVER delete files in `~/.claude/` that aren't in this source tree.
