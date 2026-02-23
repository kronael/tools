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
├── agents/        # 8 specialized agents
├── commands/      # 5 slash commands
└── skills/        # 16 auto-activating skills
```

## Skills

Auto-activate based on file context:
- **Languages**: go, python, rust, sql, typescript
- **Services**: cli, data, ops, service, trader
- **Infrastructure**: infrastructure, testing
- **Workflow**: commit, refine, tweet, wisdom

## Agents (8)

- **@deep-research**: Multi-round web research with source synthesis
- **@distill**: Extract key points from long content
- **@improve**: DO-CRITICIZE-EVALUATE-IMPROVE loop
- **@learn**: Extract patterns from history into skills
- **@readme**: Sync README/ARCHITECTURE with code
- **@refine**: Checkpoint → @improve → @readme → commit
- **@research**: Research and knowledge synthesis
- **@visual**: Render-inspect-adjust for SVG/UI

## Commands (5)

- **/improve**: Launch improve agent for code quality
- **/learn**: Launch learn agent to extract patterns
- **/readme**: Launch readme agent to update docs
- **/refine**: Finalization - @improve → @readme → commit
- **/visual**: Launch visual agent for UI/styling

See [WORKFLOW.md](WORKFLOW.md) for agent hierarchy and [ARCHITECTURE.md](ARCHITECTURE.md) for design.
