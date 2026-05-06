---
name: sub
description: /sub <prompt> — launch prompt as background subagent. NOT for sequential tasks the main thread needs results from.
when_to_use: fire-and-forget independent work, "run this in the background", "do X while I do Y", /sub
user-invocable: true
---

Launch the prompt after /sub as a background general-purpose agent (run_in_background: true).
Report what was launched. Continue immediately without waiting.
