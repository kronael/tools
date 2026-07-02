---
name: release
description: Prepare a release. NOT for a single commit (use commit).
when_to_use: "prepare a release, cut a release, tag a release"
user-invocable: true
---

# Release

## Process

0. **Read local CLAUDE.md** — `Read` the project's `CLAUDE.md` (at CWD).
   Look for a `## Release` section. Any directive there **overrides** the
   defaults in this skill. Common overrides to watch for:
   - `No tagged releases` → skip step 7 entirely (no `git tag`)
   - Custom checklist → run those steps instead of (or in addition to) step 5
   - Pinned version file or changelog path → use that instead of discovering
   Apply found overrides before proceeding. If the section is absent, use
   skill defaults throughout.

1. **Detect scope** — `git tag --list` + `git log` since last tag.
   - No prior tags → first release. Default `v0.1.0` (matches pyproject's
     usual default); skip the bump step if pyproject already says it.
2. **Version bump** — patch default. Discover the version file:
   - Python: `pyproject.toml` `version = "..."` (each subdir pyproject
     in a monorepo gets bumped independently)
   - Rust: `Cargo.toml` `version = "..."`
   - JS/TS: `package.json` `"version": "..."`
   - CLAUDE.md may pin which file is canonical when multiple exist;
     otherwise discover the deepest one and bump there.
3. **Changelog** — `CHANGELOG.md` at repo root.
   - File exists with `[Unreleased]` → move to `[vX.Y.Z] — YYYYMMDD`.
   - File missing → create with one section `[vX.Y.Z] — YYYYMMDD`.
     First release needs no `[Unreleased]` placeholder.
   - Multi-deployable repos (sibling subdirs with own pyproject) —
     each subdir gets its OWN `CHANGELOG.md` for that deployable. Root
     changelog summarises across them.
   - Empty since-last-tag → generate entries from `git log <last>..HEAD`.
3.5. **Distill to ~20%.** Re-read the just-written entry. Two passes:

   **Pass A — the `>` blockquote (broadcast).** This is the verbatim
   chat-broadcast — what the user reads in Telegram/Discord/email.
   Shape:

   ```markdown
   > <project> vX.Y.Z — <3-6 word tagline>
   >
   > <one sentence: what changed, why a user cares>
   >
   > • <change> — <what now works better>
   > • ...
   >
   > Full notes: <changelog URL>
   ```

   Audience: a sharp, curious 13-year-old skimming a channel AND an
   engineer asking "is this real?". Accessible, not dumbed down.

   - **Lede sentence** (≤ 22 words) is the ONLY prose permitted. Plain
     English distillation: a skimmer must learn what shipped from this
     sentence alone. Not a teaser.
     - Good: `Replies to the bot now count as mentions, so the agent actually answers when you tap reply.`
     - Bad: `We're excited to introduce a powerful new mention-detection pipeline.` (puffery)
     - Bad: `Promotes inbound reply_to_id to verb=mention via the ring-buffer matcher.` (jargon)
   - **Bullets**: 3–6 lines, ≤ 100 chars each. Each is a technical
     change framed as user-observable behavior. Name the API/verb —
     engineers want the hook — but lead with what now works.
     - Good: `• Routes get a #observe mode — store messages as context without firing the agent.`
     - Bad: `• Refactored impulse_config into match-key seq priority.` (no behavior delta)
   - **Banned**: "powerful", "seamless", "robust", "excited to announce",
     "we've improved", "various", exclamation marks (unless something
     actually exploded), emoji decoration, migration numbers, file
     paths, commit SHAs, internal symbol names without context.
   - **Group only when forced**: >6 bullets → collapse related ones
     (`• Voice & media — send_voice + per-platform dispatch`). 3 sharp
     bullets beat 6 padded ones.
   - Project may pin tagline/footer in its CLAUDE.md `## Announcing`
     section — that overrides.

   **Pass B — the `### Added / ### Changed / ### Fixed` body.**
   Maintainer-facing. Compress to ~20% of raw commit-log paraphrase.

   - Lead with notable user-facing features. First bullets name what
     the user can now do, in user vocabulary.
     Internal refactors and plumbing go after.
   - One line per change. Drop commit SHAs and internal-only file
     paths from body bullets (migration numbers and `Spec: specs/X.md`
     pointers stay).
   - Collapse synonymous bullets across sections.
   - Cut multi-sentence "why" paragraphs.
   - If total body bullets ≤ 5, collapse to a single un-headed list.
   - Preserve at full detail (never trim): security fixes, breaking
     changes, env-var renames, schema migrations, anything the
     blockquote already advertises as headline.
   - Preserve verbatim: the `>` blockquote, any `### Operator note`,
     `### Schema` env/migration tables.
   - Report ratio: "body 84 → 18 lines (21%)". Abort and ask if
     compression would drop a load-bearing item.

   Sizing guide: most entries land in the 15–30 line range after
   distill. 80+ line bodies are the smell. Look at the prior 3-5
   entries in this repo for what the project considers a typical wave.
4. **Docs alignment** — only spawn refine if README/CLAUDE.md carry
   version-dependent stats (test counts, line counts, version strings).
   Skip when nothing version-shaped is documented.
5. **Verify** — `make test`, `make smoke` if defined. For monorepos
   with sibling deployables, run each subdir's `make test` too.
6. **Commit** — version files + CHANGELOG(s) in one `[release]` commit.
7. **Tag** — `git tag vX.Y.Z`. ONE tag per repo even when there are
   multiple deployables; subdir versions track in their own pyprojects.

## Rules

- ALWAYS `git tag vX.Y.Z` on the release commit
- NEVER push (`git push`)
- NEVER compress the `>` blockquote past the rules above — it's broadcast verbatim
- NEVER drop security fixes, breaking changes, schema migrations, env renames during distill
- Default to patch bump unless user says otherwise
- No changes since last tag → "nothing to release", stop
- First release with no prior tag → tag whatever pyproject already
  says (typically 0.1.0). Don't fabricate a 0.0.0 → 0.1.0 bump just
  to have a delta.
- Monorepo sibling deployables → ONE `git tag` at repo root; each
  deployable's pyproject version is independent of the tag
