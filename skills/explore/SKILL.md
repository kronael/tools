---
name: explore
description: /explore — read and answer only, no code modifications. NOT for making changes (use improve).
when_to_use: "just answer, don't touch anything, explain this, read only, stop modifying"
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash
---

# /explore — read-only mode

Answer and explore. NEVER modify files.

## Behavior

- Read, grep, Bash for exploration — all fine
- NEVER use Edit, Write, or NotebookEdit
- If a change is needed, describe it instead of making it
