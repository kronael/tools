# Bundle subtraction pass

Runs `SKILL.md` § The subtraction test over the whole bundle: every rule a
blank model already writes AND follows goes; drifts, local facts, workflows and
harness overrides stay. Run it after a large consolidation, or when the owner
says the rules are too many or not upheld.

## The clean room

- ALWAYS measure with a model that loads none of the bundle:
  `claude --safe-mode -p "<prompt>"` starts with no CLAUDE.md, skills, plugins,
  hooks or output style. NEVER use an `Agent(...)` sub as the clean room — it
  inherits `~/.claude/CLAUDE.md` and the skill listing and paraphrases the
  rules under audit.
- ALWAYS run it from a scratch dir outside every repo
  (`cd "$(mktemp -d -p /var/tmp)"`), so no project CLAUDE.md loads.
- The run needs the owner's login: `CLAUDE_CODE_OAUTH_TOKEN` in its env. A
  tool shell strips it; load only that export line from the owner's shell rc,
  and NEVER print it.
- Two prompts per topic, each a fresh run:
  1. "Write the rules you follow by default when <topic>. Mark each rule you
     know you drift on `[NEEDS TELLING]` with a one-clause why."
  2. "Describe how you actually behave when <task> with no instructions: your
     real defaults, the wrong ones included."
- Keep both answers in the run dir (`/var/tmp/subtraction-<date>/<topic>.md`);
  they are scratch, not the record.

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
