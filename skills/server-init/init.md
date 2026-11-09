# Server init — build or refresh `/etc/server/CLAUDE.md`

Runs natively on the host it describes: a shell on the machine itself, never a
sandbox box. The result is one file an agent reads before touching the machine
— how it is laid out, what it serves and how each thing on it is deployed.
Every line is a fact an agent would otherwise rediscover with several commands.

Where a machine fact goes: a note every session on this machine must see goes
in `/etc/claude-code/CLAUDE.md`, Claude Code's managed file — qemubox pre-writes
it inside its box, and on a host it is written only when already writable,
NEVER with sudo. Everything else about the host goes in `/etc/server/CLAUDE.md`.

## Steps

1. **Refuse in a sandbox.** `CLAUDE_SANDBOX` set, or `/etc/claude-code/CLAUDE.md`
   naming qemubox → stop and say so. NEVER build facts from a box: its
   services and paths describe the sandbox, not the host.
   Completion criterion: `CLAUDE_SANDBOX` is empty and no sandbox note exists.

2. **Go native.** The Claude Code command sandbox has no systemd bus, no docker
   socket and a private network view: `systemctl`, `docker ps` and `ss -ltnp`
   answer wrongly or not at all inside it. ALWAYS run the scan with the
   command sandbox off. `sudo` is for reading only — `docker`, `ss -p`, `du`
   over root-owned trees, root-owned config.
   Completion criterion: `systemctl list-units` and `sudo docker ps` both
   answer.

3. **Name the target.** `/etc/server/CLAUDE.md`. It exists → this run is a
   refresh: read it first; every later step keeps what it holds.
   Completion criterion: "new" or "refresh" is stated.

4. **Scan, read-only.** NEVER start, stop, restart, reload, prune or free
   anything. A command that fails → record the gap, NEVER a guess.
   - **identity**: `uname -n`, `/etc/os-release`, `systemd-detect-virt`,
     `nproc`, `free -h`, `ip -4 -br addr`
   - **disk**: `df -h -x tmpfs -x devtmpfs -x overlay`, then `sudo du -xs`
     over the top consumers (`/srv/data/*`, `/home/*`, `/var/lib/docker`,
     `/var/log`) and `sudo docker system df` — where the space goes, not a dump
   - **layout**: `ls -la /srv /srv/* /opt /var/www /home`; who owns each data
     dir and which ones the agent's user can write
   - **services**: `systemctl list-units --type=service --state=running`, the
     same with `--user`, `sudo docker ps --format
     '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'`, `sudo ss -ltnpH`;
     units installed but not running (`list-unit-files --state=disabled`)
   - **deployments**: for each service, `systemctl cat <unit>` (compose dir,
     `ExecStartPre`, restart policy), the image tags (`sudo docker images`),
     the repo or provisioning role that owns it (the motd, ansible
     `host_vars`, the project's own `CLAUDE.md` § Deploying) and the deploy
     command
   - **features and web**: local `/etc/nginx/sites-enabled/*` or
     `/etc/caddy/Caddyfile` (server names, roots, proxied ports); each public
     name the services announce, with `getent hosts` and a `curl -s -o
     /dev/null -w '%{http_code}'` status
   - **schedules**: `sudo crontab -l`, `crontab -l`, `ls /etc/cron.d`,
     `systemctl list-timers`
   - **notes already written**: `/etc/motd`, `/run/motd.dynamic`,
     `~/.claude/LOCAL.md` (paths, publishing rules, hosts it names)
   Completion criterion: each line above ran, or its gap is recorded.

5. **Ask what a scan cannot know.** At most 5 questions, only the ones still
   open after step 4: the host's role; what matters most or is off-limits;
   where publishing goes; where secrets live (a pointer, NEVER a value).
   Completion criterion: each question answered or skipped by the user.

6. **Draft** from the template below. ALWAYS keep it under 200 lines and every
   line a fact an agent would otherwise rediscover — NEVER paste raw `df`, unit
   lists or package lists a command answers in one call. ALWAYS date every
   number that drifts (free disk, image tags). Refresh → keep every hand-added
   fact the scan cannot see; change only what the scan proves stale; a note
   (motd) that disagrees with the live state goes in as a quirk.
   Completion criterion: the draft follows the template and carries no secret
   value.

7. **Write.** New → `sudo install -d -m 755 /etc/server`, then the draft
   through `sudo tee /etc/server/CLAUDE.md`, mode 0644, owner root. Refresh →
   show `diff -u` of the old file against the draft and ask; NEVER overwrite
   without that answer. NEVER use sudo to write any other file. NEVER edit
   `LOCAL.md` — list which of its lines the facts file now covers and leave
   their removal to the user.
   Completion criterion: `cat /etc/server/CLAUDE.md` works without sudo and
   shows today's "Last verified".

## Template

````markdown
# <host> — server facts

Read by the `server-init` skill; nothing loads this file automatically.
NEVER move it to an auto-loaded path. Last verified <YYYY-MM-DD>.

## Identity
<fqdn>, <OS>, <virt or bare metal>, <cores>, <RAM>. Role: <one line>.
<network position: what reaches it, what it reaches through>

## Disk
<filesystem, size, free on YYYY-MM-DD>; the top consumers; what fills it.

## Layout
- `<path>` — <what lives there, who owns it, writable by the agent or not>

## Services
| unit or container | port | restart | logs |
|---|---|---|---|

## Deployments
- <service> — <repo or role that owns it>, <image or build>, <deploy command>

## Web and publishing
- <server name> → <port or root>; <public name> via <proxy>, <status>
- <where pages go, what serves them, the URL they land at>

## Schedules
- <cron or timer> — <what it runs, its log>

## Quirks
- <a note that disagrees with the live state; a hand edit provisioning will undo>

## Secrets
Pointers only. NEVER a value in this file.

## Upkeep
- A fact here is wrong or missing → fix it in this file (sudo, this file only)
  in the same turn and bump "Last verified".
- Drifted beyond a few lines → re-run the init (`server-init` → `init.md`).
````

## Review Checklist

- Ran natively on the host: `CLAUDE_SANDBOX` empty, no sandbox note, the
  command sandbox off for the scan.
- No service touched, nothing freed; sudo wrote only `/etc/server/CLAUDE.md`.
- A refresh showed the diff and had an answer before writing.
- No secret value in the file; `LOCAL.md` unchanged.
- The file carries its "Last verified" date and its Upkeep section.
