---
name: cli
description: CLI tool patterns. Use when building command-line tools, argument parsing, process control.
---

# CLI Style

## Arguments

**ALWAYS short flags for common operations**:
- -c not --config, -v not --verbose, -h not --help
- Old Unix style: terse, composable

**Multiple values**:
- Repeat flag: `-e ex1 -e ex2` or comma: `--hosts=h1,h2`

**Positional args**:
- Required: `<identity>`, Optional: `[branch]`

## Config Precedence

**Three-level hierarchy** (highest precedence first):
1. CLI flags (-e exchange)
2. Environment variables (EXCHANGE=, PREFIX=)
3. Configuration files (config.toml)
4. Defaults (hardcoded)

**ALWAYS fail fast with clear error on invalid config**

## Interactive vs Non-interactive

**ALWAYS support both modes**:
- Interactive: prompt for passwords, confirmations
- Non-interactive: `--yes` flag skips all prompts (for automation/CI)

Example:
```bash
# Interactive (prompts for password)
tool create --username alice

# Non-interactive (batch automation)
tool create --username alice --password "secret" --yes
```

## Exit Codes

**ALWAYS use semantic exit codes**:
- 0: Success
- 1: Configuration/argument error
- 2: Runtime error (retryable)
- 3: Fatal error (don't retry)
- 130: Interrupted (Ctrl+C)

## Output

**ALWAYS separate stdout from stderr**:
- stdout: Normal output (results, progress)
- stderr: Errors, warnings

**Default: human-readable**:
- --json for machine parsing
- --quiet for scripts (errors only)

**Error messages MUST be actionable**:
```
Error: Invalid configuration - expected http/https URL for rpc_url
  Got: "ftp://invalid"
  Fix: Use https:// instead
```

## Help Format

**ALWAYS include usage, commands, options, examples**:
```
Usage: tool [OPTIONS] [COMMAND]

Commands:
  start    Start the service
  stop     Stop the service
  help     Show this help

Options:
  -c, --config FILE     Configuration file
  -e, --exchange NAME   Filter by exchange
  -v, --verbose         Enable verbose logging
  -h, --help            Show this help

Examples:
  # Interactive (prompts for password)
  $ tool create --username alice --sku WIN-2022

  # Non-interactive (batch automation)
  $ tool create --username alice --password secret --yes
```

## Installation

**ALWAYS provide two methods**:

**Pattern 1: Development** (make link):
```makefile
link:
	ln -sf $(PWD)/target/debug/tool ~/bin/tool
```

**Pattern 2: System** (make install):
```makefile
install:
	install -m 755 target/release/tool /usr/local/bin/tool
```

**Verification**:
```bash
tool --help
```

## Configuration Validation

**ALWAYS validate on load, BEFORE any operations**:
- URL format checking (http/https, ws/wss)
- Non-zero amounts required
- Price bounds (0 < price ≤ 1)
- File path existence checks
- Required fields present

**Validation failure = exit code 1**

## Testing CLI

**Fixture data in cfg/test/**:
```bash
# Test with fixture config
./target/debug/main cfg/test/config.toml

# Test with env overrides
RUST_LOG=debug ./main cfg/test/config.toml

# Test dry-run mode
./main cfg/test/config.toml --dry-run
```

**NEVER use production configs in tests**
**ALWAYS use temporary directories for test outputs**

## Pitfalls

- NEVER assume file existence (validate first)
- NEVER write secrets to logs
- NEVER hardcode paths (use ${PREFIX})
- ALWAYS provide dry-run mode for destructive operations
- ALWAYS document environment variables in --help
