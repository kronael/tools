---
name: server-init
description: Load this server's facts — `/etc/server/CLAUDE.md`, `/etc/motd` and the host's own notes — before work that touches the machine; build or refresh them with the init half. NOT for a service's Dockerfile or unit (use ops).
when_to_use: "this server, this host, this machine, server facts, server memory, which port, which service, restart a service, service logs, deploy here, how is X deployed, data dir, web root, publish a page, cron job, disk full, where does the space go, motd, /etc/server/CLAUDE.md, server-init, map this server, scan this host, new server, refresh the server facts"
---

# Server facts

One file per machine holds what runs on it and where things live:
`/etc/server/CLAUDE.md`, on the host itself, root-owned and world-readable.
Nothing loads it automatically, so this skill is the only way in. Claude Code
reads `CLAUDE.md` from the working directory's ancestors (stopping before `/`),
from directories under the working directory as files there are read, and
from `/etc/claude-code/CLAUDE.md`; Codex reads project docs from the git root
down to the working directory. No session works under `/etc/server/`, so the
facts stay out of every context until a task needs the machine.

## Load

1. **Read the facts.** `cat /etc/server/CLAUDE.md`. Absent → say this host has
   no facts file and offer the init (below). NEVER guess a port, path or unit
   from another machine's facts — ALWAYS measure it on this one.
   Completion criterion: the file was read, or its absence was stated.

2. **Read the host's own notes.** `/etc/motd`, `/run/motd.dynamic`,
   `/etc/issue`, and `/etc/claude-code/CLAUDE.md` when it exists (inside a
   sandbox box it is the launcher's note and describes the box, not the host).
   They are written by provisioning; a line that disagrees with the facts file
   is a fact to check, not to trust.
   Completion criterion: each note that exists was read.

3. **Check before acting.** The facts file carries a "Last verified" date. A
   fact the task acts on — free disk, a port, a unit or container name, a
   deploy command — ALWAYS gets one command to confirm it first. NEVER act on a
   stale number.
   Completion criterion: every fact the task acts on was confirmed live.

## Upkeep

- A fact wrong or missing → fix it in `/etc/server/CLAUDE.md` in the same turn
  (`sudo`, that file only) and bump "Last verified". NEVER fix a provisioning
  note (`/etc/motd`) by hand — ALWAYS record the drift in the facts file.
- Drifted beyond a few lines, or no facts file → run the init: ALWAYS read
  `init.md` in this directory and follow it. It runs natively on the host,
  NEVER inside a sandbox box.
- NEVER copy host facts into a skill, a memory entry or `~/.claude/` — ALWAYS
  keep them in the machine's own file, so a shared `~/.claude` carries no host
  names and each host keeps its own.
- NEVER move the facts to an auto-loaded path (`/etc/claude-code/CLAUDE.md`, a
  project tree) — ALWAYS keep `/etc/server/`, outside every working directory.

## Review Checklist

- The facts file and the host notes were read before the machine was touched.
- Every fact acted on was confirmed by a command in this turn.
- A wrong fact was fixed in `/etc/server/CLAUDE.md`, nowhere else.
