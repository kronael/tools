---
name: cli
description: CLI tools. argparse, click, clap, --help, exit codes, signal handling, SIGTERM, SIGINT, config precedence, interactive prompts.
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

## Pitfalls

- NEVER write secrets to logs
- NEVER hardcode paths (use ${PREFIX})
- ALWAYS document env vars in --help
- ALWAYS validate config on load, BEFORE any operations
- Fixture data in cfg/test/, NEVER use production configs in tests
