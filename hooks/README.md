# Claude Code Hooks

Lifecycle hooks: keyword routing, language-skill nudges, rule injection,
commit/diary nudges. Scripts install to `~/.claude/hooks/`.

The authoritative wiring (events, matchers, timeouts) is
`../settings-recommended.json` — its `hooks` block is merged into
`~/.claude/settings.json` by the install step. This file is the
overview; the wiring is not restated here.

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

Counts tool calls in `/tmp/claude-commit-nudge`; every 100 calls or 10
minutes re-runs `stop.py`'s commit/diary check mid-session.
Non-blocking, always exits 0.

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
uncommitted changes ("consider /commit") or `$cwd/.diary/` exists with
today's entry missing or >1h stale ("consider /diary"). Pure script, no
LLM call, NEVER pushes.

See ARCHITECTURE.md for per-hook data flow.
