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

Resume interrupted work this session; if there is none, look forward.

## Behavior

- Check memory, diary, agent notifications, and conversation for anything unfinished
- Resume or relaunch each; report what was resumed
- If nothing is unfinished, do NOT stall — say the session/repo is in a clean
  state, then help the user look forward:
  - suggest `/recall-memories` to surface prior context and open threads
  - read the diary + `TODO.md`/`BUGS.md` + recent commits, then present where to
    go from here as a few concrete candidate directions
  - ASK which to pick up; never guess and start work unprompted
