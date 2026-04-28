# INSTALL.md

How to deploy the Kronael toolkit into `~/.claude/`. Two paths:

## Plugin (recommended)

```
/plugin marketplace add kronael/tools
/plugin install kronael-tools@kronael-tools
/kronael-tools:install
```

Or just say "install kronael tools" once the plugin is installed — the install skill's description matches that phrasing.

Marketplace = this repo. The `kronael-tools` plugin ships only an installer skill (`/kronael-tools:install`) that copies the bundled `skills/`, `agents/`, `hooks/` into `~/.claude/`, merges the recommended `settings.json`, and writes `~/.claude/CLAUDE.md` from the wisdom skill body. Re-run `/kronael-tools:install` to update.

## Manual

For users who don't use plugin marketplaces. Open Claude Code in this repo and say "install". The model follows the steps below.

### Inventory & sync strategy

The bundle at the repo root:
- `skills/`, `agents/`, `hooks/` → copy to `~/.claude/`
- `skills/global/SKILL.md` body → `~/.claude/CLAUDE.md` (always-loaded wisdom)
- `RECLAUDE.md` → `~/.claude/RECLAUDE.md` (re-injection rules)
- `settings-recommended.json` → merge into `~/.claude/settings.json`

### Procedure

1. **Inventory** — list source files and destinations.
2. **Compare** — diff each destination if modified.
3. **Backup** — copy current `~/.claude/{skills,agents,hooks,CLAUDE.md,settings.json}` to `~/.claude/backup/<timestamp>/`.
4. **Replace** (overwrite without asking):
   - `agents/*.md` → `~/.claude/agents/`
   - `skills/*/` → `~/.claude/skills/`
   - `hooks/*.py`, `hooks/lib/` → `~/.claude/hooks/`
5. **Merge** (show diff, ask):
   - `skills/global/SKILL.md` body (minus frontmatter) → `~/.claude/CLAUDE.md`
   - `settings-recommended.json` → `~/.claude/settings.json` — show side-by-side comparison; user picks which restrictions to apply.
6. **LOCAL.md handling**: if existing `~/.claude/CLAUDE.md` contains local paths, repo names, secrets, extract those lines into `~/.claude/LOCAL.md` (created if missing). NEVER overwrite `LOCAL.md`.
7. **External tools** (ask first):
   - `uv tool install git+https://github.com/kronael/ship` (planner-worker-judge CLI + skill)
   - `bun install -g agent-browser` (headless browser automation)
8. **Report**: X new, Y updated, Z unchanged, W external tools.

### Never-touch

- `~/.claude/settings.local.json`
- `~/.claude/LOCAL.md`
- `~/.claude/CLAUDE.local.md`
- Files in `~/.claude/` that aren't in source (org overlays, user customizations)
- `skipDangerousModePermissionPrompt` — don't sync from user back to template

### Org overlays

Org-specific skills live in separate repos layered on top:

```
cp -r <org-repo>/skills/<org> ~/.claude/skills/
```

Base install never deletes skills not in source — overlays persist across updates.
