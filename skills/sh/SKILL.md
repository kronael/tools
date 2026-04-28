---
name: sh
description: Bash/shell scripting. USE when editing .sh files or writing shell scripts. entrypoints, POSIX, bash patterns.
---

# Bash Style

## Structure
- `set -e` at top
- `do`/`then`/`else` on own line, NEVER after `;` or `&&`
- Functions for repeated logic, plain sequence otherwise

## Variables
- `"${VAR:-default}"` for optional, `"${VAR:?msg}"` for required
- ALWAYS quote: `"$VAR"` not `$VAR`
- Uppercase for env/config, lowercase for locals

## Conditionals
- `[ ]` not `[[ ]]` (POSIX portable)
- Booleans: `flag=false` then `if $flag; then` (not string comparison)
- NEVER forget closing `]` when `then` is on next line

## Loops
- Prefer `shopt -s globstar` + `**/*.ext` over `find`
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
