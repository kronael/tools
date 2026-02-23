---
name: bash
description: Bash/shell scripting patterns. Use when writing .sh files, entrypoints, shell scripts.
---

# Bash Style

## Structure
- `set -e` at top (fail fast)
- `do`/`then`/`else` on own line, never after `;` or `&&`
- Functions for repeated logic, plain sequence otherwise
- No complex path resolution: no `basename $0`, no `dirname`
- Implicit relative paths (`cfg/` not `./cfg/`)

## Variables
- `"${VAR:-default}"` for optional vars with defaults
- `"${VAR:?msg}"` for required vars
- Always quote variables: `"$VAR"` not `$VAR`
- Uppercase for env/config, lowercase for locals

## Conditionals
```bash
if [ -f "$path" ]
then
  ...
fi
```
- `[ ]` not `[[ ]]` (POSIX portable)
- `-z`/`-n` for string tests, `-f`/`-d` for file tests
- NEVER forget closing `]` when `then` is on next line

## Loops
```bash
for f in *.txt
do
  ...
done
```

## Process
- Kill by PID, never `killall` or `pkill -f`
- PID files in `tmp/` for dev
- `trap 'cleanup' INT TERM` for graceful shutdown
- `wait` after backgrounding

## Fallback Patterns
```bash
# try preferred, fall back to alternative
SEED="/preferred/path"
[ -d "$SEED" ] || SEED="fallback/path"
```

## Heredocs
- Use for multi-line output: `cat <<EOF`
- Quote delimiter for no expansion: `<<'EOF'`

## Anti-patterns
- NEVER `./` prefix on relative paths (implicit)
- NEVER `basename $0` or `dirname` tricks
- NEVER inline `; then` or `; do`
- NEVER unquoted variables
- NEVER `sudo` (ask user for privileged ops)
- NEVER `/tmp` (use project `tmp/`)
