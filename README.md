# tools

Command-line utilities and Claude Code configuration.

## CLI tools

- [udfix](udfix/) — fix Unicode box-drawing junction chars in ASCII diagrams (stdin → stdout)
- [dockbox](dockbox/) — dockerized Claude Code sandbox
- [rig](rig/) — ripgit: smart branch checkout, push, rebase, merge
- [tw-fetch](tw-fetch/) — Twitter/X thread archiver
- [tg-fetch](tg-fetch/) — Telegram channel/group archiver (telethon, TOML config)
- [dc-fetch](dc-fetch/) — Discord channel archiver (discum, `DISCORD_TOKEN` env)
- [clp](clp/) — claude project picker (experimental; sourceable bash function)

Go tools (`udfix`, `rig`): `cd <tool> && make install`. PEP 723 scripts
(`tg-fetch`, `dc-fetch`): `uv run main.py`. `dockbox` has its own Makefile.

External tools used by the Claude Code config:

- [ship](https://github.com/kronael/ship) — planner-worker-judge CLI
- [agent-browser](https://www.npmjs.com/package/agent-browser) — headless browser automation

## Claude Code toolkit

**Quickest path** — clone the repo, open Claude Code at the root, say **"install"**:

```sh
git clone https://github.com/kronael/tools /tmp/kronael
cd /tmp/kronael
claude   # then type: install
```

**Plugin path** — if you prefer the marketplace:

```
/plugin marketplace add kronael/tools
/plugin install kronael@kronael
/kronael:install
```

Both paths run [`kronael/install/SKILL.md`](kronael/install/SKILL.md), the
single source of truth for the procedure. The install step exists so your
`~/.claude/` becomes a working copy you can edit and PR back — a pure plugin
would overwrite your edits on every update. Full rationale:
[ARCHITECTURE.md](ARCHITECTURE.md#why-hybrid-plugin--install-step).

### What's in the bundle

- **Skills** (`skills/`) — auto-activating context plus workflow commands
  (`/commit`, `/ship`, `/refine`, `/diary`, ...). The `create` router skill
  bundles the creative-output generators ported from
  [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/main/skills/creative);
  only ones that run locally are bundled. Index and rationale:
  [skills/README.md](skills/README.md).
- **Agents** (`agents/`) — task workers (`@distill`, `@improve`, `@learn`,
  `@readme`, `@refine`, `@visual`), mostly launched via slash commands.
- **Hooks** (`hooks/`) — lifecycle scripts: keyword nudging, `LOCAL.md`
  injection, rule re-injection across compaction, stop-time checks. Wiring
  lives in `settings-recommended.json`; see [hooks/README.md](hooks/README.md).
- **The `global` skill** — development wisdom installed as `~/.claude/CLAUDE.md`.

### Layout

```
.claude-plugin/             marketplace.json + plugin.json
kronael/install/SKILL.md    plugin-exposed install procedure (source of truth)
skills/                     bundle copied to ~/.claude/skills/
agents/                     bundle copied to ~/.claude/agents/
hooks/                      bundle copied to ~/.claude/hooks/
settings-recommended.json   merged into ~/.claude/settings.json
RECLAUDE.md                 template for ~/.claude/RECLAUDE.md
```

## Documentation

| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](CLAUDE.md) | Repo conventions for Claude Code (auto-loaded each session) |
| [AGENTS.md](AGENTS.md) | Codex / non-Claude agent notes + pointer to the canonical install |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Repo shape, install paths, sync strategies, org overlays |
| [COOKBOOK.md](COOKBOOK.md) | Daily git recipes — detached-HEAD with `rig`, `dockbox`, and the toolkit |
| [skills/README.md](skills/README.md) | Skill rationale, index, and workflow diagram |
| [hooks/README.md](hooks/README.md) | Hook system overview |
| [hooks/ARCHITECTURE.md](hooks/ARCHITECTURE.md) | Per-hook data flow |
| [kronael/install/SKILL.md](kronael/install/SKILL.md) | Install procedure (both paths) |
| [CHANGELOG.md](CHANGELOG.md) | Release history |
