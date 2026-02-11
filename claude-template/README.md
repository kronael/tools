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
├── commands/      # 9 slash commands
└── skills/        # 16 auto-activating skills
```

## Skills

Auto-activate based on file context:
- **Languages**: go, python, rust, sql, typescript
- **Services**: cli, data, ops, service, trader
- **Workflow**: build, commit, refine, ship, tweet, wisdom

## Agents

- **distill**: Extract key points from long content
- **improve**: DO-CRITICIZE-EVALUATE-IMPROVE loop
- **learn**: Extract patterns from history into skills
- **readme**: Sync README/ARCHITECTURE with code
- **visual**: Render-inspect-adjust for SVG/UI

## Commands

- **/build**: Inner loop - plan → stages → workers → judge
- **/distill**: Extract key points from long content
- **/improve**: Code quality pass (DO-CRITICIZE-EVALUATE-IMPROVE)
- **/learn**: Extract patterns from history
- **/readme**: Update README/ARCHITECTURE/CHANGELOG
- **/refine**: Checkpoint → /improve → /readme → commit
- **/ship**: Outer loop - specs → components → /build → critique
- **/tweet**: Share work on social media
- **/visual**: UI/styling adjustments

See [WORKFLOW.md](WORKFLOW.md) for agent hierarchy and [ARCHITECTURE.md](ARCHITECTURE.md) for design.
