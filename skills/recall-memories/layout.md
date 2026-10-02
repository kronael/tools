# Claude Code session records on disk

Read from real files on a Claude Code 2.1 host and the `.claude` directory
docs (code.claude.com/docs/en/claude-directory). `recall.py` reads all of
this; use the raw paths below only when the helper cannot answer.

## Where things live

| Path | Holds |
|------|-------|
| `~/.claude/projects/<slug>/<session>.jsonl` | main transcript: every message, tool call and tool result |
| `~/.claude/projects/<slug>/<session>/subagents/agent-<id>.jsonl` | one subagent's transcript, nested agents included |
| `…/subagents/agent-<id>.meta.json` | `agentType`, `description`, `toolUseId`, `worktreePath`, `parentAgentId`, `spawnDepth` |
| `~/.claude/projects/<slug>/<session>/tool-results/<name>.txt` | full output of a call too large for the transcript; `<name>` is a `b…` id or the `toolu_…` id |
| `~/.claude/projects/<slug>/<session>.jsonl.superseded-<ts>` | an earlier copy of a transcript, set aside instead of overwritten (not read by the helper) |
| `~/.claude/projects/<slug>/memory/` | `MEMORY.md` index plus one file per memory |
| `~/.claude/history.jsonl` | every typed prompt: `display`, `project`, `sessionId`, `timestamp` (ms); never swept |
| `/tmp/claude-$(id -u)/<slug>/<session>/tasks/<id>.output` | background output; an agent's is a symlink to its subagent transcript, a shell command's is a plain file that a reboot deletes |
| `<cwd>/.diary/YYYYMMDD.md` | the diary; `summary:` block in the frontmatter |

- Slug = the launch directory with EVERY non-alphanumeric character
  replaced by `-`: `/home/u/app/x/.wt/server` → `-home-u-app-x--wt-server`.
  A worktree or subdirectory launch gets its own slug, and a session
  launched elsewhere that `cd`s into the repo stays under the launch slug.
  Scope by the records' `cwd`, as the helper does, not by slug alone.
- Transcripts, subagents and tool-results older than `cleanupPeriodDays`
  (settings.json, default 30 days) are deleted; `history.jsonl` is not.

## Records in a transcript

One JSON object per line. A line can be malformed where two writers
interleaved — skip it, never stop on it.

| `type` | Use for recall |
|--------|----------------|
| `user`, string content | a typed prompt; `origin.kind` is `human`, `task-notification`, … |
| `user` with `isCompactSummary: true` | the compaction summary: request, decisions, pending work |
| `user` with `isMeta: true` | hook feedback and caveats, not the user |
| `attachment`, `attachment.type: queued_command`, `commandMode: prompt` | a prompt the user sent while a turn ran (`prompt`, `origin.kind: human`); most mid-turn prompts exist only in this form |
| `attachment`, `queued_command`, `commandMode: task-notification` | a completion notice queued during a turn; `prompt` holds the `<task-notification>` block |
| `user`, `tool_result` blocks | `tool_use_id`, `content`, `is_error`; sibling `toolUseResult` has `stdout`, `stderr`, `interrupted`, `backgroundTaskId`, `agentId`, `status`, `bashEditDiff` |
| `assistant` | `text`, `thinking`, `tool_use` blocks (`id`, `name`, `input`) |
| `system`, `subtype: away_summary` | the recap: goal, state, next action |
| `custom-title`, `ai-title`, `agent-name` | session titles (`customTitle`, `aiTitle`) |
| `last-prompt` | `lastPrompt` of the session |
| `pr-link` | `prNumber`, `prUrl`, `prRepository` |
| `continued-in` | `continuedInSessionId`: the session that picked this one up |
| `queue-operation` | queue bookkeeping (`enqueue`, `dequeue`, `remove`); an `enqueue` `content` usually lands again as an `attachment` or `user` record, but a notice queued as the session ended survives only here |

Every message record carries `cwd`, `gitBranch`, `sessionId`, `timestamp`.

- A large output reaches the transcript only as a preview:
  `<persisted-output>\nOutput too large (178.2KB). Full output saved to:
  <path>` — read the file at `<path>` for the rest.
- An async agent's tool result is only "Async agent launched"; its report
  arrives later in a `<task-notification>` block with `<task-id>`,
  `<status>` (`completed`, `failed`, `killed`, `stopped`), `<summary>` and,
  for agents, `<result>`. `<tool-use-id>` is often missing: match on
  `<task-id>` against the call's `toolUseResult.agentId` or
  `backgroundTaskId`. The block comes as a `user` record with
  `origin.kind: task-notification`, inside a subagent prefixed by
  `[SYSTEM NOTIFICATION - NOT USER INPUT]`, or as a `queued_command`
  attachment. The same task can notify more than once; the last wins. A
  background command started inside a subagent reports to the parent's
  main transcript, so match notices across the session's files.
- A background shell's notification carries the exit code in `<summary>`;
  its output lives only in the `/tmp` file and in whatever later call read
  that file.
- A forked or resumed session copies earlier records into its new
  transcript, so one `tool_use` id can appear in several files.

## Raw fallback

In Claude Code's shell `grep` is ugrep and `rg` is the bundled ripgrep. A
relative path that starts with `-home-…` parses as an option, so ALWAYS
pass absolute paths or put `--` before them, and ALWAYS give `-a` so a
stray binary byte does not hide a file.

```bash
S=~/.claude/projects/$(pwd | sed 's/[^a-zA-Z0-9]/-/g')
grep -aicH -- '<term>' "$S"/*.jsonl "$S"/*/subagents/*.jsonl | grep -v ':0$' | sort -t: -k2 -nr | head
grep -ail -- '<term>' "$S"/*/tool-results/*
grep -ai -- '<term>' ~/.claude/history.jsonl | tail -20
```

Read a hit with `python3 $R show <toolu_id>` or `digest <session>`, not by
slicing the JSON line by hand.
