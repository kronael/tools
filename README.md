# tools

Command-line utilities and Claude Code configuration.

## CLI tools

- [udfix](udfix/) — fix or lint (`--lint`) Unicode box-drawing junction chars in ASCII diagrams (stdin → stdout)
- [dockbox](dockbox/) — dockerized Claude Code or Codex sandbox
- [qemubox](qemubox/) — persistent QEMU VM for daily coding, with shared projects and agent config
- [bhctl](bhctl/) — bluetooth headphones: hi-fi playback, headset mic, or disconnect
- [rig](rig/) — ripgit: detached checkout, push, rebase, merge; git aliases (`gco`, `gif`, `gib`, and more)
- [tw-fetch](tw-fetch/) — X archiver (cookie auth) plus a keyless post reader
- [tg-fetch](tg-fetch/) — Telegram message and member collectors (telethon, env creds)
- [dc-fetch](dc-fetch/) — Discord channel archiver (discum, `DISCORD_TOKEN` env)
- [gloww](gloww/) — read markdown with glow at the terminal's real width

Makefile tools (`udfix`, `rig`, `bhctl`, `dockbox`, `qemubox`, `gloww`):
`cd <tool> && make install`. PEP 723 scripts (`tw-fetch`, `tg-fetch`,
`dc-fetch`): `uv run main.py`.

External tools the Claude Code config uses:
[`kronael/sync/reference.md` § External tool commands](kronael/sync/reference.md#external-tool-commands-step-7).

## Claude Code toolkit

**Claude plugin path**:

```
/plugin marketplace add kronael/tools
/plugin install kronael@kronael
/kronael:sync
```

This runs [`kronael/sync/SKILL.md`](kronael/sync/SKILL.md), the single
source of truth for the procedure; re-run it to update. Run it from your
clone: sync merges your `~/.claude/` edits into the clone, then rebuilds
`~/.claude/` from it; a plugin snapshot cannot take edits.
Full rationale: [ARCHITECTURE.md](ARCHITECTURE.md#why-hybrid-plugin--sync-step).

### What's in the bundle

- **Skills** (`skills/`) — load on dispatch (`/solve`, `/<name>`) or on a
  description match, plus workflow commands (`/commit`, `/ship`, `/refine`,
  `/diary`, ...). The `create` router skill bundles the creative-output
  generators ported from
  [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/main/skills/creative);
  only ones that run locally are bundled. Index and rationale:
  [skills/README.md](skills/README.md).
- **Agents** (`agents/`) — task workers that skills launch;
  [skills/CLAUDE.md § Agent definitions](skills/CLAUDE.md#agent-definitions)
  owns that rule.
- **Hooks** (`hooks/`) — lifecycle scripts: keyword nudging, `LOCAL.md`
  injection, rule re-injection across compaction, stop-time checks. Claude
  wiring lives in `settings-recommended.json`; Codex wiring lives in
  `codex-hooks.json`; see [hooks/README.md](hooks/README.md).
- **Settings** (`settings-recommended.json`) — hook wiring, permissions,
  sandbox, env, and session retention, merged into `~/.claude/settings.json`.
  The always-apply keys of
  [`kronael/sync/reference.md` § Settings](kronael/sync/reference.md#settings-step-5)
  are applied on every sync without asking.
- **The `global` skill** — development wisdom installed as `~/.claude/CLAUDE.md`.

Repo layout: [ARCHITECTURE.md § Repo shape](ARCHITECTURE.md#repo-shape).

## Codex sync bridge

```sh
codex plugin marketplace add kronael/tools
codex plugin add kronael@kronael
```

In a fresh Codex thread, ask `Use @kronael-sync to sync Kronael.` — or, to
repair only the Codex side,
`Use @kronael-sync to bridge CLAUDE.md, .claude/skills, and hooks into Codex.`

The plugin holds one skill, `kronael-sync`. It runs the same sync from a
clone in the current directory's ancestors, else from the GitHub
marketplace snapshot, then exposes the installed bundle to Codex, where
skills are invoked as `@skill-name`. Details: [AGENTS.md](AGENTS.md),
[`kronael/sync/reference.md` § Codex bridge](kronael/sync/reference.md#codex-bridge-step-6).

Troubleshooting:

- `kronael` missing from Codex: `codex plugin marketplace upgrade kronael`,
  then `codex plugin add kronael@kronael`.
- Skills missing in Codex: run the bridge prompt, start a new thread, open `/skills`.
- Global wisdom missing in Codex: run the bridge prompt, check that
  `~/.codex/AGENTS.md` holds the `kronael:start` block, start a new thread.
  `AGENTS.override.md` takes precedence when present.
- Hooks missing in Codex: run the bridge prompt, then in a fresh Codex TUI
  session open `/hooks` and trust the changed command hooks.
- Claude hooks missing after a sync: rerun `@kronael-sync`; it merges hook
  wiring from `settings-recommended.json`.
- Codex says `Skipped loading ... invalid SKILL.md`: run
  `make skills-frontmatter-fix`, re-sync with `@kronael-sync`, start a new thread.

## Documentation

| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](CLAUDE.md) | Repo conventions for Claude Code (auto-loaded each session) |
| [AGENTS.md](AGENTS.md) | Codex / non-Claude agent notes + pointer to the canonical sync |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Repo shape, sync paths, sync strategies, org overlays |
| [COOKBOOK.md](COOKBOOK.md) | Daily git recipes — detached-HEAD with `rig`, `dockbox`, and the toolkit |
| [skills/README.md](skills/README.md) | Skill rationale, index, and workflow diagram |
| [hooks/README.md](hooks/README.md) | Hook system overview |
| [hooks/ARCHITECTURE.md](hooks/ARCHITECTURE.md) | Per-hook data flow |
| [kronael/sync/SKILL.md](kronael/sync/SKILL.md) | Sync procedure (all paths) |
| [CHANGELOG.md](CHANGELOG.md) | Release history |
| [BUGS.md](BUGS.md) | Open issues |
| [specs/index.md](specs/index.md) | Design specs and their status |
| [research/README.md](research/README.md) | Research behind the skill auto-improvement design |
| [evals/README.md](evals/README.md) | Eval examples for the skill auto-improvement loop |
| [docs/](docs/) | Research notes behind individual skills |
| [NOTICE](NOTICE), [LICENSE](LICENSE) | Upstream attribution; the Unlicense |
