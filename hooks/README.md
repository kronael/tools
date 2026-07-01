# Kronael Hooks

Lifecycle hooks: keyword routing, language-skill nudges, rule injection,
commit/diary nudges. Scripts install to `~/.claude/hooks/`.

Claude wiring (events, matchers, timeouts) is `../settings-recommended.json`;
its `hooks` block is merged into `~/.claude/settings.json` by the install
step. Codex wiring is `../codex-hooks.json`; it installs to
`~/.codex/hooks.json` and calls `codex_hook.py` before delegating to the same
hook scripts.

## The hooks

### prompt_nudge.py (UserPromptSubmit)

Fuzzy-matches prompt keywords and emits a system message telling Claude
to invoke the matching command or agent. Routes are `AGENT_KEYWORDS` in
the source — read the dict, don't duplicate it. Also injects
`COMMIT_RULES` on "commit" and `DOCS_RULES` on doc-file mentions. Meta
prompts (hook/agent debugging) are skipped so the hook doesn't
interfere with its own maintenance.

### pretool_nudge.py (PreToolUse: Read|Edit|Write|MultiEdit|NotebookEdit)

Maps the touched file to a language skill by extension/filename
(`EXT_SKILLS` and `skill_for` in the source: `.rs` → `/rs`,
`Dockerfile` → `/ops`, ...) and emits a "follow X conventions" context
nudge, once per session+file.

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

Blocks the stop with a reason if `git status --porcelain -uno` shows
uncommitted changes ("consider /commit"; Codex sees `@commit`) or
`$cwd/.diary/` exists with today's entry missing or >1h stale ("consider
/diary"; Codex sees `@diary`). Pure script, no LLM call, NEVER pushes.

See ARCHITECTURE.md for per-hook data flow.
