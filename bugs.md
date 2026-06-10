# bugs

## settings-recommended.json references a hook file that doesn't exist

`settings-recommended.json` wires `~/.claude/hooks/prompt_nudge.py` on
UserPromptSubmit, but `hooks/` only ships `pretool_nudge.py` (a
PreToolUse hook that nudges based on file extension).

The previous `nudge.py` was deleted in the merge that brought in
`pretool_nudge.py` — looks like the split was incomplete. Three
plausible fixes:

1. Add a real `hooks/prompt_nudge.py` (UserPromptSubmit-side fuzzy
   keyword → skill matcher, formerly the job of `nudge.py`).
2. Remove the `prompt_nudge.py` reference from
   `settings-recommended.json` if the prompt-side nudge is no longer
   wanted.
3. Rename `pretool_nudge.py` → `prompt_nudge.py` if they were meant to
   be one file (unlikely — the matcher field on PreToolUse is needed
   for the file-extension nudge).

Discovered during `say install` at 20260610-194538.
