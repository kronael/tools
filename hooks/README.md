# Kronael Hooks

Lifecycle hooks: keyword routing, language-skill nudges, LOCAL.md injection,
unsafe-command blocks, a GitHub text gate, Markdown formatting, commit/diary
stop checks and a session memory nudge. Scripts install to `~/.claude/hooks/`.

Claude wiring (events, matchers, timeouts) is `../settings-recommended.json`;
its `hooks` block is merged into `~/.claude/settings.json` by the install
step. Codex wiring is `../codex-hooks.json`; it installs to
`~/.codex/hooks.json` and calls `codex_hook.py` before delegating to the same
hook scripts.

Codex 0.163 fires `UserPromptSubmit` and `SubagentStart` the way Claude Code does,
so `prompt_nudge.py` serves both harnesses and a Codex worker, native or
`codex exec`, receives the `/solve` nudge. A new or changed command hook in
`hooks.json` runs only after the owner trusts it in `/hooks`; until then Codex
skips it without a message.

`statusline.py` is the status-line command `settings-recommended.json` sets:
model, context use, and the 5-hour and weekly limits in whole percent.

`skill_frontmatter_lint.py` also lives in `hooks/` and runs on demand, not from
a lifecycle event: from `make skills-frontmatter` and pre-commit. The spec
linter is the standalone [speclint](../speclint/) command. Its README owns
installation and consumer pre-commit integration; the lifecycle is in
`../skills/specs/format.md` § Before commit.

## The hooks

### prompt_nudge.py (UserPromptSubmit + SubagentStart)

Exact-matches prompt keywords and emits `hookSpecificOutput.additionalContext`
telling Claude to invoke the matching skill. That field is the one
UserPromptSubmit output the model reads; `systemMessage` renders in the
transcript for the user and never reaches the model. Routes are `SKILL_KEYWORDS` in
the source. A prompt that starts with `/astra`, and the phrases `ask codex`,
`ask astra`, `oracle` and `second opinion`, route to `/astra`. All are
suppressed inside Codex so it never nudges Codex to invoke itself. `learn` is deliberately NOT a route — `/learn` is
invoked only explicitly or by `memory_nudge.py`, never because the word
appeared in a prompt.

It also nudges `/solve` at the three points where a new task starts that a
hook can see. The first non-empty prompt of a session (triage + diary/memory
load before acting); a prompt that already invokes `/solve` suppresses it. A
prompt after `IDLE_MINUTES` (30) without one, unless it is already routed — a
keyword route, `commit`, a slash command, or the summary a resumed session
opens with: measured over twelve sessions, a prompt after that pause was a new
task twice as often as a continuation, while no opener word or length
separates the two, so there is deliberately no per-prompt nudge. Both read the
session-keyed stamp `solve-nudge-{session_id}` in `~/.claude/state`
(`lib/state.py`): its presence marks the first prompt, its mtime the previous
one. And `SubagentStart`, where the brief is a new task by construction: the
nudge lands before the subagent's first prompt, except for the harness's own
agents (`HARNESS_AGENTS`: `Explore`, `Plan`, …), which follow no skill.

A prompt with no nudge and no route gets no output: the output style and the
wisdom file sit in the system prompt already, and `SKILL_KEYWORDS` holds skill
names and words that mean one skill only, never a plain verb such as `fix` or
`test`. Meta prompts (hook/agent debugging) are skipped so the hook does not
interfere with its own maintenance.

### pretool_nudge.py (PreToolUse)

Maps the touched file to a language skill by extension/filename
(`EXT_SKILLS` and `skill_for` in the source: `.rs` → `/rs`,
`Dockerfile` → `/ops`, ...) and emits a "follow X conventions" context
nudge, once per session+file; for a code skill (`CODE_SKILLS`) the nudge
adds "Read ~/.claude/skills/software/code.md first." It also blocks the
unsafe shell commands `UNSAFE_COMMAND_PATTERNS` in `pretool_nudge.py` names,
and Codex `resume` commands inside Codex. Independent workers, auth checks and
help commands are permitted. A push, `git push` or `rip -g`, is
NOT blocked here: `skills/global` § Git limits every push to the set the user
confirmed, and the settings `ask` rules gate `git push` and a `rip -g` to
`master` or `main`.

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
exception inside the lint refuses rather than allows. A review submit — `gh pr
review`, `gh api` on `/reviews/<id>/events`, a `/reviews` POST whose `--input`
JSON or `-f`/`-F` field carries `event`, or the `submitPullRequestReview`
mutation — is refused unless the newest message the user typed contains
`SUBMIT REVIEW`; the hook reads it from the tail of the payload's
`transcript_path`, skipping tool results, hook feedback (`isMeta`), task
notifications (`origin.kind`) and a subagent's thread (`isSidechain`). No
transcript — Codex, a payload without the field — refuses too: the user
submits by hand. Posting the review without `event` stays PENDING and needs
no ask. The lint is WISDOM § Git
made checkable: `🤖 ` before the first word and the robot nowhere else, none
of the harness footer, the `**TL;DR:**` lead with nothing after it but
`Closes #N` lines, and no bullet, header, table, rule, checkbox or code block
in a PR body, the 240-char cap on a comment, the size caps (400 chars for a
PR, 3,000 for an issue), marketing words, shortened hashes. By hand: `python3
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
first prompt of a session and on pre-compaction; every later prompt is
silent. State: the session-keyed stamp `local-{session_id}` in `~/.claude/state` (`lib/state.py`).

### reclaude.py (PreCompact)

Injects `~/.claude/RECLAUDE.md` before compaction, with a note
instructing the model to preserve the wisdom across the compact.

### stop.py (Stop)

Real `Stop` emits top-level `decision: "block"` if `git status --porcelain
-uno` shows uncommitted changes ("Run /commit"; Codex sees `@commit`) or
today's diary entry is missing or >1h stale ("Run /diary"; Codex sees
`@diary`). Each nudge repeats at most every 10 minutes (`NUDGE_INTERVAL`),
on its own stamp in the git dir, until the tree is committed or today's
entry exists and is under an hour old. When called from
periodic `PostToolUse`, the same checks emit advisory
`hookSpecificOutput.additionalContext` and never block a tool call.

Today's entry is `~/.claude/projects/<slug>/diary/YYYYMMDD.md` (UTC date),
keyed on the repo's main worktree — the first entry of `git worktree list`,
so every linked worktree reads the same file (rule: `../skills/diary/SKILL.md`
§ Where it lives; detail: ARCHITECTURE.md). A diary inside the repo does not
count.

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
  idiom `local.py`/`reclaude.py` use on PreCompact. Also writes a
  per-session `done` marker so the Stop fallback below stays quiet.
- **Stop** — the fallback for sessions that never compact. Fires **at most
  once per session**, on the first Stop where either `SESSION_THRESHOLD`
  (30 min) wall-clock has elapsed OR `STOP_COUNT_THRESHOLD` (3) Stops have
  occurred. The count path covers *short* sessions that never near 30 min;
  one/two-turn trivia stays under the count and never nudges. Emits
  `hookSpecificOutput.additionalContext`, like `stop.py`'s PostToolUse path.

State: the session-keyed stamps `memory-nudge-{start,done}-{session_id}` in `~/.claude/state` (`lib/state.py`). The `start`
file holds `started_ts count`. Pure script, no LLM call, NEVER pushes.

`codex-hooks.json` does not wire it: Codex runs `stop` on Stop and `local` +
`reclaude` on PreCompact only.

## Tests

```bash
make test        # from hooks/; make test-all is the verbose run
```

Runs the Makefile's `TEST_FILES` through `uvx --with pyyaml pytest` when
`uvx` is on PATH, since the frontmatter-lint test imports `yaml`; otherwise
through the first `pytest` on PATH (else `~/.local/bin/pytest`), which needs
PyYAML for that file. TEST.md has the manual smoke tests.

See ARCHITECTURE.md for each hook's input, output and flow.
