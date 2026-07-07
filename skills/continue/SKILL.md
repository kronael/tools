---
name: continue
description: /continue — goal mode. Recall every interrupted, paused, or
  abandoned task/plan/goal from this session and resume each. NOT for just
  pushing the single current in-flight task without stopping (use fin).
when_to_use: >
  "continue", "resume", "pick up where we left off", "finish the unfinished",
  "resume the agents", "resume the paused work", "what was left"
user-invocable: true
---

# /continue — continue mode (goal mode)

Recall interrupted or abandoned work this session and resume it.

## Behavior

- Check memory, diary, agent notifications, and conversation for anything unfinished
- Resume or relaunch each; report what was resumed
- If nothing is unfinished: read the diary + `TODO.md`/`BUGS.md` + recent commits,
  then ASK the user which thread to pick up — present the top candidates, never
  guess and start work unprompted
