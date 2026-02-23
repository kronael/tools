# CLAUDE.md

Claude Code configuration: 8 agents, 18 auto-activating skills, 5 commands.

## Structure

```
global/                 # Installs to ~/.claude/
├── CLAUDE.md          # Global development wisdom
├── agents/            # 8 specialized task agents
├── commands/          # 5 slash commands (/improve, /learn, /readme, /refine, /visual)
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
4. local.py hook auto-injects LOCAL.md on every prompt

## Components

**Commands** (5): /improve, /learn, /readme, /refine, /visual

**Agents** (8): @deep-research, @distill, @improve, @learn, @readme, @refine, @research, @visual

**Skills** (18): bash, cli, commit, data, go, ops, python, refine,
research, rust, service, sql, testing, trader, tweet, typescript, web,
wisdom

**Hooks** (7): nudge (keyword->agent routing), local (rule injection on continue), redirect (toolchain command mapping), learn (flow reports on compact/end), reclaude (session restore), stop (prompt->command type classification), context (context management)

## Working on This Repo

- ALWAYS keep files under 200 lines
- ALWAYS use ALWAYS/NEVER/SHOULD statements
- ALWAYS test changes by installing then using in real project
