# TODO

## nudge.py: skill nudges based on file extensions

When Claude reads or edits files with known extensions, nudge the matching skill.

**Mapping:**
- `.rs`, `Cargo.toml` → `/rs`
- `.py`, `pyproject.toml` → `/py`
- `.go`, `go.mod` → `/go`
- `.ts`, `.tsx`, `package.json` → `/ts`
- `.sh` → `/sh`
- `.sql` → `/sql`

**Hook event:** `PreToolUse` on `Read` and `Edit` tool calls — inspect the
`file_path` param, extract extension, emit systemMessage nudging the skill.

**Dedup:** only nudge once per skill per session (track in a state file like
`local.py` does with `.claude/tmp/nudged-{session_id}`).

## nudge.py: stricter matching (2-edit distance)

Make the nudge matching stricter — only nudge when the extension match is
within ~2 edit distance (Levenshtein). Prevents false positive nudges from
loose substring matching. Example: `.rst` should NOT nudge `/rs`.
