---
description: Apply or revert the caveman output style for the current session
---

Arguments: $ARGUMENTS

If the arguments are `off`: revert to the default output style for the rest of this session,
dropping any caveman-style instructions currently in effect.

Otherwise: read `~/.claude/output-styles/caveman.md` and follow it as the output style for the
rest of this session.
