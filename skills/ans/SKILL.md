---
name: ans
description: /ans — conversational answer-only mode toggle. NEVER edit files or run shell. /ans end to exit. NOT for stopping mid-task to ask (just answer inline).
when_to_use: "just answer, don't change anything, explain only, read-only mode, no edits, answer from context, stop touching files"
user-invocable: true
---

# /ans — answer-only mode

Toggle. `/ans` enters, `/ans end` exits.

Announce in one line: `Answer-only mode ON.` / `Answer-only mode OFF.`

## Behavior

ALLOW Edit/Write for diary and auxiliary docs only: `.diary/*.md`, `MEMORY.md`, `BUGS.md`, `TODO.md`, `*.md` specs/architecture/readme/changelog.
NEVER use Edit/Write for code files (`.py`, `.ts`, `.js`, `.go`, `.rs`, `.toml`, `.yaml`, `.json`, etc.); NEVER use NotebookEdit, Bash, TaskCreate, TaskUpdate.

ALWAYS use Read, Glob, Grep, WebFetch, WebSearch freely.

ALWAYS allow Agent — read-only research only; instruct subagents not to write files or run code.

ALWAYS ground answers in the context where `/ans` was invoked — the current file, topic, or recent diff. NEVER wander into unrelated areas unless explicitly asked.

Prefer reading nearby files over broad searches.
