# Claude Code Template

Auto-activating skills + specialized agents for Claude Code.

## Install

```bash
# Open Claude Code here and say "install"
```

## What Gets Installed

```
~/.claude/
├── CLAUDE.md      # Universal development wisdom
├── agents/        # 7 specialized agents
├── commands/      # 4 slash commands
└── skills/        # 20 auto-activating skills
```

## Skills

Auto-activate based on file context:
- **Languages**: go, python, rust, sql, typescript
- **Services**: cli, collector, data, ops, service, trader
- **Infrastructure**: builder, infrastructure, testing
- **Workflow**: build, commit, refine, ship, tweet, wisdom

## Agents (7)

- **@distill**: Extract key points from long content
- **@improve**: DO-CRITICIZE-EVALUATE-IMPROVE loop
- **@learn**: Extract patterns from history into skills
- **@readme**: Sync README/ARCHITECTURE with code
- **@refine**: Checkpoint → @improve → @readme → commit
- **@research**: Research and knowledge synthesis
- **@visual**: Render-inspect-adjust for SVG/UI

## Commands (4)

- **/build**: Inner loop - plan → stages → workers → judge
- **/refine**: Finalization - @improve → @readme → commit
- **/ship**: Outer loop - specs → components → /build → critique
- **/tweet**: Share work on social media

See [WORKFLOW.md](WORKFLOW.md) for agent hierarchy and [ARCHITECTURE.md](ARCHITECTURE.md) for design.
