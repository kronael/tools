---
name: sub
description: /sub — launch a background subagent with optional model tier (haiku/sonnet/opus/fable). NOT for tasks the main thread needs results from inline.
when_to_use: "do this in the background, run this separately, do X while I do Y, spawn a sub, haiku sub, use haiku, sonnet sub, use sonnet, opus sub, use opus, fable sub, use fable"
user-invocable: true
---

Parse the first word after /sub. If it matches a tier, apply it; otherwise omit both `model` and `subagent_type`.

| Prefix | Agent tool | Effort | Use for |
|--------|-----------|--------|---------|
| `haiku` | `model: "haiku"` | (none) | Mechanical: rename, single-file edit, lookup |
| `sonnet` | `subagent_type: "sonnet"` | high | Coding, exploration, pre-review |
| `opus` | `subagent_type: "opus"` | xhigh | Complex reasoning, architecture, design |
| `fable` | `subagent_type: "fable"` | xhigh | Hardest problems, long-horizon agentic |
| *(none)* | *(omit both)* | — | General background work |

- ALWAYS use `subagent_type` for sonnet/opus/fable — their agent definitions pin effort; `model:` alone cannot set effort and prompt text like "think deeply" does nothing at the API level.
- ALWAYS use `model: "haiku"` (no subagent_type) — no haiku agent definition exists or is needed.
- ALWAYS set `run_in_background: true`.
- NEVER pass a bare task — ALWAYS include scope (files/dirs), constraint, and what to return.
- ALWAYS write the prompt as if the subagent has zero session memory — paste paths, errors, and acceptance criteria inline.
