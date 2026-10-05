# Hooks Architecture

## Overview

```
User Prompt ──> UserPromptSubmit ──> prompt_nudge.py (keyword → command/agent)
                                 ──> local.py        (LOCAL.md on first prompt)

Tool call ──> PreToolUse  ──> pretool_nudge.py   (file info / unsafe block)
          ──> PostToolUse ──> post_tool_nudge.sh (periodic commit/diary nudge)

Claude stops ──> Stop ──> stop.py       (commit + diary block)
                      ──> memory_nudge.py (session memory, once/session fallback)

Compaction ──> PreCompact ──> local.py        (LOCAL.md + RULES)
                          ──> reclaude.py     (RECLAUDE.md + preservation note)
                          ──> memory_nudge.py (session memory, unconditional)
```

Claude event/matcher wiring is owned by `../settings-recommended.json`.
Codex event/matcher wiring is owned by `../codex-hooks.json`; every Codex hook
first runs through `codex_hook.py`.

## Components

### lib/ (shared modules, not hooks)

`state.py` — per-session throttle stamp paths, the state root, and
`hook_event(data)`, which reads the event key across all three spellings.

`local.py`, `memory_nudge.py`, `prompt_nudge.py` and `reclaude.py` import it as
`lib.state`, resolved from the hook script's own directory (`sys.path[0]`), so
an install that omits the directory tracebacks on every prompt. `stop.py`
imports nothing from it: it carries its own `hook_event`, which checks
`KRONAEL_HOOK_EVENT` before the three payload keys.

### codex_hook.py (Codex adapter)

**Input:** Codex hook JSON, which may use Codex field names.
**Output:** delegated hook stdout.

**Flow:**
1. Normalize payload fields to the Claude hook shape:
   `cwd`, `session_id`, `hook_event`, `prompt`, `tool_name`, `tool_input`.
2. Dispatch to one installed target hook under `~/.claude/hooks/`.
3. Translate Claude output for Codex: strip Claude-only `ok`, promote
   `systemMessage` to `hookSpecificOutput.additionalContext` for prompt/tool
   hooks, and rewrite Kronael nudge refs from `/skill` to `@skill`.
4. For Codex `PreCompact`, suppress context-only `systemMessage` output because
   Codex only accepts block decisions for that event; forward
   `decision:block` if a hook emits one.
5. Forward Stop `decision:block` output after the same nudge-ref rewrite, so
   commit/diary nudges work in both runtimes.

This keeps the business logic in one hook implementation while allowing Codex
and Claude to use different lifecycle wiring.

### prompt_nudge.py (UserPromptSubmit)

**Input:** JSON with `prompt` field.
**Output:** `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
"additionalContext": "..."}}` or silent exit. `additionalContext` reaches the
model; `systemMessage` reaches only the user.

**Flow:**
1. Skip meta prompts (hook/agent debugging) to avoid self-interference.
2. On the first non-empty prompt of a session, prepend `SOLVE_NUDGE` (run
   `/solve` to triage before acting), unless the prompt already invokes
   `/solve`. Continuations stay silent.
3. If prompt mentions `todo|readme|changelog|spec|architecture|*.md`,
   append `DOCS_RULES`.
4. In Claude only, route a prompt that starts with `/astra` or `/sol` to that
   skill; route `ask codex`, `ask astra`, `oracle`, and `second opinion` to
   `/astra`.
5. Match model escalation only when explicit: `/fable`, `use fable`,
   `spawn fable`, `/opus`, etc.
6. Tokenise prompt and exact-match words against `SKILL_KEYWORDS`. A trailing
   `s` singular/plural alias is allowed; edit-distance matching is not.
7. If prompt contains `commit`, append `COMMIT_RULES`; otherwise emit the
   first exact route as `info`.

**State:** the session-keyed stamp `solve-nudge-{session_id}` in
`~/.claude/state` (`lib/state.py`) marks that a session's first prompt has
been seen. An unwritable state dir falls back to silence,
never a per-prompt nudge.

**Routes:** `SKILL_KEYWORDS` dict in the source.
Codex sees matched Kronael routes as `@skill` instead of `/skill`.

### pretool_nudge.py (PreToolUse)

**Input:** JSON with `tool_name`, `tool_input` (`file_path`, `notebook_path`,
`command`, `cmd`, or `apply_patch` patch text), `session_id`.
**Output:** `{"decision": "block", "reason": "..."}`,
`hookSpecificOutput.additionalContext`, or silent.

**Flow:**
1. For shell tools (`Bash`, Codex `exec_command`), block true unsafe commands:
   amend, hard reset, broad add, no-verify commits, `rm -rf`, and
   recursive Codex execution inside Codex.
2. For file tools, extract `file_path`, `notebook_path`, or explicit
   `apply_patch` file headers.
3. Map path to a skill: special filenames first (`Makefile` → `/mk`,
   `Dockerfile`/compose/workflows → `/ops`), then extension via
   `EXT_SKILLS` (`.rs` → `/rs`, `.html` → `/htmx`, ...).
4. Dedupe per session+file via `$TMPDIR/claude-extnudge/{sid}.txt` so
   each nudge fires once.
5. Emit "Editing/reading <file> — follow <skill> conventions."
Codex sees `<skill>` as `@py`, `@go`, etc.

### post_tool_nudge.sh (PostToolUse)

**Input:** original hook payload; state in the current repo's git dir
(`post_tool_nudge`, ts + count).
**Output:** `stop.py`'s advisory `hookSpecificOutput` every 100 tool calls or
10 minutes, otherwise silent. Always exits 0 — never blocks a tool call.

**Flow:**
1. Increment the call counter.
2. At 100 calls or 600 s, reset state and pipe the original payload to
   `stop.py` with `KRONAEL_HOOK_EVENT=PostToolUse`, so the commit/diary nudge
   also fires mid-session as advisory context.

### local.py (UserPromptSubmit + PreCompact)

**Input:** JSON with `prompt`, `session_id`, `cwd`, and hook event identity
(`hook_event`/`hook_event_name`/`hookEventName`, read via `lib/state.py`).
**Output:** `{"ok": true, "systemMessage": "<content>"}` or silent.
Codex runs this through `codex_hook.py`; PreCompact context output is
suppressed there to avoid invalid Codex hook JSON.

**Flow:**
1. First prompt per session (tracked via the `local-{sid}` stamp in `~/.claude/state`)
   or `PreCompact` event → inject `~/.claude/LOCAL.md` and `$cwd/LOCAL.md`
   contents.
2. On continue/recap keywords (respecting negation), append `RULES`.
3. On `PreCompact`, always append `RULES`.

### reclaude.py (PreCompact)

**Input:** JSON with hook event identity
(`hook_event`/`hook_event_name`/`hookEventName`, read via `lib/state.py`).
**Output:** `{"ok": true, "systemMessage": "<RECLAUDE.md>"}` or silent.
Codex runs this through `codex_hook.py`; PreCompact context output is
suppressed there to avoid invalid Codex hook JSON.

**Flow:**
1. Reads `~/.claude/RECLAUDE.md`; silent exit if missing.
2. On `PreCompact`, injects the content with an appended preservation
   note so the wisdom survives compaction.

The script also has a continue/recap-keyword trigger path, but the
recommended wiring runs it on `PreCompact` only — the keyword path is
unwired.

### stop.py (Stop)

**Input:** JSON with `cwd`, `session_id`, `stop_hook_active`; env
`SHIP_ROLE`, `CLAUDE_EVAL`, `KRONAEL_HOOK_EVENT`.
**Output:** `{"decision": "block", "reason": "..."}` on real Stop,
advisory `hookSpecificOutput.additionalContext` on PostToolUse, or silent.

**Flow:**
1. With `CLAUDE_EVAL` set, or `SHIP_ROLE` set and not starting with
   `worker`, exit silently before any git call and before the event split,
   so PostToolUse is silent too. The `ship` CLI sets `SHIP_ROLE` per
   `claude` child (`planner`, `judge`, `verifier`, `validator`,
   `replanner`, `worker-<id>`); only workers build and commit.
2. With `stop_hook_active` set, skip the nudges — this prevents recursion, and
   with nothing left to say the hook is silent.
3. Check `git status --porcelain -uno`; if dirty and the stamp is missing or
   at least `NUDGE_INTERVAL` (600 s) old, append a commit nudge with
   `git diff --stat` and re-stamp. A failed `git status` inside a repo
   appends its stderr instead, unthrottled — an unreadable tree is reported,
   never read as clean.
4. Resolve the diary tree (`diary_trees`, below) and check for today's
   `YYYYMMDD.md` (UTC) under its `.diary/`. Missing or >1h stale → append a
   diary nudge on every Stop; no stamp throttles it. The directory need not
   exist; a repo without one is nudged to start it.
5. Real Stop blocks with the combined message and stops there. Periodic
   PostToolUse emits the same message as advisory context only.
Pure script, no LLM call. NEVER pushes. The hook reports a missing or stale
diary; it never writes a diary header. State:
`<git-dir>/claude-commit-nudge` (commit nudge throttle).

**Diary tree:** an ignored diary is never committed, so its one copy lives
in the main worktree; any other is committed per branch and read in the
current worktree. The check tests the dated file: a `.diary/` ignore rule
matches the bare `.diary` only once the directory exists.

```
git_dir = rev-parse --absolute-git-dir
common  = rev-parse --path-format=absolute --git-common-dir
current = rev-parse --show-toplevel
     │
     v
same realpath(git_dir, common)? ──yes──> main = current
     │                               (plain repo, submodule,
     │ no: linked worktree            --separate-git-dir repo)
     v
core.worktree in <common>/config? ──yes──> main = <common>/<value>
     │                                     (worktree of a submodule)
     │ no
     v
main = dirname(<common>)                   (worktree of a plain repo)

check-ignore -q .diary/YYYYMMDD.md, run in current
     │
     ├── ignored ─────> <main>/.diary/YYYYMMDD.md
     └── not ignored ──> <current>/.diary/YYYYMMDD.md
```

`dirname(<common>)` cannot be the general rule: a submodule's or a
`--separate-git-dir` repo's common dir is a git dir stored elsewhere, so its
parent is not their checkout. Git records no main tree for a
linked worktree of a `--separate-git-dir` repo; there the last branch yields
the git dir's parent, and an ignored diary is looked for beside the git dir.
`../skills/diary/SKILL.md` § Where to write resolves `<main>` the same way;
change both together.

### memory_nudge.py (PreCompact + Stop)

**Input:** JSON with `cwd`, `session_id`, `stop_hook_active`, and hook event
identity (`hook_event`/`hook_event_name`/`hookEventName`, read via
`lib/state.py`).
**Output:** `PreCompact` → `{"ok": true, "systemMessage": "..."}` (local.py /
reclaude.py idiom). `Stop` → `hookSpecificOutput.additionalContext` (stop.py
PostToolUse idiom). Silent otherwise.

**Flow:**
1. Bail if `stop_hook_active` is set.
2. On `PreCompact`: always emit the memory-review nudge, then write a
   per-session `done` marker so the Stop fallback stays silent.
3. On `Stop`: silent if the `done` marker exists. Otherwise read the `start`
   file (`started_ts count`); the first Stop just records `now 1` and waits.
   Each later Stop bumps the count; once `now - started >= SESSION_THRESHOLD`
   (30 min) OR `count >= STOP_COUNT_THRESHOLD` (3), emit once and mark `done`.
   The count gate is what reaches *short* sessions that never compact and
   never approach 30 min.

State: the `memory-nudge-{start,done}-{session_id}` stamps in `~/.claude/state` (`lib/state.py`). Much lower
frequency than stop.py's recurring diary/commit nudges — at most once via
PreCompact plus at most once via the Stop fallback. Pure script, no LLM call.

## Data Flow

### UserPromptSubmit

```
stdin:
{
  "prompt": "improve the error handling",
  "hook_event": "UserPromptSubmit",
  "session_id": "abc123",
  "cwd": "/project"
}

stdout (prompt_nudge.py match):
{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "Invoke /improve."}}
```

### Stop

```
stdin:
{
  "cwd": "/project"
  // "stop_hook_active": true — field absent when inactive; Claude Code only sends it when true
}

stdout (dirty tree + stale diary; commit guidance elided):
{
  "decision": "block",
  "reason": "Uncommitted changes detected.\n<diff stat>\nCommit your work — ... Run /commit.\nRules: ...\nDiary not updated in over an hour (now 16:52 2026-10-01). Run /diary deliberately if there is work to record."
}

stdout (nothing to nudge, or a judging SHIP_ROLE): empty
```

Codex rewrites known Kronael refs in nudge output, e.g. `Run @commit` and
`Run @diary`.

## Error Handling

All Python hooks catch `json.JSONDecodeError`, `EOFError`, `ValueError`
and bail with exit 0 so a broken payload never blocks the session. File
I/O errors are swallowed for the same reason. `post_tool_nudge.sh`
always exits 0.

## Extension Points

**Add a new keyword route** — edit `SKILL_KEYWORDS` in `prompt_nudge.py`.

**Add a new stop nudge** — append to the `parts` list in `stop.py`. Keep
checks cheap (no network, no LLM) and guard with a path/directory probe
so the hook stays silent in projects that don't use the feature.

**Add a new injected file** — model it on `local.py` (first prompt +
`PreCompact`, negation-aware) or `reclaude.py` (`PreCompact` only).
