---
name: sub
description: /sub — launch a background subagent. NOT for tasks the main thread needs results from.
when_to_use: "do this in the background", "run this separately", "do X while I do Y"
user-invocable: true
---

Launch the prompt after /sub as a background general-purpose agent (run_in_background: true).
Report what was launched. Continue immediately without waiting.
