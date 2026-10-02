---
name: settings-restrictions-declined
description: "User runs bypassPermissions with sandbox disabled by choice — declined the toolkit's recommended restrictions."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3ae76b91-513b-4edc-9d1b-ba79473e1155
  modified: 2026-07-21T08:36:13.125Z
---

On the 2026-07-21 kronael install the user declined both offered settings
restrictions: keep `permissions.defaultMode = bypassPermissions` (no prompts)
and keep `sandbox.enabled = false`. They run wide-open deliberately.

**Why:** Fast frictionless local dev is the user's chosen tradeoff; the
recommended sandbox/perm-mode are the toolkit default, not their preference.

**How to apply:** The install skill still asks about restrictions each run
(don't skip the ask), but present them neutrally — do NOT frame enabling
sandbox or `default` perm mode as something they "should" turn on. Default to
preserving their current choices. Auto-apply items (cleanupPeriodDays,
outputStyle, hook wiring) are unaffected.
