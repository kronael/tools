# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## install: `go install ...trufflehog/v3@latest` fails (replace directives)

`kronael/install/reference.md` § "External tool commands" (Security audit)
installs `trufflehog` via `go install github.com/trufflesecurity/trufflehog/v3@latest`.
That fails: its `go.mod` contains `replace` directives, so `go install` refuses
("must not contain directives that would cause it to be interpreted differently
than if it were the main module"). Fix: install the release binary like gitleaks
— `linux_amd64.tar.gz` from github.com/trufflesecurity/trufflehog/releases into
`~/.local/bin`. Found 2026-07-21 during a full "install all tools" run; worked
around with the release binary (v3.95.9) so the install completed.

## install: prune list omits eye-13yo/hacker-eval/testing renames

The v0.3.67 renames — `eye-13yo`→`13yo-eval`, `hacker-eval`→`red-eval`,
`testing` folded into the `software` router — were never added to the
removed-skills prune list in `kronael/install/`. Reinstalls therefore leave the
old dirs as orphans in `~/.claude/skills/` (the descriptions keep preloading).
Per `skills/CLAUDE.md`, a removed/renamed dir MUST be added to that prune list.
Fix: add the three to the prune list. Found 2026-08-05 during "sync and install
all" (the three orphans were pruned by hand).

## install: reference.md security tools still cite /hacker-eval (now /red-eval)

`kronael/install/reference.md` security-audit table lists bandit, pip-audit,
semgrep, govulncheck, trufflehog, gitleaks as serving `/hacker-eval`, but that
skill was renamed to `red-eval` in v0.3.67. Fix: update the Skills column to
`/red-eval`. Found 2026-08-05.
