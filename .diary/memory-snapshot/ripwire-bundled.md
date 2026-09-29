---
name: ripwire-bundled
description: "ripwire is a bundled optional install-tool; running `ripwire wrap` from this repo trips its own exfil scanner on skills/mk and needs --force"
metadata:
  node_type: memory
  type: project
  originSessionId: 6a88abaf-bc70-4628-b951-d0d5fd4ea53d
  modified: 2026-09-07T05:26:31.371Z
---

ripwire (redhat-et, Apache-2.0 — "ripgrep of AI context", deterministic
call-graph maps for agents) is wired into the kronael bundle as of v0.3.69 as
an **optional step-6 external tool** in `kronael/install/` (reference.md +
SKILL.md). CLI + skills are the primary interface; MCP is optional via
`ripwire wrap <agent>`. Security-vetted clean: no outbound network, no
telemetry; its data-logging hooks stay OFF by default (behind `--hook`).

**Gotcha:** `ripwire wrap <agent>` (and `--scan-skills`) run from THIS repo
refuses to emit the recipe — its `EXFILTRATE:net-exfil` scanner flags
`skills/mk/SKILL.md`'s Makefile `curl -sL "$(URL)" -o` tool-download example
(a false positive). Use `ripwire wrap <agent> --force` here. Not a kronael
bug; ripwire being conservative.

MCP registration lives OUTSIDE settings.json: Claude → `claude mcp add ripwire
-- ripwire --mcp` (writes `~/.claude.json`); Codex → a `[mcp_servers.ripwire]`
stanza in `~/.codex/config.toml`. NEVER put `mcpServers` in
`settings-recommended.json`.
