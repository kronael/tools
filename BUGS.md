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
