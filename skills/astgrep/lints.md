# Use the bundled rules in a project

`skills/<language>/lints/rules.yml` owns each structural rule. Its message
states the correction; its `note` names the policy owner. Native linters own
checks they already cover. Judgment and exceptions stay in skills and refine.

```text
skill rule → rules.yml → ast-grep scan → project findings
                  ↑          ↑
             make lints   check.py ← project hook or refine
```

Sync ships these packs and `astgrep/check.py` inside `~/.claude/skills/`.
It installs ast-grep separately and leaves project configuration to the project.
The same files serve Claude and the Codex skill bridge.

From a project root, scan explicit files or directories:

```sh
python3 ~/.claude/skills/astgrep/check.py --scan src/
```

The runner uses its bundled packs regardless of the project's `sgconfig.yml`.
It reads files without editing them and respects ast-grep's normal ignores.
Packs cover Python, Rust, TypeScript and `.sh`/`.bash`; TSX needs project checks.
For extensionless Bash, configure ast-grep's `languageGlobs` and widen the hook's `files` filter.
Exit codes: 0 clean, 1 findings, 2 failed check. An empty file list is an error.
The scan needs Python and ast-grep; fixture tests also need PyYAML.

For automatic checks, add this local hook to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: kronael-lints
        name: Kronael structural rules
        language: system
        entry: bash -c 'python3 "$HOME/.claude/skills/astgrep/check.py" --scan "$@"' --
        types: [file]
        files: '\.(py|rs|ts|mts|cts|sh|bash)$'
```

Each machine running this hook needs the bundle and ast-grep installed.
An existing ast-grep project can instead add selected pack directories to
`ruleDirs` and run `ast-grep scan --error <files>`. Use expanded absolute paths;
YAML does not expand `~` or `$HOME`. An unrelated `sgconfig.yml` is not adoption.

## Refine

ALWAYS run the project's adopted checks over existing changed files first.
ALWAYS verify coverage of every applicable bundled rule before skipping fallback
for a file. A passing formatter or native linter alone does not prove this coverage.
For files missing that coverage, ALWAYS run `check.py --scan <files...>`
from the installed path above. Include untracked work in scope; skip an empty
selection and deleted paths. A missing tool is a failed check, NEVER a clean
result. ALWAYS assess findings against project rules; lenses keep the judgments.

## Prove a promotion

ALWAYS add good and bad fixtures under the owning pack's `fixtures/` directory.
Each `<id>.bad.<ext>` blank-line-separated block must match its rule;
`<id>.good.<ext>` must remain clean. `<id>.good.d/` holds path-exemption cases.
ALWAYS bind a new pack in the tools repository's `sgconfig.yml` and name each
rule in its owning skill. `make lints` checks fixture coverage, duplicate IDs,
orphan fixtures and config bindings. ALWAYS inspect real-code matches before
promoting prose; a passing fixture suite alone cannot prove the rule's scope.
