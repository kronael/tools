---
name: recall-memories
description: Look up what a prior session decided, tried, or left open — session transcripts, diary, memory, Codex history. NOT for writing entries (use diary).
when_to_use: "what did we decide, what was the status, why did we choose, where did we discuss, did we already try this, prior session, last session, last time, earlier, find context, recall, no prior context, what did codex say"
user-invocable: true
argument-hint: "<question>"
---

# Recall Memories

Read-only. The session transcripts are the record. Diary and memory are
the curated summary; they drop the reasoning, the commands, the
addresses and the dead ends. A recall that skipped the transcripts is
not a recall.

## 1. Transcripts — ALWAYS first

Slug = absolute CWD with `/` → `-`.

```bash
S=~/.claude/projects/$(pwd | tr / -)
grep -aicH -- '<term>' "$S"/*.jsonl | grep -v ':0$' | sort -t: -k2 -nr | head   # files by hit count
grep -aioU -- '.\{0,200\}<term>.\{0,200\}' "<file>" | head -20                      # context around a hit
```

Search ALL of the project's sessions, not only the current one, then
read the newest 2-3 matching files around the hits (lines are JSON
messages; filter on `role` / `type`). When the topic plausibly spans
projects — a shared tool, a skill, a vague "where did we discuss X" —
ALSO search `~/.claude/projects/*/*.jsonl`, newest first, in the same
pass; NEVER make the user re-ask to widen scope.

## 2. Diary and memory

- Diary: `Glob` `<cwd>/.diary/*.md`; grep `summary:` and the body.
  Cross-project: `~/wk/*/.diary/*.md`.
- Memory: `~/.claude/projects/<slug>/memory/MEMORY.md` and its sibling
  `.md` files. Cross-project: `~/.claude/projects/*/memory/*.md`.

Weighting: "what did we decide" and "what was wrong" → transcripts;
"what is the status" → diary summary.

## 3. Codex history

When `~/.codex` exists or the question names Codex: read `codex.md`
(sibling file) and run its sources — history, session traces, state
index, generated memories.

## 4. Deliberate and report

In `<think>`: per source, what it says; the gaps; the verdict (use it, or
research fresh). ALWAYS verify a finding against the current repo (git
log, file contents) and mark a stale finding — NEVER act on an outdated
decision.

ALWAYS open the answer with the evidence line:
`sessions <files searched>/<files with hits> · diary <hits> · memory <hits>`.
An answer without it did not run this skill. ALWAYS name the originating
project slug for a sibling match, and the `cwd` + trace path for a Codex
match.

Long hit lists: run steps 1-3 in one Explore subagent (read-only; keeps
transcript dumps out of the main context). Its brief lists the sources in
this order and requires the same evidence line.
