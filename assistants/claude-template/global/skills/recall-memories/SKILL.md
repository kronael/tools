---
name: recall-memories
description: Search diary, memory, and session history for relevant information.
user_invocable: true
arg: <question>
---

# Recall Memories

Search project diary, MEMORY.md, and recent session transcripts for
information relevant to a question. Read-only.

## Protocol

### Step 1 — Determine project slug

CWD e.g. `/home/onvos/app/kanipi` → slug `-home-onvos-app-kanipi`
(replace `/` with `-`).

### Step 2 — Search stores

Spawn an Explore subagent with the question to search in parallel:

1. **Diary**: `Glob` `<cwd>/.diary/*.md`, grep `summary:` fields and
   entry text for relevant terms. Read matching files.
2. **Memory**: Read `~/.claude/projects/<slug>/memory/MEMORY.md` and
   any `.md` files in that directory.
3. **Session transcripts**: `Glob` `~/.claude/projects/<slug>/*.jsonl`,
   sort by mtime, read the 2-3 most recent. Each line is a JSON message —
   look for `"role":"assistant"` or `"role":"user"` content matching the query.

### Step 3 — Deliberate

In `<think>`:
1. List matched sources
2. For each: what does it say? Does it answer the question? What gap remains?
3. Verdict: use it, or research fresh

## When to use

- "what did we decide about X?" → search diary + sessions
- "what's the status of Y?" → search diary summary
- "what was wrong with Z?" → search diary + sessions
- Technical question about this project → search diary + memory
