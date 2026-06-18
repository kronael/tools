---
name: recall-memories
description: Search diary, memory, and session history. NOT for writing entries (use diary).
when_to_use: "what did we decide, recall, find context from a prior session"
user-invocable: true
arg: <question>
---

# Recall Memories

Read-only search across project diary, MEMORY.md, and session transcripts.

## Protocol

### Step 1 — Slug

Slug = absolute CWD with `/` → `-`. Current-project slug is primary;
other slugs under `~/.claude/projects/` are siblings.

### Step 2 — Search (spawn Explore subagent, parallel)

ALWAYS search the current project. ALWAYS ALSO search siblings in the
same pass when the topic plausibly spans projects (cross-cutting tool,
shared skill, vague "where did we discuss X") — NEVER make the user
re-ask to widen scope.

1. **Diary** — `Glob` `<cwd>/.diary/*.md`. Cross-project: ALSO `Glob`
   `~/wk/*/.diary/*.md`. Grep `summary:` and body.
2. **Memory** — Read `~/.claude/projects/<slug>/memory/MEMORY.md` and
   sibling `.md` files. Cross-project: ALSO `Glob`
   `~/.claude/projects/*/memory/*.md`.
3. **Sessions** — `Glob` `~/.claude/projects/<slug>/*.jsonl`, sort by
   mtime, read 2-3 newest. Cross-project: ALSO `Glob`
   `~/.claude/projects/*/*.jsonl`, sort by mtime, grep the newest
   handful. Lines are JSON messages; filter on `role` and content.

ALWAYS name the originating project slug when reporting sibling matches.

### Step 3 — Deliberate

In `<think>`: list sources, state what each says, identify gaps, verdict
(use or research fresh).

ALWAYS verify matches against current repo state (git log, file
contents). ALWAYS mark stale findings explicitly — NEVER act on
outdated decisions.

## Triggers

- "what did we decide about X?" — diary + sessions
- "what's the status of Y?" — diary summary
- "what was wrong with Z?" — diary + sessions
- Technical question about this project — diary + memory
