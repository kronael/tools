# CLAUDE.md

Claude Code configuration: 5 agents, 16 auto-activating skills, 9 commands.

## Structure

```
global/                 # Installs to ~/.claude/
├── CLAUDE.md          # Global development wisdom
├── agents/            # 5 specialized task agents
├── commands/          # 9 slash commands (/build, /distill, /improve, /learn, /readme, /refine, /ship, /tweet, /visual)
├── skills/            # 16 auto-activating skills
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

### LOCAL.md Handling

During install, if destination ~/.claude/CLAUDE.md contains local paths,
repo names, secrets references, or org-specific content not in source:
1. Extract those lines to ~/.claude/LOCAL.md (create if needed)
2. Inform user what was extracted
3. NEVER overwrite LOCAL.md — it's user-maintained
4. context.py hook auto-injects LOCAL.md on every prompt

## Components

**Commands** (9): /build, /distill, /improve, /learn, /readme, /refine, /ship, /tweet, /visual

**Agents** (5): distill, improve, learn, readme, visual

**Skills** (16): build, cli, commit, data, go, ops, python, refine, rust,
service, ship, sql, trader, tweet, typescript, wisdom

## Working on This Repo

- ALWAYS keep files under 200 lines
- ALWAYS use ALWAYS/NEVER/SHOULD statements
- ALWAYS test changes by installing then using in real project
