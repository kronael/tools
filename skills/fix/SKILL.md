---
name: fix
description: One-shot bug fix from a screenshot or short report. NOT for refactors or vague improvement (use improve).
when_to_use: "fix this bug, screenshot bug, capture.png, broken UI, one-shot fix, small bug report, describe debug suggest fix"
user-invocable: true
---

# /fix

Single bug, single fix, single pass. The user shows something broken, usually
a screenshot, and wants it gone. Run the four-step audit trail before editing.

## Behavior

If the target is unclear, ALWAYS try to read `./capture.png`, then
`/tmp/capture.png`. If neither file exists and no bug is described, ask the
user what to fix.

1. **Describe** — what is on screen or in the report. Read actual values,
   labels, and colors. No interpretation yet.
2. **Bug** — one sentence naming the contradiction or broken behavior.
3. **Debug** — locate the producing code and the wrong condition.
4. **Suggest fix** — one sentence on the corrective rule, then apply it.
5. **Verify** — run the project's typecheck and tests.

## Rules

- ALWAYS read the screenshot before any other tool call if one has not been
  read yet.
- NEVER propose multiple alternatives — ALWAYS pick one fix.
- NEVER refactor surrounding code — ALWAYS touch the minimum that fixes the bug.
- NEVER ask "want me to apply this?" — the user already asked.
- NEVER add tests unless the bug class is repeating.
- Stop and ask if the fix changes a public API, turns into a design question,
  or cannot be reproduced from the screenshot/report.
