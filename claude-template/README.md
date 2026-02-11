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
├── agents/        # 5 specialized agents
├── commands/      # 8 slash commands
└── skills/        # 15 auto-activating skills
```

## Skills

Auto-activate based on file context:
- **Languages**: go, python, rust, sql, typescript
- **Services**: cli, data, ops, service, trader
- **Workflow**: build, commit, refine, ship, wisdom

## Agents

- **distill**: Extract key points from long content
- **improve**: DO-CRITICIZE-EVALUATE-IMPROVE loop
- **learn**: Extract patterns from history into skills
- **readme**: Sync README/ARCHITECTURE with code
- **visual**: Render-inspect-adjust for SVG/UI

## Commands

- **/ship**: Outer loop - specs → components → /build → critique
- **/build**: Inner loop - plan → stages → workers → judge
- **/refine**: Checkpoint → /improve → /readme → commit
- **/improve**: Code quality pass (DO-CRITICIZE-EVALUATE-IMPROVE)
- **/readme**: Update README/ARCHITECTURE/CHANGELOG
- **/learn**: Extract patterns from history
- **/distill**: Extract key points from long content
- **/visual**: UI/styling adjustments

See [WORKFLOW.md](WORKFLOW.md) for agent hierarchy and [ARCHITECTURE.md](ARCHITECTURE.md) for design.
