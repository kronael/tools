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
├── agents/        # 6 specialized agents
├── hooks/         # 5 UserPromptSubmit/Stop/PreCompact hooks
└── skills/        # 34 auto-activating skills (see skills/README.md)
```

## Skills

Auto-activate based on file context:
- **Languages**: go, py, rs, sh, sql, ts, tsx
- **Domain**: cli, data, ops, service, trader, agent-browser
- **Infrastructure**: testing
- **Workflow**: commit, create-eval, diary, docs-audit, merge-trivial,
  pr-draft, recall-memories, refine, release, ship, specs, tweet, wisdom
- **Shortcuts**: fin, sub
- **Agent launchers** (user-invocable): distill, improve, learn, readme, visual

See [skills/README.md](global/skills/README.md) for the rationale
behind each family (memory, refinement, shortcuts, hooks).

## Agents (6)

- **@distill**: Extract key points from long content
- **@improve**: DO-CRITICIZE-EVALUATE-IMPROVE loop
- **@learn**: Extract patterns from history into skills
- **@readme**: Sync README/ARCHITECTURE with code
- **@refine**: Checkpoint → @improve → @readme → commit
- **@visual**: Render-inspect-adjust for SVG/UI

## Slash Commands

Defined as user-invocable skills:

- **/improve**: Launch @improve agent for code quality
- **/learn**: Launch @learn agent to extract patterns
- **/readme**: Launch @readme agent to update docs
- **/refine**: Finalization - @improve → @readme → commit
- **/visual**: Launch @visual agent for UI/styling

See [WORKFLOW.md](WORKFLOW.md) for agent hierarchy and [ARCHITECTURE.md](ARCHITECTURE.md) for design.
