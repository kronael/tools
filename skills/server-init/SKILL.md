---
name: server-init
description: Build or refresh this host's server memory, the skill server-<hostname> — what runs here and where things live. NOT for writing a service's Dockerfile or unit (use ops), NOT inside dockbox or qemubox (the launcher's note covers the box).
when_to_use: "server-init, server memory, map this server, scan this host, new server, what runs on this machine, host layout, services and ports on this host, where things live on this server, the server skill is wrong, refresh the server memory, machine facts in LOCAL.md"
---

# Server init

Builds `~/.claude/skills/server-<hostname>/SKILL.md`, one host's memory: its
role, layout, services and publishing paths. Only its description sits in the
skill listing; the body loads when a task needs the machine and grows as work
finds facts. Named per host, so a `~/.claude` shared between machines keeps one
memory each.

Where a machine fact goes: a note every session on this machine must see goes in
`/etc/claude-code/CLAUDE.md`, Claude Code's managed file — dockbox and qemubox
pre-write it, and on a host it is written only when already writable, NEVER
with sudo; a fact about this host goes in its `server-<hostname>` skill.

## Steps

1. **Refuse in a sandbox.** `CLAUDE_SANDBOX` set, or `/etc/claude-code/CLAUDE.md`
   naming dockbox or qemubox → stop and say so. NEVER build a memory from a
   box: its services and paths describe the sandbox, not the host. ALWAYS use
   the launcher's note for sandbox facts.
   Completion criterion: `CLAUDE_SANDBOX` is empty and no sandbox note exists.

2. **Name the target.** `host=$(hostname -s)`, target
   `~/.claude/skills/server-$host/SKILL.md`. It exists → this run is a refresh:
   read it first; every later step keeps what it holds.
   Completion criterion: the target path and "new" or "refresh" are stated.

3. **Scan, read-only.** NEVER sudo, NEVER start, stop, restart or reload
   anything. A command that needs root → record the gap ("docker: socket needs
   root"), NEVER a guess.
   - identity: `hostname -f`, `/etc/os-release`, `systemd-detect-virt`,
     `nproc`, `free -h`, `df -h -x tmpfs -x devtmpfs`
   - services: `systemctl list-units --type=service --state=running
     --no-pager`, the same with `--user`, `docker ps --format
     '{{.Names}}\t{{.Image}}\t{{.Ports}}'`
   - ports: `ss -ltnp` (another user's process shows without a name)
   - layout: `ls /srv /srv/* /opt /var/www /home`; web roots and names from
     `/etc/nginx/sites-enabled/*` or `/etc/caddy/Caddyfile`
   - schedules: `crontab -l`, `ls /etc/cron.d`, `systemctl list-timers
     --no-pager`
   - facts already written: `~/.claude/LOCAL.md` and `~/.claude/CLAUDE.md`
     (paths, publishing rules, hosts they name)
   Completion criterion: each line above ran, or its gap is recorded.

4. **Ask what a scan cannot know.** AskUserQuestion, at most 5, only the ones
   still open after step 3: the host's role; what matters most or is
   off-limits; where publishing goes; where secrets live (a pointer, NEVER a
   value).
   Completion criterion: each question answered or skipped by the user.

5. **Draft** from the template below. ALWAYS keep the body under 200 lines and
   every line a fact an agent would otherwise rediscover — NEVER paste raw
   `df` or package lists a command answers in one call. Refresh → keep every
   hand-added fact the scan cannot see; change only what the scan proves stale.
   Completion criterion: the draft's `name` is `server-<host>`, equal to its
   directory.

6. **Write.** New → write it. Existing → show `diff -u` of the old file against
   the draft and ask; NEVER overwrite without that answer. NEVER write a secret
   value. NEVER edit `LOCAL.md` — list which of its lines the memory now covers
   and leave their removal to the user.
   Completion criterion: `python3 ~/.claude/hooks/skill_frontmatter_lint.py
   ~/.claude/skills/server-<host>` reports no error.

## Template

````markdown
---
name: server-<host>
description: Server memory for host <host> — role, services, ports, data dirs, web roots, publishing. Applies only where `hostname -s` prints <host>. NOT for any other machine (use its own server-<hostname>).
when_to_use: "<host>, this server, this host, this machine, which port, which service, restart a service, service logs, deploy here, data dir, web root, publish a page, cron job"
user-invocable: false
---

# <host>

## Identity
<fqdn>, <OS>, <virt or bare metal>. Role: <one line>. Last verified <YYYY-MM-DD>.

## Layout
- `<path>` — <what lives there, who owns it>

## Services
| unit or container | port | restart | logs |
|---|---|---|---|

## Publishing
- <where pages go, what serves them, the URL they land at>

## Secrets
Pointers only, in `~/.claude/LOCAL.md`. NEVER a value in this file.

## Upkeep
- A fact here is wrong or missing → fix it in this file in the same turn and
  bump "Last verified".
- NEVER edit this file from inside dockbox or qemubox: it describes the host.
- Drifted beyond a few lines → re-run `/server-init`.
````

## Review Checklist

- Ran on the host: `CLAUDE_SANDBOX` empty, no sandbox note.
- No sudo, no service touched, no write outside
  `~/.claude/skills/server-<host>/`.
- A refresh showed the diff and had an answer before writing.
- No secret value in the memory; `LOCAL.md` unchanged.
- The memory carries its Upkeep section and passes the frontmatter lint.
