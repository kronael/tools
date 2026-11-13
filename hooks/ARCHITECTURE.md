# Hooks Architecture

## Overview

```
User Prompt ──> UserPromptSubmit ──> prompt_nudge.py (keyword → command/agent;
                                                      /solve on a new task;
                                                      caveman budget line)
                                 ──> local.py        (LOCAL.md on first prompt)

Subagent ──> SubagentStart ──> prompt_nudge.py (/solve for the brief)

Tool call ──> PreToolUse  ──> pretool_nudge.py   (file info / unsafe block / GitHub text gate)
                          ──> reply_gate.py      (SendUserMessage: caveman line ceiling)
          ──> PostToolUse ──> post_tool_nudge.sh (rumdl fmt on a written .md via
                                                  pretool_nudge.py; periodic
                                                  commit/diary nudge)

Claude stops ──> Stop ──> stop.py       (commit + diary block)
                      ──> memory_nudge.py (session memory, once/session fallback)

Compaction ──> PreCompact ──> local.py        (LOCAL.md)
                          ──> reclaude.py     (RECLAUDE.md + preservation note)

Compaction complete ──► SessionStart (compact) ──► memory_nudge.py (memory pass request)
```

Claude event/matcher wiring is owned by `../settings-recommended.json`.
Codex event/matcher wiring is owned by `../codex-hooks.json`; every Codex hook
first runs through `codex_hook.py`.

## Components

### lib/ (shared modules, not hooks)

`state.py` — per-session throttle stamp paths, the state root, and
`hook_event(data)`, which reads the event key across all three spellings.

`local.py`, `memory_nudge.py`, `prompt_nudge.py`, `pretool_nudge.py`,
`reclaude.py` and `reply_gate.py` import it as `lib.state`, resolved from the
hook script's own directory (`sys.path[0]`), so an install that omits the
directory tracebacks on every prompt and every tool call. `stop.py`
imports nothing from it: it carries its own `hook_event`, which checks
`KRONAEL_HOOK_EVENT` before the three payload keys.

`caveman.py` — `caveman_selected(home)`: whether `~/.claude/settings.json`
selects the caveman output style. `prompt_nudge.py` and `reply_gate.py` import
it as `lib.caveman`.

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

### prompt_nudge.py (UserPromptSubmit + SubagentStart)

**Input:** JSON with `prompt` field; on `SubagentStart`, `agent_type` and the
parent's `session_id` instead.
**Output:** `{"hookSpecificOutput": {"hookEventName": "<event>",
"additionalContext": "..."}}` or silent exit. `additionalContext` reaches the
model; `systemMessage` reaches only the user.

**Flow:**
0. On `SubagentStart`, emit `SUBAGENT_NUDGE` (run `/solve` on the brief) and
   stop; silent for `HARNESS_AGENTS`. The parent's first-prompt stamp is not
   touched.
1. Skip meta prompts (hook/agent debugging) to avoid self-interference;
   they get only `CAVEMAN_NUDGE`.
2. On the first non-empty prompt of a session, prepend `SOLVE_NUDGE` (run
   `/solve` to triage before acting), unless the prompt already invokes
   `/solve`. On a later prompt, prepend `IDLE_NUDGE` when `IDLE_MINUTES` have
   passed since the previous prompt and `is_routed` is false — no keyword
   route, no `commit`, no slash command, not a resumed session's summary.
   Every later prompt restamps the gap, routed or not. Other continuations
   stay silent.
3. Preserve a leading workflow command. Route explicit dispatch to `/dispatch`
   and opinion requests to `/oracle`, retaining the original override text.
4. Route explicit model requests to `/dispatch`, and provider requests to
   `/codex` or `/claude`. Both harnesses use these routes. Bare model-like
   words and paths do not select a model; the hook never chooses effort.
5. Tokenise prompt and exact-match words against `SKILL_KEYWORDS` — skill
   names and words that mean one skill only, never a plain verb. A trailing
   `s` singular/plural alias is allowed; edit-distance matching is not.
6. Emit the first exact route as `info: Invoke /<skill>.`.
7. Append `CAVEMAN_NUDGE` to every prompt while `~/.claude/settings.json`
   selects the caveman style, never under Codex. It names the § Budget tiers
   and the 40-column unit; the rules stay in the style file. A prompt with no
   nudge, no route and another style gets no output.

**State:** the session-keyed stamp `solve-nudge-{session_id}` in
`~/.claude/state` (`lib/state.py`): its presence marks that a session's first
prompt has been seen, its mtime is the previous prompt's time. An unwritable
state dir falls back to silence, never a per-prompt nudge.

**Routes:** `SKILL_KEYWORDS` dict in the source.
Codex sees matched Kronael routes as `@skill` instead of `/skill`.

### pretool_nudge.py (PreToolUse; PostToolUse via post_tool_nudge.sh)

**Input:** JSON with `tool_name`, `tool_input` (`file_path`, `notebook_path`,
`command`, `cmd`, or `apply_patch` patch text), `session_id`,
`transcript_path`, and the event (`hook_event_name`, read via
`lib/state.py`).
**Output:** `{"decision": "block", "reason": "..."}`,
`hookSpecificOutput.permissionDecision` with its reason,
`hookSpecificOutput.additionalContext`, or silent.

**PostToolUse flow** (`format_markdown`):
1. Not a `Write`/`Edit`/`MultiEdit` of an existing `.md` → silent.
2. Walk up from the file to the first directory holding `.git` (a worktree's
   `.git` file included); none, or no `.rumdl.toml` there → silent: the
   repository did not opt in, and a nested clone never inherits a config.
3. Run `<root>/node_modules/.bin/rumdl`, else `rumdl` on PATH, as
   `rumdl fmt -- <path relative to root>` from the root, so the config's
   `exclude` applies; `RUMDL_TIMEOUT_S` caps the run.
4. Exit 0 → silent (Claude Code reports a file a hook changed, and an Edit
   whose `old_string` spans a reflowed line fails rather than applying to stale
   text). Non-zero exit → one line with rumdl's first output line; no binary,
   a timeout or an OS error → one line, and a timed-out run gets the written
   bytes back.

**PreToolUse flow:**
1. For shell tools (`Bash`, Codex `exec_command`), `unsafe_command_reason`
   applies the shell guards documented in `README.md` § pretool_nudge.py.
   Codex calls also reject recursive `codex resume` or `codex exec resume`.
   Then `gh_text_lint.command_reason` checks each `gh` invocation that posts a
   PR body, an issue body or a comment is blocked when the body it carries
   fails the lint, cannot be read, or is required and absent. The reason names
   the failing lines and the skill that owns the text. A segment that submits
   findings, where `github_action` returns `SUBMIT`, is blocked unless the
   latest human prompt contains `SUBMIT REVIEW`; no transcript blocks.
   Then `command_action` checks for an approving review or PR merge.
   Claude receives a `PreToolUse` native `ask` in every permission mode; a
   mode that cannot show the prompt (`-p`, `dontAsk`) denies it there. This
   hook returns `deny` to Codex with the pending command, because a Codex
   `PreToolUse` hook cannot request approval: the adapter forwards this
   decision. The denial directs the human to execute the command or use an
   interactive Claude session.
   Each decision is emitted on every call, outside the
   file-nudge dedup cache. A command that passes them and names a file step 3
   maps to `/wisdom` gets that nudge; commands share one dedup key, so it
   fires once per session.
2. For file tools, extract `file_path`, `notebook_path`, or explicit
   `apply_patch` file headers.
3. Map path to a skill: special filenames first (an instruction file →
   `/wisdom`, `pyproject.toml` → `/py`, `Makefile` → `/mk`,
   `Dockerfile`/compose/workflows → `/ops`), then extension via
   `EXT_SKILLS` (`.rs` → `/rs`, `.html` → `/htmx`, ...).
4. Dedupe per session+file via `~/.claude/tmp/extnudge/{sid}.txt` so
   each nudge fires once.
5. Emit "Editing/reading <file> — follow <skill> conventions.", plus
   " Read ~/.claude/skills/software/code.md first." when the skill is in
   `CODE_SKILLS`.
Codex sees `<skill>` as `@py`, `@go`, etc.

The action check covers visible supported `gh` commands. It does not enforce
GitHub branch protection or cover arbitrary scripts, aliases, curl, browsers or
all MCP tools. Disabled, untrusted, failing or timed-out hooks cannot protect a
call. A configured interactive host must still demonstrate its prompt behavior.
The installed hook and its active wiring determine which guard runs; an edited
source file does not prove that the runtime uses it.

Native tool approval is separate from hook output. Submit an authorized command
through the native execution tool within the active session restrictions. Use
its approval request when supported and permitted; do not add a chat gate or
change permission settings. `approval_policy=never` prevents approval requests,
not all normal command execution. A missing dialog alone does not establish a
refusal. Report the actual tool result; success does not prove a fresh human
approval. A hook or tool denial remains binding. In Codex, `PermissionRequest`
handles a request that already exists; it cannot create one from `PreToolUse`.
See the [Codex hook contract](https://learn.chatgpt.com/docs/hooks#pretooluse).

### gh_text_lint.py (library + CLI)

**Input:** a text kind (`pr`, `issue`, `comment`) and the text, or a shell
command plus its `cwd`.
**Output:** `lint` returns `Problem(line, text)` records; `command_reason`
returns the block reason for a posting command, or None; the CLI prints
`<file>:<line>: <problem>` lines and exits 1, or `ok: <kind> <chars> chars`.

The rules are WISDOM § Git and the Format section of the posting skill, kept
to what a program can check. `mark_heredocs` replaces each heredoc's content
with a marker. The shell scan inspects executable command substitutions in
unquoted heredocs, including tab-stripping heredocs. Quoted or escaped
delimiters suppress expansion. Escaped substitution markers and plain command
prose remain literal. The scan also recognizes executable brace groups and
respects shell escapes and quoted command text. Backslash-newline
continuations are joined, and `find_posts` locates visible gh
invocations that post. Each one is checked over its own slice of the
command with the `cd` calls before it applied to `cwd`. `read_bodies` finds
the text a slice posts in `--input` JSON (file or heredoc), `--body-file`,
`-F <file>`, `-F body=@<file>`, a heredoc, or the inline `--body` (literal or
`$(cat <path>)`); a `$VAR` path, stdin, a missing or undecodable file,
unparsable JSON or a command substitution is an OSError the gate reports, and
any other exception becomes the block reason. `github_action` recognises review
submissions, approvals and merges in CLI, REST and GraphQL forms; ambiguous
relevant input is refused. GraphQL inspection is bounded: block-string bodies
and unresolved body values are refused. `command_action` checks each visible
invocation, including command substitutions. `latest_prompt` walks the transcript
backwards in 64 KiB chunks, skips tool-result lines before parsing, and
returns the first `type: user` record that is not `isMeta`, not `isSidechain`
and whose `origin.kind` is `human` or absent. Imported by `pretool_nudge.py`;
run by hand from `pr-draft` (with `--draft` and `--title`), `gh-issue` and
`gh-comment`.

### reply_gate.py (PreToolUse on SendUserMessage)

**Input:** JSON with `tool_name`, `tool_input.message` and `session_id`;
`~/.claude/settings.json` `outputStyle`.
**Output:** `hookSpecificOutput.permissionDecision` `deny` with the measured
line count and a one-time key, `hookSpecificOutput.updatedInput` with the key
line removed from `message`, or silent.

`SendUserMessage` is the brief-mode reply tool: with `claude --brief` and
`defaultView` `chat`, its `message` is the only text the user reads. A
PreToolUse denial stops the call before delivery, and the model writes the
shorter message itself. A Stop hook sees a reply after the terminal shows it,
so a block there adds a second copy. A `MessageDisplay` hook can replace the
lines on screen, but the model does not learn which lines the user read.

`CAP_LINES` is the 20-line hard ceiling of `../output-styles/caveman.md`
§ Budget and `COLUMNS` its 40-column unit; `test_reply_gate.py` asserts the
style file still states both.

**Flow:**
1. Silent for any other tool, a missing `message`, an `outputStyle` other
   than `caveman`, or an unusable state directory.
2. Read the key in the per-session stamp `reply-gate-{session_id}` in
   `~/.claude/state` (`lib/state.py`) and remove the stamp, so a key covers one
   call. When the first line of `message` is `override <key>` with that key:
   answer `updatedInput`, the call's input with that line and the blank lines
   after it removed from `message`, and no permission decision.
3. Drop fenced code and link targets, then count rendered lines
   (`ceil(len/40)` per source line, a blank line counts one). At or under the
   ceiling: pass.
4. Over the ceiling: write a new key (`secrets.token_hex(4)`) to the stamp and
   deny. The reason gives the count, says the user has not seen the message,
   asks for the answer to the question alone, with the rest left in plain
   text, and names the key and its `override <key>` first line. A key that
   cannot be stored means no denial.

The hook cannot tell the fact, action and explanation tiers apart, so it holds
only the ceiling; the 1-3 and ≤12 tiers stay with the style file. It measures
one call: it cannot see that several calls belong to one reply. Codex does
not wire it: `SendUserMessage` and `outputStyle` belong to Claude Code.

### post_tool_nudge.sh (PostToolUse)

**Input:** original hook payload; state in the current repo's git dir
(`post_tool_nudge`, ts + count).
**Output:** `pretool_nudge.py`'s Markdown note when it has one, else
`stop.py`'s advisory `hookSpecificOutput` every 100 tool calls or 10 minutes,
otherwise silent. Always exits 0 — never blocks a tool call.

**Flow:**
1. A payload naming a `.md` file goes through `pretool_nudge.py` first; a note
   from it is the call's whole output, since two JSON documents on stdout
   parse as none.
2. Increment the call counter.
3. At 100 calls or 600 s, reset state and pipe the original payload to
   `stop.py` with `KRONAEL_HOOK_EVENT=PostToolUse`, so the commit/diary nudge
   also fires mid-session as advisory context.

### local.py (UserPromptSubmit + PreCompact)

**Input:** JSON with `prompt`, `session_id`, `cwd`, and hook event identity
(`hook_event`/`hook_event_name`/`hookEventName`, read via `lib/state.py`).
**Output:** on UserPromptSubmit `{"hookSpecificOutput": {"hookEventName":
"UserPromptSubmit", "additionalContext": "<content>"}}`; on PreCompact
`{"ok": true, "systemMessage": "<content>"}`; or silent.
Codex runs this through `codex_hook.py`; PreCompact context output is
suppressed there to avoid invalid Codex hook JSON.

**Flow:**
1. First prompt per session (tracked via the `local-{sid}` stamp in `~/.claude/state`)
   or `PreCompact` event → inject `~/.claude/LOCAL.md` and `$cwd/LOCAL.md`
   contents. Every later prompt is silent.

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
4. Resolve the diary file (`main_tree`, `diary_file`, below) and check for
   today's `YYYYMMDD.md` (UTC). Missing or >1h stale → append a diary nudge
   when the `claude-diary-nudge` stamp is missing or at least `NUDGE_INTERVAL`
   old, and re-stamp. The directory need not exist; a repo without one is
   nudged to start it. The same stamp covers `rollups_due`, which checks the
   last completed ISO week and last calendar month. A missing week with daily
   entries receives `/compact-memories diary week <YYYY-WNN>`.
   The month owns weeks whose Monday falls in that month, including all seven
   days of each week. Missing completed weeks with daily entries receive exact
   period nudges in chronological order. The missing month receives
   `/compact-memories diary month <YYYY-MM>` only after its final assigned week
   ends at UTC midnight, every assigned week with daily entries has a summary,
   and at least one weekly summary exists. Existing rollups are skipped;
   the hook does not scan historical periods or refresh existing files.
5. Real Stop blocks with the combined message and stops there. Periodic
   PostToolUse emits the same message as advisory context only.
Pure script, no LLM call. NEVER pushes. The hook reports a missing or stale
diary; it never writes a diary header. State:
`<git-dir>/claude-commit-nudge` and `<git-dir>/claude-diary-nudge` (one
throttle stamp per nudge).

**Diary file:** `~/.claude/projects/<slug>/diary/YYYYMMDD.md`, never inside
the repo. `<slug>` is the first entry of `git worktree list --porcelain`
(the main tree) with every non-alphanumeric character replaced by `-`, so
every worktree of a repo reads the same file. Git lists the git dir, not the
checkout, for a submodule or a `--separate-git-dir` repo; the slug follows
that path, and `../skills/diary/SKILL.md` § Where it lives names the same
tree. Change both together. Outside a repo the hook checks nothing.

### memory_nudge.py (SessionStart compact + Stop)

**Input:** JSON with `session_id`, `stop_hook_active`, `source`, and hook
event identity (`hook_event`/`hook_event_name`/`hookEventName`, read via
`lib/state.py`). The recommended `SessionStart` matcher is `compact`.
**Output:** `hookSpecificOutput.additionalContext`, with `hookEventName`
set to `SessionStart` or `Stop`. Silent on other events or on `SessionStart`
with another source.

The prompt requests `/learn`'s memory pass against the recorded session
transcript. It requests the shared evidence check, qualifying durable memory,
and a report of what qualified or that nothing qualified. It does not invoke
the skill or lint pass. Emitting the request does not prove that the model
runs learn or saves memory.

`SessionStart` supplies context after compaction. Claude discards
`PreCompact.systemMessage`, so the memory nudge uses the supported
`additionalContext` field. Event contracts:
[SessionStart](https://code.claude.com/docs/en/hooks#sessionstart),
[PreCompact](https://code.claude.com/docs/en/hooks#precompact).

**Flow:**
1. Exit silently if `stop_hook_active` is set, to prevent recursion.
2. On `SessionStart` with `source: compact`, emit after each manual or auto
   compaction. Write the session's `done` marker to suppress later Stop nudges.
   An existing marker does not suppress another compact event.
3. On `Stop`: silent if the `done` marker exists. Otherwise read the `start`
   file (`started_ts count`); the first Stop just records `now 1` and waits.
   Each later Stop increments the count. Emit when either 30 minutes pass
   since the first Stop (`SESSION_THRESHOLD`) or the count reaches 3
   (`STOP_COUNT_THRESHOLD`). Mark `done` to keep this fallback once per session.

**State:** `memory-nudge-{start,done}-{session_id}` in `~/.claude/state`
(`lib/state.py`), keyed by session rather than `cwd`. The marker records
emission, not completion of learn. Pure script, no LLM call. Never blocks or pushes.

The Codex adapter has no `memory_nudge` target, and `codex-hooks.json` does
not wire this hook. The shared skills do not imply automatic Codex delivery.

## Error Handling

`pretool_nudge.py` wraps `main()` in `suppress(Exception)` and exits 0. The
other Python hooks catch `json.JSONDecodeError`, `EOFError` and `ValueError` on
the payload and exit 0. `stop.py` lets an OS error escape: a `cwd` that does
not exist raises `FileNotFoundError` from its first `git` call and exits 1,
which Claude Code shows and does not treat as blocking. `post_tool_nudge.sh`
always exits 0, and a rumdl run that fails or times out becomes a context
note rather than an exit code.

## Extension Points

**Add a new keyword route** — edit `SKILL_KEYWORDS` in `prompt_nudge.py`.

**Add a new stop nudge** — append to the `parts` list in `stop.py`. Keep
checks cheap (no network, no LLM) and guard with a path/directory probe
so the hook stays silent in projects that don't use the feature.

**Add a new injected file** — model it on `local.py` (first prompt +
`PreCompact`, negation-aware) or `reclaude.py` (`PreCompact` only).
