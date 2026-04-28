---
name: release
description: Prepare a release. Version bump, changelog, docs alignment, git tag.
user-invocable: true
---

# Release

## Process

1. Detect scope — `git log` since last tag
2. Version bump — patch default, detect version file from project language (CLAUDE.md SHOULD define which)
3. Changelog — move [Unreleased] to `[vX.Y.Z] — YYYYMMDD`, generate from git log if empty
4. Docs alignment — spawn refine agent: update CLAUDE.md, README if version/stats changed
5. Verify — `make test`, `make smoke` if available
6. Commit version + changelog
7. `git tag vX.Y.Z` — the tag IS the release

## Rules

- ALWAYS `git tag vX.Y.Z` on the final commit
- NEVER push (`git push`)
- Default to patch bump unless user says otherwise
- No changes since last tag → "nothing to release", stop
