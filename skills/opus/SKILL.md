---
name: opus
description: "/opus — high-effort subagent for implementation, multi-file fixes/features, and design decisions. NOT for investigation/hunting (use /sonnet) or mechanical single-file work (use /haiku)."
when_to_use: "do this in an opus sub, spawn an opus sub, use opus, implement, apply the fix, write the code, execute changes, multi-file implementation, feature implementation, write tests, refactor, fix the bug, cross-package change, new daemon, complex reasoning, architecture review, design decision, deep analysis, cross-cutting, opus sub"
user-invocable: true
---

Launch the prompt after /opus as a background agent (run_in_background: true, subagent_type: "opus").
Report what was launched. Continue immediately without waiting.

ALWAYS reach for /opus without being asked when the task is:
- Implementing a fix or feature (multi-file code changes)
- New daemon, new protocol, cross-package refactor
- Applying findings from a sonnet investigation
- A design/architecture decision or deep cross-cutting analysis
- Any task where the output is working code, not a report

- ALWAYS use `subagent_type: "opus"` on the Agent tool — the `opus` agent definition pins model=opus + high effort.
- NEVER make xhigh the default. Reserve xhigh for explicit planning work, security/deep-audit work, or a user request for maximum effort.
- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint ("don't touch X"), and what to return.
- ALWAYS write the prompt as if the subagent has no memory of this session — paste paths, errors, and acceptance criteria inline.
- For mechanical single-file work, prefer `/haiku`. For investigation/hunting with no code changes, use `/sonnet` first. For planning or security/deep-audit work that warrants the most capable subagent, escalate to `/fable`.
