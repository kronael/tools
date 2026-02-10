# CLAUDE.md

Claude Code configuration: 5 agents, 15 auto-activating skills.

## Structure

```
global/                 # Installs to ~/.claude/
├── CLAUDE.md          # Global development wisdom
├── agents/            # 5 specialized task agents
├── commands/          # 5 slash commands (/improve, /refine, etc.)
├── skills/            # 15 auto-activating skills
└── settings.json      # Shared Claude Code settings
```

## Settings

`global/settings.json` — shared config (tracked):
- sandbox enabled + autoAllowBashIfSandboxed
- LSP plugins (rust-analyzer, pyright, gopls, typescript)
- Task(*) auto-allow for agent launches

`.claude/settings.local.json` — session permissions (not tracked, in global gitignore)

## Installation (for Claude)

When user says "install":

1. **Inventory** - List files in global/ and their destinations in ~/.claude/
2. **Compare** - For each destination:
   - New: will install
   - Identical: skip
   - Modified: show diff summary, ask user (Overwrite/Skip/Diff)
3. **Backup** - Before overwriting, copy to ~/.claude/backup/
4. **Install** - Copy approved files
5. **Report** - Summary: X new, Y updated, Z unchanged

Source → Destination:
- global/CLAUDE.md → ~/.claude/CLAUDE.md
- global/agents/*.md → ~/.claude/agents/
- global/commands/*.md → ~/.claude/commands/
- global/skills/*/ → ~/.claude/skills/

NEVER delete files not in source
NEVER modify files user chose to skip
ALWAYS backup before overwriting

## Components

**Agents** (5): distill, improve, learn, readme, visual

**Commands** (5): /improve, /learn, /readme, /refine, /visual

**Skills** (15): builder, cli, commit, data, go, infrastructure, python,
refine, rust, service, ship, sql, trader, typescript, wisdom

## Working on This Repo

- ALWAYS keep files under 200 lines
- ALWAYS use ALWAYS/NEVER/SHOULD statements
- ALWAYS test changes by installing then using in real project
