---
name: codemap
description: Map a codebase and drill into it — ranked overview, task lookup, callers, blast radius — and generate module, import and call graphs from the code. NOT for hand-drawn diagrams (use diagrams), a mid-conversation sketch (use show-me) or structural search and rewrite (use astgrep).
when_to_use: "map the codebase, orient in a new repo, codebase overview, unfamiliar repo, where is X implemented, which code does this task touch, drill down, who calls this, every use of a symbol, blast radius, what breaks if I change X, god files, import cycles, call graph, import graph, package graph, module graph from code, generate a diagram of the code, interactive call graph, ripwire, goda, pydeps"
user-invocable: true
---

# Codemap

Views of a codebase generated from its source, run on demand: one `ripwire`
binary for Python, TypeScript, Go and Rust, plus one graph tool each for Go
packages and Python imports. Nothing here runs as a server or loads at
session start.

`ripwire` missing from PATH: ALWAYS stop and ask the owner to run the
binary-only install, `kronael/sync/reference.md` § ripwire in the bundle
source repo (`~/.claude/LOCAL.md` names its path). NEVER substitute a grep
tour and call it a map.

## Orient, then drill down

| Question | Command |
|---|---|
| What is in this repo | `ripwire <dir> --tree` (each file's top symbols), then `ripwire <dir> --max-tokens=3000` (ranked signatures with resolved callees) |
| Which code a task touches | `ripwire <dir> --for="<the task in plain words>"` |
| One symbol's body | `--expand=<file>:<name>` (body plus the signatures it calls); `--outline=<file>:<name> --top-k=0` (control-flow skeleton; without `--top-k=0` the ranked top-200 map follows it) |
| Who calls it | `--callers=<file>:<name>` |
| Every use — reads, imports, trait or interface dispatch | `--uses=<name>` |
| What breaks if it changes | `--impact=<file>:<name>` (the blast radius, split into tested and untested) |
| God files and import cycles | `--deps` |

- ALWAYS take the `next=` attribute when present — `--callers`, `--impact`
  and `--for` end with one; it is the pasteable follow-up call.
- ALWAYS qualify a name that more than one file defines as `<file>:<name>`. A
  bare common name merges every definition: in a Go repo `--callers=Close`
  gave 5 defs and 218 callers, `--callers=store/store.go:Close` 172. The
  not-found error lists the defining files.
- NEVER read `count="0"` from `--callers` on a trait or interface method as
  "unused". ripwire declines a call it cannot bind to one definition
  (`declined_calls=`), so dispatch through a trait reads as no callers: 0
  callers and 10 uses for one Rust trait method. ALWAYS run `--uses` there, or
  the LSP tool's findReferences and goToImplementation.
- `--max-tokens` shapes the default map and `--for --detail=N`; plain `--for`
  ignores it.
- `--json` mirrors the XML keys for the map, `--for`, `--callers`,
  `--callees` and `--impact`; `--tree` has no JSON form.
- NEVER treat a map as the reference set for a rename or signature change —
  the language skill's rename tool and the LSP tool own that (`software` →
  `lsp.md`).

## Diagrams from the code

ALWAYS write output under the project's gitignored `./tmp/` (`mkdir -p tmp`
first) — NEVER a tracked path.

| Picture | Command |
|---|---|
| Module (directory) flowchart, any language | `ripwire <dir> --mermaid > tmp/modules.mmd` — Mermaid text; an edge is 3 or more inter-module calls, not imports (file imports: `--deps`); show it inline, or hand it to `show-me` |
| Interactive call graph the owner opens in a browser | `ripwire <dir> --html=tmp/callgraph.html`, colour with `--color-by=lang`, `community`, `cx` (complexity), `churn` or `tested` |
| Go package graph | `go run github.com/loov/goda@v0.10.1 graph -short ./... \| dot -Tsvg -o tmp/packages.svg` |
| Python import graph | `uvx pydeps <pkg> --noshow --show-dot --no-output > tmp/imports.dot`, then `dot -Tsvg` |

- ALWAYS draw a single-package Python repo's imports with pydeps: its
  `--mermaid` has one directory and next to no edges (1 edge against
  pydeps' 53 on one repo).
- NEVER install mermaid-cli to render — it pulls in Chromium. ALWAYS render
  DOT with the installed `dot` and leave Mermaid as text.
- NEVER dependency-cruiser or madge for a TypeScript graph — without a
  per-repo config the first refuses to run and with `--no-config` crawls
  `node_modules` and `dist`, and the second draws edges into `dist/*.d.ts`.
  ALWAYS `ripwire --deps` for TypeScript imports instead.
