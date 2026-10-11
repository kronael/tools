# spec-lint

Lint a `specs/` corpus against the `specs` skill's format rules
(`skills/specs/format.md`): numbering, the closed status vocabulary, index
rows, links, wording and code pointers. One file, stdlib only, Python 3.9+.

```sh
spec-lint                 # the specs/ dir under the current directory
spec-lint specs           # the same, named
spec-lint path/to/project # discover every specs/ corpus below a dir
spec-lint specs/03-x.md   # the corpus a changed file belongs to
spec-lint -v specs        # name each corpus checked
spec-lint --help          # every rule with its severity
```

A directory passed by name is checked as it is. A spec file or a project
directory is searched for corpora: a dir named `specs` holding an `index.md`
or a numbered spec file, so a test suite named `specs` or the skill's own
`skills/specs/` is left alone. Generated dirs (`node_modules`, `.venv`,
`dist`, ...) and nested checkouts (a dir with its own `.git`) are skipped.

## Rules

Errors fail the run; warnings print. A rule names itself in each finding and
points back at `format.md`, so a failure teaches.

| Rule | Severity | Fires on |
|------|----------|----------|
| `spec-naming` | error | a name that is not `<NN>-<topic>.md` or `<phase>/<N>-<topic>.md`, a third directory level, two files sharing a number; warn: a flat number without zero-padding |
| `spec-status` | error | a frontmatter `status` outside `draft experiment planned partial shipped reference`, or an index Status cell that differs from the file |
| `spec-index-row` | error | a spec with no row in `specs/index.md` or in a `<phase>/index.md` the root index links |
| `spec-index-dangling` | error | an index link to a file that does not exist |
| `spec-link` | error | a spec link to a file that does not exist |
| `spec-table-owner` | error | `CREATE TABLE <name>` declared in two specs |
| `spec-length` | error over 1000 lines, warn over 500 | a spec that is prose where tables with `file:line` anchors belong |
| `spec-tbd` | error | `TBD`, `TODO`, `implement later` |
| `spec-future-tense` | warn | `we will`, `we'll`, `will be` |
| `spec-history` | warn | `no longer`, `formerly`, `renamed from`, `used to be`, `as before`, backward compatibility |
| `spec-wording` | warn | `harness`; marketing words (`powerful`, `seamless`, `robust`, ...) |
| `spec-options` | warn | a heading that lays out options or alternatives |
| `spec-open-questions` | warn | an open-questions heading in a spec that is not `draft` or `reference` |
| `spec-checklist` | warn | a task-list item (`- [ ]`, `- [x]`) |
| `spec-pointer` | warn | a backticked `path` or `path:line` that resolves nowhere, matches several files, or points past the end of its file |
| `spec-no-pointer` | warn | a `partial` or `shipped` spec that names no file |

Fenced code is never prose: nothing inside a fence counts for the prose
rules, and `CREATE TABLE` counts only inside one.

### Code pointers

A pointer is a backticked `path:line` or a backticked path with a slash.
It resolves from the spec's own directory, the corpus, the component (the
directory holding `specs/`) and every ancestor up to the repository root
(the nearest `.git`, a directory or a worktree's file). Failing that, it
resolves by its trailing path segments anywhere in the repository — a bare
`loader.py:12` resolves when exactly one file has that name, and the
component's own file wins over a sibling component's copy. Several matches
warn as ambiguous; name the path from the repository root. A bare
`config.yaml` without a line number is prose, not a pointer.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | no errors; warnings may have printed |
| 1 | at least one error |
| 2 | a path does not exist, or the arguments are wrong |

Findings and the summary line go to stdout; `no such file` and `no spec
corpus under ...` notes go to stderr.

## Install

```sh
cd spec-lint && make install    # ~/.local/bin/spec-lint (PREFIX overrides)
make test                       # pytest
```

The kronael sync (`kronael/sync/SKILL.md` step 8) installs it with the other
CLI tools. As a pre-commit hook in any repository:

```yaml
- repo: local
  hooks:
    - id: spec-lint
      name: lint specs/
      entry: spec-lint
      language: system
      files: (^|/)specs/.*\.md$
```
