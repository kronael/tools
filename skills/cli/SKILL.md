---
name: cli
description: CLI tools. NOT for one-off scripts (use sh).
when_to_use: "writing a CLI tool, argparse/click/clap, adding --help or subcommands, service instance defaults, --instance"
---

# CLI Style

ALWAYS Read `../software/code.md` before the first edit — it owns naming,
comments, design and the boring-code rules.

## Arguments

- ALWAYS use short flags for common options, with long aliases: `-c/--config`, `-v/--verbose`, `-h/--help`.
- Repeat flag for multiples: `-e ex1 -e ex2` or comma: `--hosts=h1,h2`
- Positional: required `<identity>`, optional `[branch]`
- ALWAYS default to one service instance; select another with `-i/--instance`, never a required positional argument.

## Config Precedence

CLI flags > env vars > config files > defaults. Fail fast on invalid config.
The config file and API-keys positions: `software/code.md` § House conventions.

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

## Performance

- NEVER import heavy deps at top of entrypoint for an interactive CLI — lazy-import inside the subcommand. Measure with `hyperfine '<tool> --help'`.

## Pitfalls

- NEVER write secrets to logs
- NEVER hardcode paths (use ${PREFIX}); a user program's state, settings, cache and
  data live under the XDG dirs (`software/code.md` § House conventions), `/srv/data` is for services
- ALWAYS document env vars in --help
- ALWAYS validate config on load, BEFORE any operations
- Fixture data in cfg/test/, NEVER use production configs in tests
