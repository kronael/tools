# Bundle subtraction pass

Runs `SKILL.md` § The subtraction test over the whole bundle: every rule a
blank model already writes AND follows goes; drifts, local facts, workflows and
harness overrides stay. Run it after a large consolidation, or when the owner
says the rules are too many or not upheld.

## The clean room

A clean room loads nothing of the owner's setup: no CLAUDE.md, no skill of any
kind, no tools, no settings, no memory. Anything less lets the model read or
paraphrase the rules under audit, and the test measures the bundle, not the
model.

- NEVER use an `Agent(...)` sub: it inherits `~/.claude/CLAUDE.md` and the
  skill listing, and its tools can Read the skills.
- NEVER rely on `--safe-mode` alone: it still lists Claude Code's built-in
  skills, keeps tools, reads the real home and runs its default model.
- ALWAYS run every prompt like this, with a fresh root per pass:

  ```sh
  R=$(mktemp -d -p /var/tmp cleanroom-XXXX); mkdir -p "$R/home" "$R/cwd"
  cd "$R/cwd" && env -i HOME="$R/home" CLAUDE_CONFIG_DIR="$R/home/.claude" \
    PATH="/usr/bin:/bin:$(dirname "$(command -v claude)")" \
    CLAUDE_CODE_OAUTH_TOKEN="$tok" \
    claude --model <the model sessions use> --safe-mode \
      --disable-slash-commands --tools "" -p "<prompt>"
  ```

  `$tok` is the owner's login, read from their shell rc into a variable;
  NEVER print it. Pin the model: an empty config falls back to another one.
- ALWAYS prove the isolation from the run's own transcript, never from its
  self-report: under `$R/home/.claude/projects/` no `skill_listing`,
  `claudeMd` or `nested_memory` attachment, zero `tool_use` blocks, and the
  pinned model in every assistant record.
- Two prompts per topic, each a fresh run:
  1. "Write the rules you follow by default when <topic>. Mark each rule you
     know you drift on `[NEEDS TELLING]` with a one-clause why."
  2. "Describe how you actually behave when <task> with no instructions: your
     real defaults, the wrong ones included."
- Keep both answers in `$R/<topic>-<n>.md`; they are scratch, not the record.

## Order — highest cost per rule first

1. `skills/global/SKILL.md` — loaded in every session.
2. `skills/software/code.md` and the language skills (`rs`, `py`, `go`, `ts`,
   `tsx`, `sh`, `sql`) — loaded on every code edit.
3. Domain skills (`ops`, `cli`, `data`, `service`, `solana`, `htmx`, …).
4. Workflow skills last (`commit`, `ship`, `refine`, `release`, `merge`,
   `kronael/sync`): a workflow survives by definition; test only their
   free-standing prose rules.

One topic per run, at most 4 runs in parallel. A topic is one section or one
skill — never a whole file of mixed concerns.

## Verdict per rule

Build one table per file: rule, reproduced by prompt 1, followed by default per
prompt 2, verdict.

- Reproduced and followed → CUT.
- Reproduced but confessed broken in prompt 2 → KEEP, rewritten as the
  ALWAYS/NEVER that names the trap.
- Contradicted or absent → KEEP; overriding a prior is guidance's best use.
- Local fact, workflow, or deliberate harness override → KEEP; label an
  override in place so a later pass does not cut it.
- Real engineering content that is not always needed → MOVE to the cold file
  that owns it; NEVER delete it.

Then cut every survivor the system prompt or the active output style already
states.

## Apply

- ALWAYS show the owner the table for a hot file (`global`, `code.md`) and
  wait for sign-off before cutting; cold files follow the table directly.
- One commit per file or skill family; `make skills-frontmatter` exits 0;
  sync live (`kronael/sync`).
- Record the tables as a diary companion, `.diary/YYYYMMDD-subtraction.md`,
  referenced from that day's log — the next pass starts from it.
