# tools

Command-line utilities and Claude Code configuration.

## Tools

- [dockbox](dockbox/) - dockerized Claude Code sandbox
- [rig](rig/) - ripgit: smart branch checkout, push, rebase, merge

### External tools (installed during assistants setup)

- [ship](https://github.com/kronael/ship) - planner-worker-judge CLI for autonomous feature delivery
- [agent-browser](https://www.npmjs.com/package/agent-browser) - headless browser automation CLI

## Assistants

- [claude-template](assistants/claude-template/) - Skills, agents, hooks for Claude Code
- [usage-patterns](assistants/usage-patterns/) - 12 usage patterns extracted from 57 production projects

## Installation

Each tool has its own Makefile. Navigate to the tool directory and run `make install`.

For Claude Code configuration, open `assistants/claude-template/` and say "install".

## Daily Use

See [COOKBOOK.md](COOKBOOK.md) for detached-HEAD recipes that combine
rig, dockbox, and the assistants — start a feature, push, rebase,
recover lost work, ship from spec.
