# Kronael Hooks

Lifecycle hooks: keyword routing, language-skill nudges, rule injection,
unsafe-command blocks, and commit/diary stop checks. Scripts install to
`~/.claude/hooks/`.

Claude wiring (events, matchers, timeouts) is `../settings-recommended.json`;
its `hooks` block is merged into `~/.claude/settings.json` by the install
step. Codex wiring is `../codex-hooks.json`; it installs to
`~/.codex/hooks.json` and calls `codex_hook.py` before delegating to the same
hook scripts.

## The hooks

### prompt_nudge.py (UserPromptSubmit)

Exact-matches prompt keywords and emits an informational system message telling
Claude to invoke the matching command or agent. Routes are `AGENT_KEYWORDS` in
the source. Codex second-opinion routing is explicit only (`ask codex`,
`oracle`, `second opinion`) and suppressed inside Codex so it never nudges
Codex to invoke itself. `learn` is deliberately NOT a route — `/learn` is
invoked only explicitly or by `memory_nudge.py`, never because the word
appeared in a prompt.

Also injects `COMMIT_RULES` on "commit" and `DOCS_RULES` on doc-file mentions.
Meta prompts (hook/agent debugging) are skipped so the hook does not interfere
with its own maintenance.

### pretool_nudge.py (PreToolUse)

Maps the touched file to a language skill by extension/filename
(`EXT_SKILLS` and `skill_for` in the source: `.rs` → `/rs`,
`Dockerfile` → `/ops`, ...) and emits a "follow X conventions" context
nudge, once per session+file. It also blocks true unsafe shell commands:
`git push`, `git reset --hard`, broad `git add`, amend/no-verify commits,
`rm -rf`, and recursive Codex execution inside Codex.

Claude wiring includes file tools and `Bash`. Codex wiring includes file tools,
`apply_patch`, and `exec_command`.

### post_tool_nudge.sh (PostToolUse)

Counts tool calls in the current repo's git dir; every 100 calls or 10
minutes re-runs `stop.py`'s commit/diary check mid-session using the original
hook payload.
Non-blocking, always exits 0.

### codex_hook.py (Codex adapter)

Normalizes Codex hook payloads into the Claude-style fields the existing hooks
expect (`cwd`, `session_id`, `hook_event`, `prompt`, `tool_name`,
`tool_input`) and delegates to the target hook. Codex should call this wrapper;
do not wire Codex directly to the Claude scripts unless their payload contract
is intentionally changed.

The adapter also translates Claude hook output for Codex: it strips Claude-only
`ok`, promotes `systemMessage` into `hookSpecificOutput.additionalContext` for
prompt/tool hooks, and rewrites Kronael nudge references from `/skill` to
`@skill`. Codex `PreCompact` does not accept context injection JSON, so the
adapter suppresses context-only `systemMessage` output for that event and only
forwards explicit `decision: block` responses.

### local.py (UserPromptSubmit + PreCompact)

Injects `~/.claude/LOCAL.md` (and `$cwd/LOCAL.md` if present) on the
first prompt of a session and on pre-compaction. Re-injects a short
`RULES` block on continue/recap keywords, respecting negation.
State: `$cwd/.claude/tmp/local-{session_id}`.

### reclaude.py (PreCompact)

Injects `~/.claude/RECLAUDE.md` before compaction, with a note
instructing the model to preserve the wisdom across the compact.

### stop.py (Stop)

Real `Stop` emits top-level `decision: "block"` if `git status --porcelain
-uno` shows uncommitted changes ("consider /commit"; Codex sees `@commit`) or
the repo diary has today's entry missing or >1h stale ("consider /diary";
Codex sees `@diary`). When called from periodic `PostToolUse`, the same checks
emit advisory `hookSpecificOutput.additionalContext` and never block a tool
call.

The hook may append a blank diary header for missing/stale diary entries. Pure
script, no LLM call, NEVER pushes.

### memory_nudge.py (PreCompact + Stop)

Reminds the assistant to evaluate the session for memory-worthy content
(corrections, confirmed decisions, project facts, reference pointers) and save
it via the auto-memory mechanism or `/learn` — much rarer than the diary
nudge, tied to the moment context would otherwise be lost:

- **PreCompact** — always nudges (manual or auto). Emits `systemMessage`, the
  same idiom `local.py`/`reclaude.py` use to survive compaction. Also writes a
  per-session `done` marker so the Stop fallback below stays quiet.
- **Stop** — the fallback for sessions that never compact. Fires **at most
  once per session**, on the first Stop where either `SESSION_THRESHOLD`
  (30 min) wall-clock has elapsed OR `STOP_COUNT_THRESHOLD` (3) Stops have
  occurred. The count path covers *short* sessions that never near 30 min;
  one/two-turn trivia stays under the count and never nudges. Emits
  `hookSpecificOutput.additionalContext`, like `stop.py`'s PostToolUse path.

State: `$cwd/.claude/tmp/memory-nudge-{start,done}-{session_id}`. The `start`
file holds `started_ts count`. Pure script, no LLM call, NEVER pushes.

See ARCHITECTURE.md for per-hook data flow.
