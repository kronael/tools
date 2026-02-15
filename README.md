# Assistants

Claude Code configuration: 20 skills, 7 agents, 4 commands, 5 hooks.

## Contents

**[claude-template/](claude-template/)** - Skills, agents, commands, and hooks
for Claude Code. Open Claude Code there and say "install".

**[usage-patterns/](usage-patterns/)** - 12 usage patterns extracted from 57
production projects (1.3MB logs).

## Installation

```bash
cd claude-template
# Say "install"
```

Claude compares with existing ~/.claude/, shows diffs, asks before overwriting.

## Components

**Commands** (4): /build, /refine, /ship, /tweet

**Agents** (7): @distill, @improve, @learn, @readme, @refine, @research, @visual

**Skills** (20): build, builder, cli, collector, commit, data, go,
infrastructure, ops, python, refine, rust, service, ship, sql, testing,
trader, tweet, typescript, wisdom

**Hooks** (5): nudge (keyword-to-agent routing), local (rule injection on
continue), redirect (toolchain command mapping), learn (flow reports on
compact/end), reclaude (session restore)

## Agent Hierarchy

```
/ship (outer loop: specs -> components)
  └── /build (inner loop: plan -> parallel workers -> commit)

/refine (finalization: @improve + @readme)

@improve, @readme, @learn, @visual, @distill, @research (leaf agents)
```

Nudge hook routes prompts to agents via fuzzy keyword matching.

## References

- [WORKFLOW.md](claude-template/WORKFLOW.md) - agent hierarchy
- [ARCHITECTURE.md](claude-template/ARCHITECTURE.md) - component details
- [hooks ARCHITECTURE.md](claude-template/global/hooks/ARCHITECTURE.md) - hook system

## See Also

**[kronael/ship](https://github.com/kronael/ship)** - Autonomous coding agent
that implements the planner-worker-judge pipeline as a standalone Python tool.
Consumes Claude Code CLI and skills from ~/.claude/skills/. Same architectural
pattern as /ship and /build commands here (spec-driven parallel implementation),
but as an independent tool.
