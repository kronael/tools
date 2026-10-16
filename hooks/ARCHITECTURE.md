# Hooks Architecture

## Overview

```
User Prompt ──► UserPromptSubmit ──► prompt_nudge.py  (solve + LOCAL.md on the first
                                                        prompt, caveman pointer, routes)

Tool call ──► PreToolUse  ──► pretool_nudge.py   (file skill pointer / unsafe deny /
                                                   GitHub text gate / submit ask)
          ──► PostToolUse ──► pretool_nudge.py   (rumdl fmt on a written .md)
                          ──► stop.py            (commit + diary, every 100 calls or 10 min)
                          ──► style_nudge.py     (tool count; caveman pointer at level 2+)

Claude stops ──► Stop ──► stop.py          (commit + diary block)
                      ──► memory_nudge.py  (learn pointer, once per session)
                      ──► style_nudge.py   (measure the reply, move the level)

                 kvs ◄── every hook reads and writes its memory here
```

Claude event wiring is `../settings-recommended.json`; Codex wiring is
`../codex-hooks.json`, and every Codex hook first runs through `codex_hook.py`.
PreCompact and SessionStart carry no hook: Claude Code discards a PreCompact
hook's `systemMessage`, and the output style survives compaction on its own.

## Components

### lib/ (shared modules, not hooks)

- `reminder.py` — the one XML shape: `skill(name)`, `file(path)`,
  `reminder(skill, rule, text, **measured)`, and the two outputs `context(event,
  *lines)` (`hookSpecificOutput.additionalContext`) and `block(*lines)` (a Stop
  `decision: block`). `emit` prints one JSON document.
- `kvs.py` — the client of the `kvs` CLI: `get`, `set` (with `ttl` and
  `if_old`), `incr`, each passing `-s <session>` and `-p <cwd>`. Every call
  returns None or False when the binary is missing or fails.
- `state.py` — `hook_event(data)`, the lifecycle event across the three key
  spellings.

The hooks import them as `lib.*`, resolved from the script's own directory
(`sys.path[0]`), so an install that omits the directory tracebacks on every call.

### State

Every key lives in `kvs` under the project (the main git tree of `cwd`) and,
where named, the session id from the hook input. Values are text; `caveman`
holds JSON.

| Key | Scope | Hook | Meaning |
|-----|-------|------|---------|
| `prompted` | session | prompt_nudge | set once with `--if ""`: the first prompt was seen |
| `pointed:<skill>:<path>` | session | pretool_nudge | set once per file: its skill pointer was given |
| `tools` | session | style_nudge | tool calls in the current turn; reset to 0 on each prompt |
| `caveman` | session | style_nudge | `{"level": n, "miss": n, "ok": n, <metric>: v, "cap": c}` |
| `commit-nudged` | project | stop | TTL 600 s: the commit pointer was given in this window |
| `tool-calls` | project | stop | tool calls in the current 10-minute window (TTL on creation) |
| `memory:stops`, `memory:started`, `memory:done` | session | memory_nudge | Stop count, first Stop time, the pointer was given |

Inspect a session: `kvs -s <session_id> ls`; the project's sessions: `kvs sessions`.

### prompt_nudge.py (UserPromptSubmit)

**Input:** JSON with `prompt`, `session_id`, `cwd`, optional `harness`.
**Output:** `context('UserPromptSubmit', *lines)` or silent.

**Flow:**
1. A meta prompt (`META_PATTERNS`: hook or agent debugging) gets only the
   caveman pointer, so the hooks never discuss themselves into the routing.
2. First prompt (`kvs set prompted 1 --if ""` succeeds, non-empty prompt):
   `<reminder skill="solve">` unless the prompt invokes `/solve`, then a
   `<file>` pointer for each `LOCAL_FILES` entry that exists.
3. `style_nudge.on_prompt`: resets `tools`, returns the caveman pointer at
   level 1 or higher.
4. `todo|readme|changelog|spec|architecture|*.md` → `<skill name="readme"/>`.
5. `commit` → `<skill name="commit"/>`; else the first route from
   `explicit_route` (astra phrases in Claude only, explicit tier escalation,
   then `SKILL_KEYWORDS` by exact word with a trailing-`s` alias) as
   `<skill name="<route>"/>`, unless that pointer is already in the list.

### style_nudge.py (PostToolUse + Stop)

**Input:** `session_id`, `cwd`, the event; at Stop `last_assistant_message` and
`stop_hook_active`.
**Output:** PostToolUse: the caveman pointer at level 2+. Stop: silent, except
one `<reminder skill="caveman" rule="budget" lines=.. cap=..>revise …</reminder>`
at level 3 for a reply over twice its cap.

**Flow (Stop):**
1. `stop_hook_active`, no message, or nothing visible after removing
   `<status>`/`<think>` blocks and code fences → return.
2. `measure`: rendered lines (`ceil(len/80)` per line, blank lines count),
   the longest list, the most sentences in one bullet.
3. `find_miss` against `cap_for(tools)`: 20 lines, 25 when `tools >= 4`;
   bullets 5; sentences 2. The first broken rule names the miss.
4. Level: miss → +1 (max 3), compliant → −1 (min 0); `miss`/`ok` counters;
   the last miss's values stay for the pointer. Saved as JSON under `caveman`.
5. Level 3 and `lines > 2 * cap` → the revision reminder; else silent.

**Flow (PostToolUse):** `kvs incr tools`; level ≥ 2 → the pointer.
**`on_prompt`** (called by prompt_nudge): `kvs set tools 0`; level ≥ 1 → the pointer.

Without kvs `main` returns before reading the event.

### pretool_nudge.py (PreToolUse; PostToolUse)

**Input:** `tool_name`, `tool_input` (`file_path`, `notebook_path`, `command`,
`cmd`, or an `apply_patch` patch), `session_id`, `cwd`, `harness`, the event.
**Output:** `hookSpecificOutput.permissionDecision` (`deny` or `ask`) with its
reason, `context('PreToolUse', '<skill name="py"/>')`, a PostToolUse rumdl
note, or silent.

**PreToolUse flow:**
1. Shell tools (`Bash`, Codex `exec_command`): deny `UNSAFE_COMMAND_PATTERNS`
   and recursive Codex; then `gh_text_lint.command_decision` on every `gh`
   invocation that posts text (deny on a failing or unreadable body; `ask` on a
   review submit, which becomes a deny under Codex).
2. File tools: `extract_path`, `skill_for` (special names first, then
   `EXT_SKILLS`), `kvs set pointed:<skill>:<path> 1 --if ""` once per session
   and file (every time without kvs), then the pointer.

**PostToolUse flow** (`format_markdown`): a `Write`/`Edit`/`MultiEdit` of an
existing `.md` whose repository root holds `.rumdl.toml` → `rumdl fmt` from
that root with the pinned or PATH binary; exit 0 silent, else one line, and a
timed-out run gets the written bytes back.

### gh_text_lint.py (library + CLI)

`lint(kind, text)` returns `Problem(line, text)` records; `command_decision`
returns a `Decision` for a posting command or None; the CLI prints
`<file>:<line>: <problem>` and exits 1, or `ok: <kind> <chars> chars`. The
rules are WISDOM § Git and the Format section of the posting skill, kept to
what a program can check. `mark_heredocs` keeps heredoc content out of the
command parse, `find_posts` locates every posting `gh` invocation,
`read_bodies` finds the text it posts, `is_submit` recognises a review submit.

### stop.py (Stop; PostToolUse)

**Input:** `cwd`, `session_id`, `stop_hook_active`, the event; env `SHIP_ROLE`,
`CLAUDE_EVAL`.
**Output:** `block(*lines)` on Stop, `context('PostToolUse', *lines)` on
PostToolUse, or silent.

**Flow:**
1. `CLAUDE_EVAL`, a non-worker `SHIP_ROLE`, or `stop_hook_active` → silent.
2. PostToolUse: `kvs incr tool-calls -t 600` (project scope); the check runs
   when the count is 1 (a new window) or a multiple of 100; without kvs never.
3. `commit_nudge`: `git status --porcelain -uno`; a failure inside a repository
   → `<reminder skill="commit">git status failed: …</reminder>`; changed files
   → `kvs set commit-nudged 1 -t 600 --if ""` and, when it was set (or without
   kvs), `<reminder skill="commit" files="N">`.
4. `diary_nudge`: today's `~/.claude/projects/<slug>/diary/YYYYMMDD.md` (UTC),
   `<slug>` = the first entry of `git worktree list --porcelain` with every
   non-alphanumeric replaced by `-`, so every worktree reads one file. Missing
   → `<reminder skill="diary">no diary entry today</reminder>`; older than an
   hour → `<reminder skill="diary" age="Nh">diary not updated</reminder>`.
   A diary inside the repository does not count; outside git nothing is checked.
5. Stop blocks with the lines; PostToolUse emits them as context.

The hook never writes a diary header and never pushes.

### memory_nudge.py (Stop)

**Input:** `session_id`, `cwd`, `stop_hook_active`, the event.
**Output:** `context('Stop', '<reminder skill="learn">…</reminder>')` once, or silent.

**Flow:** `kvs incr memory:stops`; the first Stop records `memory:started` and
returns; later Stops fire when the count reaches `STOP_COUNT_THRESHOLD` (3) or
`SESSION_THRESHOLD` (1800 s) passed since the start, and `kvs set memory:done 1
--if ""` makes the nudge fire once. Codex does not wire it.

### codex_hook.py (Codex adapter)

**Input:** Codex hook JSON, which may use Codex field names.
**Output:** the delegated hook's stdout, translated.

1. `normalize` the payload to the Claude shape and mark `harness: codex`.
2. Run one target of `TARGETS` (`prompt_nudge`, `pretool_nudge`, `stop`).
3. `translate_output`: drop `ok`; rewrite `/skill` → `@skill` in `systemMessage`,
   `reason` and `additionalContext`; promote `systemMessage` to
   `additionalContext` for prompt and tool events; on PreCompact forward only
   `decision: block`.

## Error handling

`pretool_nudge.py` wraps `main()` in `suppress(Exception)` and exits 0. The
other hooks catch `json.JSONDecodeError`, `EOFError` and `ValueError` on the
payload and return. `stop.py` lets an OS error escape: a `cwd` that does not
exist raises from its first `git` call and exits 1, which Claude Code shows and
does not treat as blocking. A `kvs` failure or absence never raises: the client
returns None and the hook forgets.

## Extension points

**Add a keyword route** — `SKILL_KEYWORDS` in `prompt_nudge.py`.

**Add a stop check** — a function returning one `reminder(...)` line or None,
listed in `stop.nudges`. Keep it cheap (no network, no LLM) and silent in
projects that lack the feature.

**Add memory** — a `kvs` key, scoped by session unless the fact is about the
repository; `set --if ""` for once-only, `incr -t` for a counter in a window.
Add its row to § State.
