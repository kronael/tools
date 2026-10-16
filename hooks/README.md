# Kronael Hooks

Lifecycle hooks that point the model at a skill, a file or a measured rule, in
one XML shape, and never paste rule text: keyword routing, the language skill of
a touched file, the caveman budget, unsafe-command blocks, a GitHub text gate,
Markdown formatting, commit/diary stop checks and a session memory check.
Scripts install to `~/.claude/hooks/`.

Claude wiring (events, matchers, timeouts) is `../settings-recommended.json`;
its `hooks` block is merged into `~/.claude/settings.json` by the sync. Codex
wiring is `../codex-hooks.json`; it installs to `~/.codex/hooks.json` and calls
`codex_hook.py` before delegating to the same scripts.

`statusline.py` is the status-line command `settings-recommended.json` sets:
model, context use, and the 5-hour and weekly limits in whole percent.
`skill_frontmatter_lint.py` runs on demand from `make skills-frontmatter` and
pre-commit, not from a lifecycle event.

## What a hook may inject

`lib/reminder.py` is the only writer of context. Three forms, one line each:

- `<skill name="commit"/>` — a pure pointer; the skill holds the rules.
- `<file path="~/.claude/LOCAL.md"/>` — a file worth reading now.
- `<reminder skill="caveman" rule="budget" lines="27" cap="20"/>` — a rule
  anchor with the measured values; optional one-line text inside the element.

A hook that has nothing to point at prints nothing.

## Memory

Hooks are separate processes; what they remember between calls lives in
`kvs` (`../kvs`), the key-value store the sync installs, scoped by the
session id from the hook input and by the project. `lib/kvs.py` is the one
client; when the binary is missing every hook still runs and only forgets:
no first-prompt pointers, no caveman escalation, commit nudges on every Stop.
`ARCHITECTURE.md` § State lists every key.

## The hooks

### prompt_nudge.py (UserPromptSubmit)

The first prompt of a session gets `<reminder skill="solve">` and a `<file>`
pointer for each `LOCAL.md` that exists (`~/.claude/LOCAL.md`, `$cwd/LOCAL.md`).
Every prompt gets the caveman pointer when the last reply missed its budget
(`style_nudge.on_prompt`), `<skill name="readme"/>` on a document mention,
`<skill name="commit"/>` on "commit", else the first exact keyword route from
`SKILL_KEYWORDS`. `/astra`, "ask codex", "oracle" and "second opinion" route to
`astra` in Claude only. A tier name routes only as `/fable` or "use fable".
A prompt about hooks or agents (`META_PATTERNS`) keeps only the caveman pointer.

### style_nudge.py (PostToolUse + Stop)

Caveman adherence with memory. At Stop it measures the final reply after
stripping code fences and `<status>`/`<think>` blocks: rendered 80-column
lines against the cap (20, or 25 after four or more tool calls in the turn),
bullets per list (5) and sentences per bullet (2). A miss raises the session's
level by one, a compliant reply lowers it; Stop itself injects nothing. Level 1
puts `<reminder skill="caveman" rule="budget" lines="27" cap="20"/>` on the
next prompt; level 2 repeats it after every tool call, next to where the reply
is written; at level 3 a reply over twice its cap gets one revision request at
Stop. `kvs` holds the level and the last measurement under the key `caveman`.

### pretool_nudge.py (PreToolUse; PostToolUse)

Points at the language skill of a touched file (`skill_for`: `.rs` → `rs`,
`Dockerfile` → `ops`, `SKILL.md` → `wisdom`), once per session and file.
Denies the unsafe shell commands `UNSAFE_COMMAND_PATTERNS` names and recursive
Codex execution inside Codex. A push is NOT blocked here: `skills/global` § Git
gates it and the settings `ask` rules cover `git push` and `ghpush`.

It refuses a `gh` command that posts GitHub text whose body fails
`gh_text_lint.py`: `gh pr create`/`edit`, `gh issue create`/`edit`, `gh pr
comment`, `gh issue comment`, `gh pr review`, and a `gh api` call on
`pulls/<N>` or `issues/<N>` that carries a body or on `/reviews`, `/comments`
or `/replies`. The body comes from `--body-file`, `-F <file>`, `-F body=@<file>`,
`--input` JSON, a heredoc or the inline `--body`; a body it cannot read is
refused too. A review submit passes the lint, then gets `permissionDecision:
ask`: Claude Code shows the permission dialog, a headless run denies, and under
Codex the hook denies and hands the user the command. The lint is WISDOM § Git
made checkable (`🤖 ` first, no harness footer, the `**TL;DR:**` lead, no
header, table or code block in a PR body, the size caps, marketing words,
shortened hashes). By hand: `python3 ~/.claude/hooks/gh_text_lint.py
pr|issue|comment <file>`.

On PostToolUse it reflows the Markdown file a `Write`, `Edit` or `MultiEdit`
touched when the file's repository has a root `.rumdl.toml`: the repository's
`node_modules/.bin/rumdl`, else `rumdl` on PATH, as `rumdl fmt` from that root.
Silent when rumdl ran; one line when it is missing, fails or times out.

### stop.py (Stop; PostToolUse)

Stop blocks with `<reminder skill="commit" files="N">` when `git status
--porcelain -uno` shows changes (once per 10 minutes per repository, the
`commit-nudged` key) and with `<reminder skill="diary">` when today's entry
under `~/.claude/projects/<slug>/diary/` is missing or over an hour old. A
`git status` that fails inside a repository blocks with its stderr. On
PostToolUse the same check runs as advisory context on the first tool call of
each 10-minute window and every hundredth call (`tool-calls`). Silent under a
`ship` role that judges rather than builds (`SHIP_ROLE` not starting with
`worker`) and when `CLAUDE_EVAL` is set.

### memory_nudge.py (Stop)

Once per session, `<reminder skill="learn">`: on the first Stop after 30
minutes of session time or three Stops, whichever comes first.

### codex_hook.py (Codex adapter)

Normalizes Codex payloads to the Claude shape (`cwd`, `session_id`,
`hook_event`, `prompt`, `tool_name`, `tool_input`, `harness: codex`) and runs
one of `prompt_nudge`, `pretool_nudge`, `stop`. It strips Claude-only `ok`,
promotes `systemMessage` to `additionalContext` for prompt and tool events,
rewrites `/skill` to `@skill` in nudge text, and forwards only `decision:
block` on PreCompact.

## Tests

```bash
make test        # from hooks/; make test-all is the verbose run
```

Runs the Makefile's `TEST_FILES` through `uvx --with pyyaml pytest` when `uvx`
is on PATH, else the first `pytest` on PATH. `conftest.py` holds the in-memory
kvs the tests run against. TEST.md has the manual smoke tests.

See ARCHITECTURE.md for each hook's input, output, flow and state.
