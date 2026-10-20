# Language servers and code-intelligence MCP

Three independent mechanisms that answer different questions. ALWAYS set up
the first two; Serena never runs as a server.

| Mechanism | Surfaces as | Coverage |
|---|---|---|
| LSP plugin | `LSP` tool (hover, goToDefinition, findReferences, goToImplementation, callHierarchy) — read-only, no rename | go, rust, python, typescript |
| gopls MCP | `go_*` tools (diagnostics, package API, symbol refs, rename diff, vulncheck) | Go only |
| Serena, one call at a time | the `serena` skill's `call.py rename_symbol` — a rename that follows the language server's references | the languages its table names |

## Which tool changes code

The language tools (gopls, ts-morph, LibCST, `go fix`) live in each language
skill; listings and comment edits in `astgrep`.

- ALWAYS rename a symbol with the tool the `serena` skill's language table
  names — NEVER grep-and-edit. It follows the language server, so
  `module.name` access from other files renames too.
- ALWAYS find a symbol's callers (`LSP` findReferences) and an interface's
  implementers (goToImplementation) before changing a signature — NEVER grep
  for them. In Go, ALWAYS the `go` skill's `go_symbol_references` instead.
  Serena's `find_referencing_symbols` returned the same set at 3-7 times the
  bytes (Python 7.4x, Go 3.1x).
- One text change across many files that is no symbol (a config key, a log
  string): ALWAYS list every hit with `rg -n` before the edit and read `git
  diff` after; `code` § System changes bans the scripted replace.

## The rule that bites

LSP plugins ship NO binary. Enabling `<lang>-lsp@claude-plugins-official` in
`settings.json` → `enabledPlugins` only wires up a server that must ALREADY be
on PATH. A plugin listed as enabled with a missing binary fails silently — the
`LSP` tool just returns no results. ALWAYS verify the binary before believing
the plugin works.

## Install

```bash
go install golang.org/x/tools/gopls@latest              # → $HOME/go/bin
rustup component add rust-analyzer                      # → $HOME/.cargo/bin
npm i -g pyright typescript-language-server typescript  # bun i -g also works
```

- No rustup yet: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --no-modify-path --component rust-analyzer`
- ALWAYS `--profile minimal` — the default profile pulls rust-docs for nothing.
- rust-analyzer NEEDS `cargo` on PATH; it shells out to `cargo metadata`. A
  standalone rust-analyzer binary without a toolchain is dead weight.

## PATH is the usual failure

Claude Code's shell PATH is built from the login profile, which on a sandboxed
box may be masked and unwritable — so `--no-modify-path` installs land outside
PATH. ALWAYS symlink into a directory already on PATH rather than editing a
profile that will not be read:

```bash
for b in rust-analyzer cargo rustc rustup; do ln -sf "$HOME/.cargo/bin/$b" "$HOME/.local/bin/$b"; done
```

Check with `echo $PATH | tr ':' '\n'` FIRST — `$HOME/go/bin` and `$HOME/.bun/bin`
are usually present, `$HOME/.cargo/bin` usually is not.

## gopls MCP server

```bash
claude mcp add -s user gopls -- gopls mcp
claude mcp list                    # must print: gopls: gopls mcp - ✔ Connected
```

ALWAYS register at `-s user` scope when the project `.mcp.json` is absent,
masked, or not a regular file — `claude mcp list` names that file in its
diagnostics when it cannot parse it. Tool details: `go` skill.

## Sandbox

Installs need `dangerouslyDisableSandbox: true`. Two distinct blocks, both
expected: the Go module cache under `$HOME/go/pkg/mod` is read-only, and
`$HOME/.claude.json` (which `claude mcp add` writes) is deny-listed. Neither is
a network problem — ALWAYS read the actual error before assuming the allowlist.

## Verify — never assume

ALWAYS prove each server answers on a real file of that language:
`LSP(operation: "hover")` on a function name must return its signature.

- rust-analyzer alone: `rust-analyzer analysis-stats <crate-dir>` — "Mir failed
  bodies: 0" means it indexes fine.
- Servers root at the session cwd. A file OUTSIDE that workspace degrades:
  gopls answers hover but warns "not included in your workspace";
  rust-analyzer returns nothing at all. An empty rust hover therefore means
  wrong workspace FIRST, broken install second.
