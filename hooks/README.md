# Kronael Hooks

Lifecycle hooks: keyword routing, language-skill nudges, rule injection,
unsafe-command blocks, Markdown formatting, and commit/diary stop checks.
Scripts install to `~/.claude/hooks/`.

Claude wiring (events, matchers, timeouts) is `../settings-recommended.json`;
its `hooks` block is merged into `~/.claude/settings.json` by the install
step. Codex wiring is `../codex-hooks.json`; it installs to
`~/.codex/hooks.json` and calls `codex_hook.py` before delegating to the same
hook scripts.

## The hooks

### prompt_nudge.py (UserPromptSubmit)

Exact-matches prompt keywords and emits `hookSpecificOutput.additionalContext`
telling Claude to invoke the matching skill. That field is the one
UserPromptSubmit output the model reads; `systemMessage` renders in the
transcript for the user and never reaches the model. Routes are `SKILL_KEYWORDS` in
the source. A prompt that starts with `/astra` or `/sol` routes to `/astra` (`/sol` is
its Sol variant);
`ask codex`, `ask astra`, `oracle` and `second opinion` route to `/astra`. All are suppressed inside Codex so it never nudges
Codex to invoke itself. `learn` is deliberately NOT a route — `/learn` is
invoked only explicitly or by `memory_nudge.py`, never because the word
appeared in a prompt.

On the first non-empty prompt of a session it also prepends a `/solve` nudge
(triage + diary/memory load before acting), tracked by the session-keyed
stamp `solve-nudge-{session_id}` in `~/.claude/state` (`lib/state.py`) so
continuations stay silent. A prompt that already invokes `/solve` suppresses it.

Also injects `COMMIT_RULES` on "commit" and `DOCS_RULES` on doc-file mentions.
Meta prompts (hook/agent debugging) are skipped so the hook does not interfere
with its own maintenance.

### pretool_nudge.py (PreToolUse)

Maps the touched file to a language skill by extension/filename
(`EXT_SKILLS` and `skill_for` in the source: `.rs` → `/rs`,
`Dockerfile` → `/ops`, ...) and emits a "follow X conventions" context
nudge, once per session+file; for a code skill (`CODE_SKILLS`) the nudge
adds "Read ~/.claude/skills/software/code.md first." It also blocks true
unsafe shell commands: `git reset --hard`, broad `git add`, amend/no-verify
commits, any recursive `rm` (`-r`, `-R`, `-rf`, `--recursive`),
`gh release create`, and recursive Codex execution inside Codex. `git push` is
NOT blocked here — it is gated by consent in `skills/global` and the settings
`ask` rule, not by the hook.

It also refuses a `gh` command that posts GitHub text whose body fails
`gh_text_lint.py`: `gh pr create`/`edit`, `gh issue create`/`edit`, `gh pr
comment`, `gh issue comment`, `gh pr review`, and a `gh api` call on
`pulls/<N>` or `issues/<N>` that carries a body or on `/reviews`, `/comments`
or `/replies`. Each gh invocation in a call is checked, with its `cd` applied
and its backslash-newline continuations joined, and a heredoc's content is
never read as a command. The body comes from
`--body-file`, `-F <file>`, `-F body=@<file>`, `--input` JSON, a heredoc, or
the inline `--body` (literal or `$(cat <path>)`); a path it cannot read (a
shell variable, a missing or undecodable file), stdin, unparsable JSON and a
required body that is absent (`--fill`, `--web`) are refused too, and an
exception inside the lint refuses rather than allows. The lint is WISDOM § Git
made checkable: a bare `🤖` as the last line and none of the harness footer,
the `**TL;DR:**` lead, no header, table, rule, checkbox or code block past 6
lines in a PR body, the `🤖 ` prefix and 240-char cap on a comment, the size
caps, marketing words, shortened hashes. By hand: `python3
~/.claude/hooks/gh_text_lint.py pr|issue|comment <file>`, with `--draft` and
`--title` for a PR; `pr-draft`, `gh-issue` and `gh-comment` run it as their
completion criterion.

Claude wiring includes file tools and `Bash`. Codex wiring includes file tools,
`apply_patch`, and `exec_command`.

On a PostToolUse payload (fed by `post_tool_nudge.sh`) it instead reflows the
Markdown file a `Write`, `Edit` or `MultiEdit` touched: when the file's
repository — the nearest `.git`, a worktree's `.git` file included — has a root
`.rumdl.toml`, it runs the repository's `node_modules/.bin/rumdl`, else `rumdl`
on PATH, as `rumdl fmt` from that root, so the config's `exclude` patterns
apply. Silent when rumdl ran: Claude Code itself tells the agent a hook changed
the file, and an Edit whose `old_string` spans a reflowed line fails instead of
applying to stale text. One line when rumdl is missing, exits non-zero or
times out, and a timed-out run leaves the file as the tool wrote it. A
repository without `.rumdl.toml`, a file outside any repository and a clone
nested in an opted-in tree are never touched; Codex's `apply_patch` is not a
write it formats. `software/code.md` § Layout and formatting owns the rule a
repository adopts.

### post_tool_nudge.sh (PostToolUse)

Pipes a payload that names a `.md` file through `pretool_nudge.py` first (the
Markdown reflow above); a note from it is the call's only output. Then counts
tool calls in the current repo's git dir; every 100 calls or 10 minutes
re-runs `stop.py`'s commit/diary check mid-session using the original hook
payload. Non-blocking, always exits 0.

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
State: the session-keyed stamp `local-{session_id}` in `~/.claude/state` (`lib/state.py`).

### reclaude.py (PreCompact)

Injects `~/.claude/RECLAUDE.md` before compaction, with a note
instructing the model to preserve the wisdom across the compact.

### stop.py (Stop)

Real `Stop` emits top-level `decision: "block"` if `git status --porcelain
-uno` shows uncommitted changes ("Run /commit"; Codex sees `@commit`) or
today's diary entry is missing or >1h stale ("Run /diary"; Codex sees
`@diary`). The commit nudge repeats at most every 10 minutes
(`NUDGE_INTERVAL`); the diary nudge has no throttle: it repeats on every
Stop until today's entry exists and is under an hour old. When called from
periodic `PostToolUse`, the same checks emit advisory
`hookSpecificOutput.additionalContext` and never block a tool call.

Today's entry is `.diary/YYYYMMDD.md` (UTC date). A worktree is one checkout
of a repo; `git worktree add` makes linked ones beside the main checkout. An
entry git ignores is read from the main worktree, its single uncommitted
copy; any other from the current worktree, since a tracked diary is
committed per branch. A plain repo, a submodule and a `--separate-git-dir`
repo are their own main worktree (linked worktrees: ARCHITECTURE.md), and
`../skills/diary/SKILL.md` § Where to write uses the same rule.

A `git status` that fails inside a repo blocks with its stderr — the tree is
reported as unreadable rather than assumed clean.

Under the `ship` CLI ([kronael/ship](https://github.com/kronael/ship)), each
`claude` process it starts carries its role in `SHIP_ROLE`. A worker
(`worker-<id>`) gets both nudges — the commit nudge is what makes it commit.
Any other non-empty role (planner, judge, verifier, validator, replanner)
judges rather than builds, and the hook exits silently for it, on Stop and
PostToolUse alike.

The hook reports a missing or stale diary entry and never writes a header —
run `/diary` deliberately when a session is worth recording. Pure script, no
LLM call, NEVER pushes.

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

State: the session-keyed stamps `memory-nudge-{start,done}-{session_id}` in `~/.claude/state` (`lib/state.py`). The `start`
file holds `started_ts count`. Pure script, no LLM call, NEVER pushes.

## Tests

```bash
make test        # from hooks/; make test-all is the verbose run
```

Runs the Makefile's `TEST_FILES` through `uvx --with pyyaml pytest` when
`uvx` is on PATH, since the frontmatter-lint test imports `yaml`; otherwise
through the first `pytest` on PATH (else `~/.local/bin/pytest`), which needs
PyYAML for that file. TEST.md has the manual smoke tests.

See ARCHITECTURE.md for per-hook data flow.
