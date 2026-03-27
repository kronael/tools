---
name: recall
description: Read, retrieve, or extract context from past sessions. Trigger on "recall", "last session", "what did we work on", "remember", "extract from history", "what was decided", "past context", or any reference to prior conversations.
user-invocable: true
---

Launch a Haiku Explore subagent to read recent session JSONL files from `~/.claude/projects/`
(current project, newest-first, 3-5 sessions max). Return a terse summary of what was worked
on, key decisions, and open threads — focused on: **"{args}"** if provided, otherwise broadly.
