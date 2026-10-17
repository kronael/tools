# Subtraction pass — the procedure

How to measure a rule for `SKILL.md` § The subtraction test, which owns the
verdict criteria. Run it over one rule before writing or trimming it, and over
the whole bundle after a large consolidation or when the owner says the rules
are too many or not upheld.

## The clean room

A clean room loads nothing of the owner's setup: no CLAUDE.md, no skill of any
kind, no tools, no settings, no memory. Anything less lets the model read or
paraphrase the rules under audit, and the test measures the bundle, not the
model.

- ALWAYS run every prompt through `clean-room.sh <model-id> <prompt-file>` in
  this directory, one fresh room per run. NEVER measure with an `Agent(...)`
  sub: it is handed `~/.claude/CLAUDE.md` and every applicable project
  `CLAUDE.md` before its first token, so "do not read any files" removes
  nothing and it paraphrases the rule back as its own. The tell is
  specificity: a clean model gives the field default, a contaminated one
  returns this repo's exact paths, counts and separators.
- NEVER drop a flag from the script's `claude` line: without
  `--disable-slash-commands` the run lists Claude Code's built-in skills, and
  without `--safe-mode` it loads a CLAUDE.md from its working directory.
- ALWAYS export `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` first — the
  room's fresh `HOME` puts OAuth and the keychain out of reach. Read the
  owner's token from their shell rc into the variable; NEVER print it.
- ALWAYS pass a full model ID (`claude-opus-5-5`). An empty config falls back
  to another model, and `claude` answers an alias or an unknown name from
  whatever it resolves, which turns a two-model verdict into one model run
  twice without failing.
- ALWAYS trust a run only on its transcript, never on the model's report of
  what it saw. After every run the script reads the transcripts under the
  room's `CLAUDE_CONFIG_DIR` and exits non-zero unless they hold no
  `skill_listing`, `instructions` (a loaded CLAUDE.md) or `nested_memory`
  attachment, zero `tool_use` blocks, and the pinned model in every assistant
  record; `clean-room.sh check <model-id> <room>` re-runs the check.
- ALWAYS also send a probe through the same set-up, one this repo answers
  unusually — "where do you put git worktrees, how do you name a new branch,
  what line width do you code to" — and discard the whole run when
  repo-specific detail comes back instead of the field default.
- Rooms stay under `/var/tmp`; keep answers beside them as
  `<room>/<topic>-<n>.md`, scratch, not the record.

## Prompts

- ALWAYS write each prompt to a file and pass its path — NEVER inline it in a
  `-p "…"` argument: bash runs a backticked word inside double quotes as a
  command, `[NEEDS TELLING]` included.
- ALWAYS name the DOMAIN only ("error handling", "code comments") and let the
  model decide what belongs in it. NEVER list sub-topics taken from our
  headings: a "cover X, Y, Z" line is our table of contents, a model
  completing it proves only that it can write to a spec, and the finding — a
  rule it never thought to mention — can no longer show. NEVER quote or
  paraphrase our text, and NEVER ask for a critique of ours. Before sending,
  read the prompt back and strike any phrase you could locate in the file
  being measured.
- Two questions, each in a fresh room:
  1. Knowledge, once per domain: "Write the rules you follow by default when
     <domain>, from your own judgment. Mark each rule you know you drift on
     `[NEEDS TELLING]` with a one-clause why."
  2. Behaviour, once per candidate rule — each rule question 1 reproduced and
     did not mark: "Describe how you actually behave when <the task the rule
     governs> with no instructions: your real defaults, the wrong ones
     included." Name the task, never the rule.
- ALWAYS ask both questions of two models — one agreeing is a signal, two is a
  verdict.

## Order — highest cost per rule first

1. `skills/global/SKILL.md` — loaded in every session.
2. `skills/software/code.md` and the language skills (`rs`, `py`, `go`, `ts`,
   `tsx`, `sh`, `sql`) — loaded on every code edit.
3. Domain skills (`ops`, `cli`, `data`, `service`, `solana`, `htmx`, …).
4. Workflow skills last (`commit`, `ship`, `refine`, `release`, `merge`,
   `kronael/sync`): a workflow survives by definition; test only their
   free-standing prose rules.

One domain per run, at most 4 runs in parallel. A domain is what one section
or one skill governs — never a whole file of mixed concerns.

## Findings

- One verdict table per file: rule, question 1 and question 2 per model,
  behavioural evidence, verdict. ALWAYS record the tables as the diary
  companion `YYYYMMDD-subtraction.md` (`diary` § Named companions), referenced from that day's log —
  the next pass starts from it.
- ALWAYS file a proposed cut to an always-loaded file (`global`, `code.md`) in
  `BUGS.md` as a proposal naming which model produced what, and wait for the
  owner's sign-off — NEVER cut one on sight, it changes every future session.
  A cold file follows its table directly.
- One commit per file or skill family; `make skills-frontmatter` exits 0;
  sync live (`kronael/sync`).
