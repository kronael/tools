---
name: cli
description: CLI tools. NOT for one-off scripts (use sh).
when_to_use: writing a CLI tool, argparse/click/clap, adding --help or subcommands
---

# CLI Style

## Arguments

- ALWAYS short flags for common ops: -c, -v, -h (old Unix style)
- Repeat flag for multiples: `-e ex1 -e ex2` or comma: `--hosts=h1,h2`
- Positional: required `<identity>`, optional `[branch]`

## Config Precedence

CLI flags > env vars > config files > defaults. Fail fast on invalid config.

## Exit Codes

- 0: success, 1: config error, 2: runtime error (retryable), 3: fatal, 130: interrupted

## Output

- stdout: results, stderr: errors
- --json for machine parsing, --quiet for scripts
- Error messages MUST be actionable (show got + fix)

## Modes

- ALWAYS support --yes for non-interactive (CI/automation)
- ALWAYS provide --dry-run for destructive operations

## Installation

Two methods: `make link` (dev, symlink debug binary) and `make install` (system, install release binary).

## Completions

- ALWAYS ship completions for bash + zsh (fish if framework supports). argparse: argcomplete; click: `_<APP>_COMPLETE`; clap: `clap_complete`. Expose `<tool> completions <shell>` subcommand.

## Performance

- ALWAYS keep cold-start < 100ms. NEVER import heavy deps at top of entrypoint — lazy-import inside the subcommand. Measure with `hyperfine '<tool> --help'`.

## Pitfalls

- NEVER write secrets to logs
- NEVER hardcode paths (use ${PREFIX})
- ALWAYS document env vars in --help
- ALWAYS validate config on load, BEFORE any operations
- Fixture data in cfg/test/, NEVER use production configs in tests
