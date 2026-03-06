# CLAUDE.md

Claude Code configuration: 6 agents, 16 auto-activating skills, 5 commands.

## Structure

```
global/                 # Installs to ~/.claude/
├── CLAUDE.md          # Global development wisdom
├── agents/            # 6 specialized task agents
├── commands/          # 5 slash commands (/improve, /learn, /readme, /refine, /visual)
├── skills/            # 16 auto-activating skills
└── settings.json      # Shared Claude Code settings
```

## Settings

`global/settings.json` — shared config (tracked):
- LSP plugins (rust-analyzer, pyright, gopls, typescript)
- Task(*) auto-allow for agent launches

`.claude/settings.local.json` — session permissions (not tracked, in global gitignore)

## Installation (for Claude)

When user says "install":

1. **Inventory** — list files in global/ and destinations in ~/.claude/
2. **Categorize** each file by sync strategy (see below)
3. **Compare** — for each destination, show diff if modified
4. **Ask** — present summary, let user approve per-category
5. **Backup** — before overwriting, copy to ~/.claude/backup/
6. **Install** — copy approved files
7. **Report** — summary: X new, Y updated, Z unchanged

### Sync Strategies

**Replace** (always overwrite with fresh version):
- global/agents/*.md → ~/.claude/agents/
- global/commands/*.md → ~/.claude/commands/
- global/skills/*/ → ~/.claude/skills/
- global/hooks/*.py → ~/.claude/hooks/
- global/hooks/lib/ → ~/.claude/hooks/lib/

**Merge** (show diff, ask what to keep):
- global/CLAUDE.md → ~/.claude/CLAUDE.md
- global/settings.json → ~/.claude/settings.json

**Never touch** (user-maintained):
- ~/.claude/settings.local.json
- ~/.claude/LOCAL.md
- ~/.claude/CLAUDE.local.md (project-level)

**Overlay** (org repos add after base install):
- Org-specific skills → ~/.claude/skills/<org>/
- Installed separately: `cp -r skills/<org> ~/.claude/skills/`
- NEVER included in base — org content lives in overlay repos

NEVER delete files not in source
NEVER modify files user chose to skip
NEVER sync skipDangerousModePermissionPrompt from ~/.claude/ back to template
ALWAYS backup before overwriting

### LOCAL.md Handling

During install, if destination ~/.claude/CLAUDE.md contains local paths,
repo names, secrets references, or org-specific content not in source:
1. Extract those lines to ~/.claude/LOCAL.md (create if needed)
2. Inform user what was extracted
3. NEVER overwrite LOCAL.md — it's user-maintained
4. local.py hook auto-injects LOCAL.md on first prompt + pre-compaction

## Components

**Commands** (5): /improve, /learn, /readme, /refine, /visual

**Agents** (6): @distill, @improve, @learn, @readme, @refine, @visual

**Skills** (16): bash, cli, commit, data, go, ops, python, refine,
rust, service, sql, testing, trader, tweet, typescript, wisdom

**Hooks** (7): nudge (keyword->agent routing), local (rule injection on continue), redirect (toolchain command mapping), learn (flow reports on compact/end), reclaude (session restore), stop (prompt->command type classification), context (context management)

## Working on This Repo

- ALWAYS keep files under 200 lines
- ALWAYS use ALWAYS/NEVER/SHOULD statements
- ALWAYS test changes by installing then using in real project
