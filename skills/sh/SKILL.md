---
name: sh
description: Bash/shell scripting. NOT for Python utilities (use py) or persistent CLI tools (use cli).
when_to_use: editing .sh files or writing shell scripts
requires: software
---

# Bash Style

Requires the `software` skill's `code.md` for shared naming, style, and design
rules. Below are shell-specific additions.

## Structure
- ALWAYS `set -Eeuo pipefail` at top, NEVER rely on `set -e` alone for pipelines
- ALWAYS `tmp=$(mktemp -d)` + `trap 'rm -rf -- "$tmp"' EXIT` for transient files; NEVER hand-roll `/tmp/script-$$`
- ALWAYS iterate `find` output with `while IFS= read -r -d ''` < <(find ... -print0) or `mapfile -t arr < <(cmd)`; NEVER `for f in $(find ...)` or `for f in $(ls)`
- `do`/`then`/`else` on own line, NEVER after `;` or `&&`
- Functions for repeated logic, plain sequence otherwise

## Variables
- `"${VAR:-default}"` for optional, `"${VAR:?msg}"` for required
- ALWAYS quote: `"$VAR"` not `$VAR`
- Uppercase for env/config, lowercase for locals

## Conditionals
- `[[ ]]` not `[ ]` (bash scripts)
- Booleans: `flag=false` then `if $flag; then` (not string comparison)
- NEVER forget closing `]` when `then` is on next line

## Loops
- ALWAYS `shopt -s globstar` + `**/*.ext` over `find` for simple recursion
- NEVER pipe into `while` when loop body sets variables (subshell loses state)

## Process
- `trap 'cleanup' INT TERM` for graceful shutdown
- `wait` after backgrounding

## Fallback Patterns
```bash
SEED="/preferred/path"
[ -d "$SEED" ] || SEED="fallback/path"
```

## Heredocs
- `cat <<EOF` for multi-line output
- `<<'EOF'` for no expansion

## Anti-patterns
- NEVER inline `; then` or `; do`
- NEVER unquoted variables
- NEVER `sudo` (ask user for privileged ops)
