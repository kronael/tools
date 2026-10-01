---
name: sync-tools-skills
description: Vendor agent skills from an upstream tools repo into another project, then deliver them to its live agents. NOT for syncing ~/.claude with the tools repo (use kronael/sync), authoring a new skill (use wisdom), or general code (use the language skill).
when_to_use: vendor skills from kronael/tools, refresh a project's vendored agent skills, refresh agent skill bundle, update create-* skills, take skills from tools, deliver new agent skills, bump migration version for skills
---

# Vendor agent skills from an upstream tools repo

A project that ships an in-container agent (e.g. arizuko's `ant/skills/`) vendors
SOME skills from a shared tools repo. Refresh + deliver them in five steps.

- ALWAYS vendor a NAMED allow-list of skills — NEVER bulk-copy all of
  `tools/skills/`: same-name skills (diary/go/oracle/specs) would clobber the
  project's tuned versions.
- ALWAYS `rsync -a --delete <tools>/skills/<name>/ <project>/ant/skills/<name>/`
  per vendored skill (delete-sync so removed upstream files don't linger).
- After refresh, ALWAYS review `git diff -w` — if the only diff is whitespace,
  the bundle is already current; discard the churn (`git checkout`).

## Deliver to live agents (the part that's easy to forget)

A rebuilt agent image only reaches FRESH groups. EXISTING groups get the new
skills + merged CLAUDE.md only on `/migrate`, which fires when the agent's
`MIGRATION_VERSION` exceeds the group's. So after refreshing:

1. Bump `ant/skills/self/MIGRATION_VERSION`.
2. Add `ant/skills/self/migrations/<N>-vX.Y.Z-<topic>.md` — its first lines are
   the chat broadcast. Update `migration.md` "Latest migration version".
3. `sudo make -C ant image` (bakes the new version + skills).
4. NEVER assume the migrate fired — VERIFY: routd reads the upstream
   `MIGRATION_VERSION` at startup (`checkMigrationVersion`) from its mounted
   repo source and enqueues `/migrate` for behind root groups. Restart each
   instance so its routd re-reads the bump, then confirm a group's stored
   version advanced and the new skills seeded into its `~/.claude/skills/`.
   If routd has NO repo-source mount, the trigger can't fire — fix the mount.

If the project ships a thin wrapper script for step-1 (the rsync allow-list),
run it; otherwise rsync the named skills by hand.
