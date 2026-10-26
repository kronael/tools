# speclint

Check a specification corpus for naming, status, index agreement and code pointers. Python 3.13+,
with no runtime dependencies. [Spec conventions](../skills/specs/format.md) own the lifecycle; tests
and review establish implementation completion. Rumdl owns Markdown syntax, formatting and supported
file links and heading anchors.

## Run

```sh
speclint                 # check specs/ under the current directory
speclint specs           # check the complete named corpus
speclint path/to/project # discover all corpora in a project
speclint specs/03-api.md # check the file's complete corpus
speclint -v .            # print each discovered corpus
speclint --help          # rules and exit codes
```

An explicitly named directory called `specs` is checked even when empty or malformed. Project
discovery finds directories called `specs` with an index or numbered Markdown file at any depth. An
unrelated test directory or skill called `specs` has no such marker and is excluded. Generated
directories and nested Git checkouts are excluded. Unreadable directories and invalid UTF-8 fail
visibly. A project with no corpora passes; a missing explicit path fails.

## Rules

Errors fail the run. Warnings report uncertain code references without blocking the commit.

| Rule | Severity | Checks |
|---|---|---|
| `spec-naming` | error; padding warns | `<NN>-<topic>.md` or `<phase>/<N>-<topic>.md`; unique numbers within each directory; at most one phase level |
| `spec-status` | error | Required status header, closed vocabulary, and index Status agreement |
| `spec-index-row` | error | Exactly one row per spec in the root index or a phase index linked from it |
| `spec-index-dangling` | error | Index links to absent Markdown files within the corpus, including deleted specs and phase indexes |
| `spec-pointer` | warning | Unresolved or ambiguous code references, invalid line ranges |

Each spec starts with `---`, one `status: value` line, and `---`, each on its own line. Values are
`draft`, `experiment`, `planned`, `partial`, `shipped`, and `reference`. Single or double quotes
around the value, blank lines, full-line comments and trailing status comments are accepted. This is
a restricted YAML header: extra keys, duplicate statuses and other YAML forms fail. UTF-8 with a
byte-order mark and CRLF input are accepted.

Indexes use `| Spec | Status | Summary |` columns in that order, with optional additional columns.
Each spec row has one inline Markdown link in the first cell, the exact status in the second, and a
summary in the third. A prose link or summary-cell link does not register a spec. The root index can
link `<phase>/index.md` to include that phase's rows. Index links may use relative or
repository-root paths, URL encoding, titles and heading fragments. Rumdl validates fragments and
general Markdown links; speclint interprets index links to establish membership and status
agreement.

`CLAUDE.md` and `AGENTS.md` are directory instructions, not specs. Empty corpora pass, including an
empty index. Retirement deletes the spec and its index row together. Lint never decides whether a
spec is implemented. Prose, SQL examples, length and the absence of code pointers do not determine
status or completion.

### Code pointers

A pointer is a backticked path containing a slash, optionally with a line range (`src/app.py:12-30`,
`server/Makefile`), or a bare filename with an extension and line (`loader.py:12`). Bare names
without a line, host/port pairs and trailing-slash directories are excluded. Tokens containing
spaces, URLs, `..`, wildcard or shell syntax are excluded. A leading slash, tilde, hyphen, hash, at
sign or colon is excluded. A path segment starting with `YYYYMMDD` or `NN` is a placeholder.

Pointers resolve from the spec's directory, corpus, component and ancestors through the nearest Git
repository root. A unique matching trailing path in that repository also resolves; the component's
file wins over a sibling's copy. Ambiguity warns. Fenced code is excluded. Pointer warnings do not
verify a requirement or infer implementation status.

## Install and pre-commit

Local installation uses `cd speclint && make install` from a tools clone. Kronael sync uses this
target. Direct execution with [uvx](https://docs.astral.sh/uv/guides/tools/) needs no installed
bundle. Set `SPECLINT_COMMIT` to the full 40-character commit of a published tools revision
containing this package:

```sh
uvx --from "git+https://github.com/kronael/tools.git@${SPECLINT_COMMIT}#subdirectory=speclint" speclint .
```

In a consumer's `.pre-commit-config.yaml`, replace `FULL_COMMIT_HASH` with that full published
commit:

```yaml
repos:
  - repo: local
    hooks:
      - id: speclint
        name: lint specification corpora
        entry: uvx --from 'git+https://github.com/kronael/tools.git@FULL_COMMIT_HASH#subdirectory=speclint' speclint .
        language: system
        pass_filenames: false
        always_run: true
```

Install the consumer hook with `pre-commit install`. `always_run` activates it even on deletion-only
commits; `pass_filenames: false` keeps the complete corpora in scope. Scanning the project also
permits retirement of its last corpus. Use explicit corpus paths for unnumbered drafts that
discovery cannot identify. Ignored or externally stored specs need explicit local checks; CI sees
only its checkout. Missing uvx, failed installation and malformed inputs return nonzero. See
[pre-commit hook options](https://pre-commit.com/#new-hooks).

Use a separate rumdl pre-commit hook with the complete relevant Markdown scope, including unchanged
targets. Enable and verify MD057 for file targets and MD051 for heading fragments. Cross-file
fragments require the referenced Markdown in scope. Consumer lint does not need a Makefile target or
repository checker script.

## Development

| Command | Purpose |
|---|---|
| `make prepare` | Install locked development dependencies |
| `make test` | Run rule fixtures with Python development checks |
| `make integration` | Build and inspect a wheel; run uvx and real Git hooks in temporary consumers |
| `make check` | Ruff lint and format checks |
| `make right` | Strict type checks |
| `make build` | Build source and wheel distributions |
| `make install` | Install the command with uv |
| `make clean` | Delete bytecode and distribution files |

Fixtures use invented examples. Integration tests require uv and Git on PATH. They create consumers
outside the source checkout and install hooks there. Local installation tests do not establish that
a remote commit is published or executable.

Exit codes: `0` means no errors, `1` means rule errors, and `2` means invalid arguments, paths or
unreadable input. Findings and counts go to stdout; input errors and empty-discovery notes go to
stderr.
