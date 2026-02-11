# Assistants

Claude Code configuration: 16 skills, 5 agents, 9 commands, 5 hooks.

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

## Agent Hierarchy

```
/ship (outer loop: specs → components)
  └── /build (inner loop: plan → parallel workers → commit)

/refine (finalization: /improve + /readme)

/improve, /readme, /learn, /visual, /distill (leaf agents)
```

Nudge hook routes prompts to agents via fuzzy keyword matching.

See [WORKFLOW.md](claude-template/WORKFLOW.md) for full hierarchy,
[ARCHITECTURE.md](claude-template/ARCHITECTURE.md) for component details,
[hooks ARCHITECTURE.md](claude-template/global/hooks/ARCHITECTURE.md) for
hook system.
