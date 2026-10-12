---
name: serena
description: Rename a Python or Rust symbol across a project in one call through Serena's language-server rename, started on demand. NOT for Go (use go), TypeScript (use ts), finding callers (use the LSP tool) or a text change that is no symbol (use astgrep).
when_to_use: "rename a symbol, rename a function, rename a method, rename a class, rename across files, rename_symbol, Serena, refactor rename in Python, rename in Rust, grep-and-edit rename broke something"
user-invocable: true
---

# Serena

Serena wraps the installed language servers and adds the one thing the
read-only `LSP` tool lacks: an edit that follows the server's references.
`call.py` in this directory starts it for one tool call over stdio and stops
it. NEVER register Serena as an MCP server — `kronael/sync/reference.md`
§ External tool commands in the bundle source repo owns the install and the
config, and says why.

```sh
python3 ~/.claude/skills/serena/call.py rename_symbol \
  '{"name_path": "hook_event", "relative_path": "hooks/lib/state.py", "new_name": "read_hook_event"}'
```

- Run it from inside the git project: it activates the top level of the
  working tree. A Python rename takes about 2 s, start to stop.
- `name_path` is the symbol's path inside the file: `Class/method` for a
  method, the bare name for a top-level definition.
- Exit 0 prints Serena's reply; 1 means the tool refused (no such symbol);
  2 means Serena did not start or answer, with its log tail on stderr.

## Which language

- **Python** — `call.py rename_symbol`. Measured exact: 5 files, tests pass.
- **Rust** — `call.py rename_symbol`; an inherent method's `name_path` is
  `impl Type/method`. rust-analyzer loads the default cargo features only,
  so code behind a disabled feature keeps the old name while the default
  build stays green — 2 of 7 sites in one rename, a trait impl in another.
  ALWAYS `rg -nw '<old name>'` after it, rename each leftover in gated code
  by hand, and `cargo check --features <feature>` for each gate it touched.
- **Go** — `gopls rename` (`go` skill), which shows the diff before it writes.
- **TypeScript** — ts-morph `rename()` (`ts` skill). NEVER Serena: in a pnpm
  monorepo it renamed 3 of 25 references and reported success.

## Rules

- ALWAYS start a rename on a clean tree — `rename_symbol` writes at once and
  has no dry run.
- NEVER take "Successfully renamed" as proof — Serena says it after a
  partial rename too (Rust and TypeScript above). ALWAYS read `git diff` and
  run the type check and the tests before the rename counts as done.
- NEVER grep-and-edit a rename that a language above covers — `sed -w` on a
  Python rename passed the tests and silently renamed a dict key of the same
  name.
