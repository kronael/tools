---
name: con
description: /con — goal mode. Recall every interrupted, paused, or
  abandoned task/plan/goal from this session (not just live agent
  processes) and resume each. NOT for just pushing the single current
  in-flight task to completion without stopping (use fin).
when_to_use: >
  "continue", "resume", "pick up where we left off", "finish the unfinished",
  "resume the agents", "resume the paused work", "what was left"
user-invocable: true
---

# /con — continue mode (goal mode)

Recall everything interrupted, paused, or left abandoned this session —
tasks, plans, agent runs, half-finished goals, however they surfaced — and
resume each.

## Procedure

1. **Load context** — read `~/.claude/projects/<slug>/memory/MEMORY.md`
   (slug = absolute CWD with `/` → `-`, e.g. `/home/user/app/foo` →
   `-home-user-app-foo`), the most recent `<cwd>/.diary/*.md` entry, and
   skim the conversation for the last task list, plan, or eval output.
2. **Inventory** — every agent notification in the session (running /
   paused / completed, with agentId and last known state), and every
   pending item anywhere in the conversation (unactioned findings, plan
   phases not yet built, "remaining" notes, half-done features, tests left
   open).
3. **Resume agents** — still-resumable ones get a `SendMessage` nudge to
   their agentId ("continue from where you left off: [state]"), not a
   re-brief from scratch. Not-resumable ones get relaunched with the
   original task plus what's already done and what remains. Relay each
   agent's final message back, not raw output.
4. **Act** on every inventoried item in priority order, verifying with the
   actual command or diff — a success report alone isn't verification.
5. **Report** — what was resumed, what was completed, and what (if
   anything) is still blocked and why.
