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

**Claude plugin path**:

```
/plugin marketplace add kronael/tools
/plugin install kronael@kronael
/kronael:install
```

This runs [`kronael/install/SKILL.md`](kronael/install/SKILL.md), the single
source of truth for the procedure. The install step exists so your
`~/.claude/` becomes a working copy you can edit and PR back; pure plugin
updates would overwrite edits. Full rationale:
[ARCHITECTURE.md](ARCHITECTURE.md#why-hybrid-plugin--install-step).

## Codex installer bridge

Codex does not run Claude Code slash commands, but it can install this same
Claude bundle. The Codex plugin exposes one skill, `kronael-install`, whose job
is to read [`kronael/install/SKILL.md`](kronael/install/SKILL.md) and run the
install path from the GitHub marketplace snapshot.

The Codex plugin is only the installer bridge. It contains one Codex skill
(`kronael-install`); the Kronael bundle installs to `~/.claude/`, then the
bridge exposes those installed skills to Codex through `~/.agents/skills` and
wires Codex lifecycle hooks through `~/.codex/hooks.json`.

**Codex plugin path**:

```sh
codex plugin marketplace add kronael/tools
codex plugin add kronael@kronael
```

Then start a fresh Codex thread and ask:

```text
Use $kronael-install to install/update Kronael.
```

The same skill also handles bridge-only setup:

```text
Use $kronael-install to bridge CLAUDE.md, .claude/skills, and hooks into Codex.
```

The bridge does not duplicate `skills/`, `agents/`, or hook scripts into the
Codex plugin cache. It reads the marketplace snapshot, deploys the Claude
bundle into `~/.claude/`, symlinks the installed skills into Codex's user skill
location, and copies `codex-hooks.json` into `~/.codex/hooks.json`.

To repair or apply only the Codex side of that bridge, ask:

```text
Use $kronael-install to bridge .claude/skills and hooks into Codex.
```

That links `~/.agents/skills` to `~/.claude/skills` when possible and copies
`codex-hooks.json` to `~/.codex/hooks.json`. If `~/.agents/skills` already
exists as a directory, the bridge adds per-skill symlinks for Kronael skills
instead. Codex scans `~/.agents/skills`, not `~/.claude/skills`.

Codex compatibility for Claude projects:

- Add `CLAUDE.md` to `project_doc_fallback_filenames` in
  `~/.codex/config.toml` so Codex reads Claude-only project instructions.
- If a project already has `AGENTS.md`, keep a short pointer there telling
  Codex to read `CLAUDE.md`; fallback files do not stack with `AGENTS.md`.
- To expose project `.claude/skills` to Codex, symlink
  `.agents/skills -> ../.claude/skills` instead of copying skill files.

Troubleshooting:

- `kronael` missing from Codex: run `codex plugin marketplace upgrade kronael`
  (or `kronael-local` for older installs), then
  `codex plugin add kronael@kronael`.
- Kronael skills missing in Codex after install: run the bridge prompt above,
  then start a new Codex thread and open `/skills`.
- Kronael hooks missing in Codex after install: run the bridge prompt above to
  refresh `~/.codex/hooks.json`, then start a fresh Codex TUI session, open
  `/hooks`, and trust the changed command hooks.
- Claude hooks missing after install: rerun `$kronael-install`; it merges hook
  wiring from `settings-recommended.json`.
- Codex says `Skipped loading ... invalid SKILL.md`: run
  `make skills-frontmatter-fix`, reinstall/bridge with `$kronael-install`,
  then start a new Codex thread. The lint extracts SKILL.md frontmatter,
  validates it with PyYAML, and fixes known loose forms Claude Code tolerated.

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
  injection, rule re-injection across compaction, stop-time checks. Claude
  wiring lives in `settings-recommended.json`; Codex wiring lives in
  `codex-hooks.json`; see [hooks/README.md](hooks/README.md).
- **The `global` skill** — development wisdom installed as `~/.claude/CLAUDE.md`.

### Layout

```
.claude-plugin/             marketplace.json + plugin.json
.agents/plugins/            repo-local Codex marketplace metadata
plugins/kronael/            thin Codex plugin exposing kronael-install
kronael/install/SKILL.md    plugin-exposed install procedure (source of truth)
skills/                     bundle copied to ~/.claude/skills/
agents/                     bundle copied to ~/.claude/agents/
hooks/                      bundle copied to ~/.claude/hooks/
codex-hooks.json            copied to ~/.codex/hooks.json for Codex hooks
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
| [kronael/install/SKILL.md](kronael/install/SKILL.md) | Install procedure (all paths) |
| [CHANGELOG.md](CHANGELOG.md) | Release history |
