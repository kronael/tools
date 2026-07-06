---
name: astgrep
description: Structural code search and rewrite with ast-grep (tree-sitter AST patterns). NOT for type-aware refactors (use the LSP/language skill) or literal search (use ripgrep). NOT for SQL — no built-in grammar.
when_to_use: ast-grep, structural search, structural find/replace, codemod, batch refactor by pattern, rewrite a call pattern across the repo, find all usages structurally, sgconfig, YAML lint rule, match by AST node kind
user-invocable: true
---

# astgrep — structural search & rewrite

Search and rewrite code by its tree-sitter AST, not text. A pattern is real
code with meta-variables; matches respect nesting and skip strings/comments.
Methodology + citations: `docs/astgrep/research-astgrep.md`.

ALWAYS invoke the binary as `ast-grep`. NEVER rely on `sg` — it collides with
shadow-utils' `/usr/bin/sg`; `uv tool upgrade ast-grep-cli` recreates the shim.

## When to invoke / NOT

- USE for: "every `console.log` call regardless of args", multi-line
  constructs, a codemod across many files, AST-`kind`/structure queries.
- NOT for semantic edits (scope-aware rename, follow imports, resolve
  overloads) — ast-grep has no types or cross-file symbol table; use the LSP.
- NOT for a trivial literal string — ripgrep is faster.
- Built-in languages here: `go rust python typescript tsx bash`. Use `tsx`
  (not `ts`) for any file with JSX. **SQL is NOT built in** — it needs a
  compiled tree-sitter grammar under `customLanguages` in `sgconfig.yml`
  (a build step, plus `expandoChar` since `$VAR` isn't valid SQL). Don't
  pretend `-l sql` works.

## Commands

`ast-grep run` — ad-hoc, pattern-driven. `ast-grep scan` — runs YAML rules.

```sh
# search
ast-grep run -p 'console.log($MSG)' -l ts src/
# rewrite: ALWAYS preview (no -U) first, eyeball the diff, then apply
ast-grep run -p 'print($A)' -r 'logging.info($A)' -l py .
ast-grep run -p 'print($A)' -r 'logging.info($A)' -l py -U .   # applies
# rule-based (maintained codemods/lints)
ast-grep scan -r rule.yml --globs '!**/vendor/**' .
```

Useful flags: `-i` interactive confirm, `-U/--update-all` apply all,
`--json[=stream]` machine output, `--debug-query[=ast]` show how a pattern
parsed (reach for this the moment a pattern "should match but doesn't").

## Pattern syntax

- `$VAR` — exactly one **named** node. Uppercase/digits/underscore only.
- `$$$` / `$$$ARGS` — zero or more nodes (args, params, statements).
- `$_` (or `$_X`) — single node, **not captured**.
- Reusing a name forces equality: `$A == $A` matches `a == a`, not `a == b`.
- `$$VAR` — matches **unnamed** nodes (operators) that `$VAR` skips.

ALWAYS write a pattern that is **syntactically valid code** in the target
language — `$LEFT $OP $RIGHT` and dangling fragments silently fail to match.
For ambiguous or fragment patterns, use a **pattern object** instead of a bare
string: `context:` (a larger valid snippet) + `selector:` (the node kind to
return), or match by `kind:` directly.

## Rewrite safety — the iron rules

A bare `run -p/-r` **over-matches by construction**. Codex-verified failures
(see `docs/astgrep/codex-critique.md`):

- `console.log($$$) -> ''` wrecks expressions: `() => console.log(a)` becomes
  `() => `. Delete log *statements* only via a scan rule with
  `inside: { kind: expression_statement }`.
- `$E.unwrap() -> $E?` fires in `let x = value.unwrap();` → invalid Rust.
- `<Old $$$P />` matches only self-closing JSX, never elements with children.

Therefore:

- ALWAYS preview without `-U` (or use `-i`) on a clean git tree first.
  `-U` is **destructive with no undo**.
- ALWAYS scope a real rewrite with `inside`/`has`/`kind` in a `scan` YAML rule
  rather than a broad `run -r` one-liner.
- ALWAYS run the formatter after (`gofmt`/`rustfmt`/`prettier`/`ruff format`).
  ast-grep substitutes nodes; it does **not** reformat or fix indentation.
- ast-grep has no types — review every hunk a rewrite produces.

## YAML rules

```yaml
id: no-console-log
language: TypeScript
rule:
  pattern: console.log($$$A)
  inside: { kind: expression_statement }
fix: ''
```

- Atomic: `pattern`, `kind`, `regex` (Rust regex — **no look-around or
  backrefs**), `nthChild`, `range`.
- Relational: `inside`, `has`, `follows`, `precedes`, each with `stopBy`
  (`neighbor` default | `end` | a rule).
- Composite: `all`, `any`, `not`, `matches` (reference a `utils` rule).
- `constraints` (per meta-var sub-rules), `transform` (derive vars before
  `fix`), `rewriters` (recursive sub-rewrites).

Project config `sgconfig.yml`: `ruleDirs`, `utilDirs`, `testConfigs`,
`languageGlobs`, `customLanguages`. `scan` discovers rules from `ruleDirs`.
Test rules with `ast-grep test` (`valid:` must not match, `invalid:` must).

## Strictness

Default `smart` skips "trivial" nodes in the target — surprising over-matches
(a dropped `async`/quote style) mean tighten toward `ast` or `cst`. Levels
strict→loose: `cst`, `smart`, `ast`, `relaxed`, `signature`, `template`.

## Anti-patterns

- Broad `run -r` codemod applied with `-U` unreviewed — corrupts expression
  contexts and unscoped matches.
- Bare pattern for ambiguous code (`a: 123`) — use `context`+`selector`/`kind`.
- Trusting auto-detect on JSX — pass `-l tsx` explicitly.
- Skipping the formatter pass — leaves mis-indented output.
- Claiming SQL works — it needs a custom grammar build first.

## Reference

`docs/astgrep/research-astgrep.md` (cited methodology),
`docs/astgrep/codex-critique.md` (empirical breakage), ast-grep.github.io.
