# ast-grep: Grounded Methodology Reference

Research basis for a Claude Code skill on structural code search and rewrite.
All non-obvious claims cite their source. Where a blog and the official docs
(`ast-grep.github.io`) disagree, the docs win and the disagreement is noted.

Primary source throughout: the official documentation at
<https://ast-grep.github.io>. Fetched June 2026.

## 1. What it is / when to reach for it

ast-grep is a Rust CLI for searching, linting, and rewriting code using the
Abstract Syntax Tree (AST) produced by tree-sitter parsers, not text matching.
The docs frame it as "grep but based on AST instead of text" — "using code to
search code with the same pattern"
(<https://ast-grep.github.io/guide/introduction.html>). It scales from a single
`-p` one-liner to YAML lint rules, and ships a language server and test
framework.

**Reach for ast-grep over `grep`/`ripgrep` when** the thing you want is
structural: multi-line constructs, "any `console.log` call regardless of
arguments or formatting," or matches that must respect nesting. Meta-variables
(`$VAR`, `$$$`) capture sub-trees that a line-oriented regex cannot express
cleanly (intro doc, above).

**Reach for ast-grep over `sed`/regex when rewriting**, because the rewrite
operates on matched AST nodes and substitutes captured meta-variables, so it
will not corrupt code by matching inside strings/comments the way a blind
regex does (<https://ast-grep.github.io/guide/rewrite-code.html>).

**Do NOT reach for it when:**
- You need semantic / type-aware understanding (rename a symbol respecting
  scope, follow imports, resolve overloads). ast-grep has no type system or
  cross-file symbol table — that is an LSP / compiler-tooling job. The intro
  positions ast-grep against text tools, not against type-aware refactors.
- The target is a trivial literal string. ripgrep is faster and simpler; the
  docs themselves note text tools are "fast but imprecise" — when precision
  is not needed, the speed wins (intro doc).
- The language has no tree-sitter grammar registered (see §2).

Comparable tools the docs name: Semgrep, comby, shisho, gogocode, gritQL
(intro doc). Semgrep is the closest peer; ast-grep is positioned as faster and
lighter-weight, single-binary, no cloud.

## 2. Language support

Per the languages reference
(<https://ast-grep.github.io/reference/languages.html>), ast-grep ships
built-in support for ~31 languages. The full alias table includes:

Bash `bash`; C `c`; C++ `cc/c++/cpp/cxx`; C# `cs/csharp`; CSS `css`; Elixir
`ex/elixir`; Go `go/golang`; Haskell `hs/haskell`; HCL `hcl`; HTML `html`;
Java `java`; JavaScript `javascript/js/jsx`; JSON `json`; Kotlin `kotlin/kt`;
Lua `lua`; Nix `nix`; PHP `php`; Python `py/python`; Ruby `rb/ruby`; Rust
`rs/rust`; Scala `scala`; Solidity `solidity/sol`; Swift `swift`; TypeScript
`ts/typescript`; TSX `tsx`; YAML `yml`.

For the skill's target set:
- **Go, Rust, Python, TypeScript, TSX, Bash — all first-class, built in.**
- **SQL is NOT built in.** It does not appear in the table. Using SQL requires
  the custom-language mechanism: compile a tree-sitter SQL grammar to a shared
  library and register it under `customLanguages` in `sgconfig.yml` with
  `libraryPath`, `extensions`, and `expandoChar`
  (<https://ast-grep.github.io/advanced/custom-language.html>). This is a build
  step (`tree-sitter build --output sql.so`), not a flag. Treat SQL as
  "available only after setup," and note `expandoChar` is needed because `$VAR`
  is not valid SQL syntax.

Note JS/TS vs TSX is a real split: `ts` and `tsx` are distinct languages with
distinct grammars (JSX changes parsing). Pick `tsx` for any file containing
JSX.

**Language selection** has three mechanisms (languages doc):
1. `-l/--lang <alias>` on the CLI (required for stdin / ambiguous input).
2. File extension auto-detection during directory scans.
3. `languageGlobs` in `sgconfig.yml` to map non-standard extensions to a
   language (e.g. `.vue` → html).

## 3. CLI surface

Two main subcommands.

`ast-grep run` — ad-hoc, pattern-driven
(<https://ast-grep.github.io/reference/cli/run.html>):
- `-p, --pattern <PATTERN>` — AST pattern to match.
- `-r, --rewrite <FIX>` — string to replace the matched node.
- `-l, --lang <LANG>` — language of the pattern.
- `--json[=pretty|stream|compact]` — structured output. `stream` emits one
  JSON object per line (good for piping); `compact` is single-line;
  `pretty` is indented.
- `-i, --interactive` — interactive edit session, confirm each change.
- `-U, --update-all` — apply all rewrites without confirmation.
- `--globs <GLOB>` — include/exclude paths, `.gitignore` syntax, `!` to
  exclude.
- `-A/--after`, `-B/--before`, `-C/--context <NUM>` — context lines.
- `--debug-query[=pattern|ast|cst|sexp]` — print how your pattern parsed.
  Essential for debugging a pattern that "should match but doesn't."

`ast-grep scan` — rule-driven
(<https://ast-grep.github.io/reference/cli/scan.html>):
- `-r, --rule <FILE>` — run a single YAML rule file.
- `-c, --config <FILE>` — root config (default `sgconfig.yml`).
- `--inline-rules <TEXT>` — pass a rule as a string.
- `-U/--update-all`, `-i/--interactive`, `--json`, `--globs` — as above.
- `--report-style <rich|medium|short>` — diagnostic format.

Canonical forms:
```sh
# search
ast-grep run -p 'console.log($MSG)' -l ts src/
# rewrite (preview, then apply)
ast-grep run -p 'console.log($MSG)' -r 'logger.info($MSG)' -l ts src/
ast-grep run -p 'console.log($MSG)' -r 'logger.info($MSG)' -l ts -U src/
```

`run -r` does an ad-hoc rewrite directly from the CLI; `scan` applies the
`fix:` field embedded in YAML rules (scan doc). Use `run` for one-offs, `scan`
for a maintained rule set.

## 4. Pattern syntax

From <https://ast-grep.github.io/guide/pattern-syntax.html> and the deep-dive
<https://ast-grep.github.io/advanced/pattern-parse.html>:

- `$VAR` — a wildcard matching **exactly one** named AST node. Names must be
  uppercase A–Z, digits, and underscore (`$META`, `$META_VAR1`). So
  `console.log($GREETING)` matches `console.log('hi')` but not
  `console.log(a, b)` (two nodes).
- `$$$` / `$$$ARGS` — match **zero or more** nodes: arguments, parameters,
  statements. `console.log($$$)` matches any arity.
- `$_` — single anonymous node; meta-vars starting with `_` are **not
  captured** (use when you need "some node here" but won't reference it).
- Reusing a name forces identical matches: `$A == $A` matches `a == a`, not
  `a == b`.
- `$$VAR` — matches **unnamed** nodes (operators, punctuation) which `$VAR`
  skips by default (pattern-parse doc).

**Patterns are code.** They are preprocessed (`$` swapped for a valid char),
parsed by tree-sitter, then the "effective" node is extracted — by default
"the leaf node or the innermost node with more than one child" (pattern-parse
doc). Two consequences:

1. A pattern must be **syntactically valid** in the target language.
   `$LEFT $OP $RIGHT` fails because it is not parseable code; an incomplete
   fragment like `"a": 123` (no braces) cannot parse alone.
2. Some code is **ambiguous** (`a: 123` is a label statement or an object
   pair in JS). Disambiguate with a **pattern object**:
   - `context:` — a larger valid snippet that contains the target.
   - `selector:` — the kind of node within the context to actually match.
   - `strictness:` — matching algorithm (§8).
   Example: match an object key by giving `context: '{ a: 123 }'` plus
   `selector: pair` (pattern-parse doc). When a bare pattern is ambiguous or
   not standalone-valid, reach for a pattern object or `kind:`.

## 5. YAML rules

Minimal shape (<https://ast-grep.github.io/guide/rule-config.html>):
```yaml
id: my-rule
language: TypeScript
rule:
  pattern: console.log($MSG)
```
Optional siblings: `message`, `severity`, `fix`, `note`, `constraints`,
`transform`, `utils`. A node must satisfy **all** fields in a rule object
(rule-config doc).

Rule categories (<https://ast-grep.github.io/reference/rule.html>):
- **Atomic**: `pattern`, `kind` (tree-sitter node type), `regex` (Rust regex
  on node text), `nthChild` (index in parent), `range` (line/col, start
  inclusive / end exclusive).
- **Relational**: `inside`, `has`, `follows`, `precedes`. Each takes a
  sub-rule plus `stopBy` and optional `field`. `stopBy` is `neighbor`
  (default — only the immediate surrounding node), `end` (search to the end
  of the direction), or a rule object (stop when it matches).
- **Composite**: `all` (every sub-rule), `any` (one of), `not` (negation),
  `matches` (reference a named utility rule).

`constraints` — a dictionary keyed by meta-variable name (no `$`) → a rule the
captured node must additionally satisfy (e.g. constrain `$NAME` by `regex`).
`fix` — replacement template using captured meta-vars.
`transform` — derive new meta-vars from captured ones via string ops
(`replace`, `substring`, `convert`, `rewrite`) before substituting into `fix`
(<https://ast-grep.github.io/guide/rewrite/transform.html>). `rewriters` /
the `rewrite` transform apply sub-rules recursively to a captured sub-tree.
`utils` — named reusable sub-rules referenced via `matches`.

Complete rule with a fix
(<https://ast-grep.github.io/guide/rule-config.html>):
```yaml
id: no-await-in-promise-all
language: TypeScript
rule:
  pattern: Promise.all($A)
  has:
    pattern: await $_
    stopBy: end
message: Avoid await inside Promise.all
severity: warning
fix: Promise.all($A)
```

## 6. Project config

`sgconfig.yml` is the project root config, analogous to `tsconfig.json`
(<https://ast-grep.github.io/reference/sgconfig.html>). Top-level keys:
`ruleDirs` (required — directories of YAML rules), `testConfigs` (test dirs),
`utilDirs` (shared utility rules), `languageGlobs` (extension→language map),
`customLanguages` (register tree-sitter grammars, e.g. SQL),
`languageInjections` (experimental). `ast-grep scan` discovers rules by reading
the dirs in `ruleDirs`, resolved relative to the `sgconfig.yml` location
(sgconfig doc).

## 7. Testing rules

`ast-grep test` runs rule tests
(<https://ast-grep.github.io/guide/test-rule.html>). Point `sgconfig.yml` at a
test dir via `testConfigs: [{ testDir: rule-tests }]`. A test file:
```yaml
id: no-await-in-loop
valid:
  - for (let a of b) { console.log(a) }
invalid:
  - async function foo() { for (var bar of baz) await bar; }
```
`valid` snippets must NOT match; `invalid` snippets MUST match. Outcomes:
Validated, Reported (both correct), Noisy (false positive), Missing (false
negative). `--skip-snapshot-tests` checks match/no-match only. Snapshot tests
record exact message + position into a `__snapshots__` directory;
`ast-grep test --update-all` writes/accepts snapshots, `--interactive` reviews
them selectively (test-rule doc).

## 8. Pitfalls & gotchas (highest value for an agent)

- **The pattern must be valid code.** Non-parseable fragments
  (`$LEFT $OP $RIGHT`, dangling `"a": 123`) silently fail to match. Use
  `--debug-query` to see how the pattern parsed, and a pattern object
  (`context`/`selector`) for fragments (pattern-parse doc).
- **Ambiguous single-node patterns** resolve to the wrong kind. When in doubt,
  add `kind:` or a pattern object (pattern-parse doc).
- **Strictness changes what matches.** Default is `smart`: pattern nodes must
  match, but unnamed nodes in the target are skipped. Levels, strict→loose:
  `cst` (match every node), `smart` (default — skip source trivial nodes),
  `ast` (named nodes only), `relaxed` (ast minus comments), `signature`
  (kinds only, text ignored), and `template` (smart but text-only, kinds
  ignored) — `template` exists in installed 0.42.3 (`ast-grep run --help`)
  but is omitted from the published
  <https://ast-grep.github.io/advanced/match-algorithm.html>.
  Surprising over-matching usually means the default `smart` skipped something
  you cared about (e.g. an `async` keyword) — tighten toward `ast`/`cst`.
- **Meta-var naming is strict**: uppercase/digits/underscore, leading `$`.
  Lowercase won't be treated as a meta-var. `$$VAR` matches unnamed nodes;
  `$_X` is non-capturing.
- **`$$$` is non-greedy** — it stops at the next thing the pattern needs to
  match (pattern-parse doc). Don't assume it swallows trailing nodes.
- **Rewrite does not reformat.** It substitutes captured nodes and preserves
  surrounding formatting; it is "indentation sensitive" — the fix template's
  indentation is preserved and re-anchored to context
  (<https://ast-grep.github.io/guide/rewrite-code.html>). It will NOT run
  prettier/gofmt/rustfmt for you. **Always run the language formatter after a
  rewrite.** (Docs give no formatter guidance — this is the agent's job.)
- **`-U/--update-all` is destructive with no undo.** The docs describe no undo
  feature (rewrite doc). ALWAYS preview first (run without `-U`, or use
  `-i`), and commit / be on a clean git tree before applying.
- **`constraints`/`regex` use the Rust regex crate**, not PCRE: "some features
  are not available like arbitrary look-ahead and back references"
  (<https://ast-grep.github.io/guide/rule-config/atomic-rule.html>). Inline
  flags like `(?i)` work; lookbehind/lookahead/backrefs do not.
- **Auto-detect can pick the wrong grammar** — JSX-bearing files parsed as
  `ts` instead of `tsx` will mis-parse. Pass `-l tsx` (or set `languageGlobs`)
  explicitly.
- **`run -r` vs `scan` fix**: `run -r` is an ad-hoc CLI rewrite; `scan` applies
  the `fix:` field from YAML rules and supports `transform`/`rewriters` /
  multi-rule projects. Prefer `scan` once a rewrite is worth keeping.

## 9. Concrete codemod examples

Each is `ast-grep run`; preview without `-U`, then re-run with `-U`, then run
the formatter. Patterns verified against the syntax docs above.

```sh
# Python: print(x) -> logging.info(x)
ast-grep run -p 'print($A)' -r 'logging.info($A)' -l py .

# TypeScript: drop console.log calls (any arity) -> empty statement
ast-grep run -p 'console.log($$$)' -r '' -l ts src/

# TSX: replace a deprecated component name, keeping children
#   (use a YAML rule for attributes; simple element rename shown here)
ast-grep run -p '<OldButton $$$PROPS />' -r '<Button $$$PROPS />' -l tsx src/

# Go: wrap a bare returned error with context
ast-grep run -p 'return err' \
  -r 'return fmt.Errorf("operation failed: %w", err)' -l go .

# Rust: Option/Result .unwrap() -> ? propagation
ast-grep run -p '$E.unwrap()' -r '$E?' -l rust src/

# Bash: backtick command substitution -> $(...)
ast-grep run -p '`$CMD`' -r '$($CMD)' -l bash .
```

**Empirically verified breakage (codex, ast-grep 0.42.3 — see
`codex-critique.md`). Four of these examples are unsafe as canned codemods:**
- `console.log($$$) -> ''` corrupts EXPRESSION contexts, not just statements:
  `() => console.log(a)` becomes `() => `; `x = console.log(a) + 1` becomes
  `x =  + 1`. To delete log *statements* only, scan with a rule whose `rule`
  is `pattern: console.log($$$)` + `inside: { kind: expression_statement }`.
- `<OldButton $$$PROPS />` matches ONLY self-closing JSX. `<OldButton>hi
  </OldButton>` does not match (exit 1) — "keeping children" is false. Element
  rename needs a YAML rule matching `jsx_opening_element` + `jsx_closing_element`.
- `$E.unwrap() -> $E?` fires in plain assignments: `let x = value.unwrap();`
  becomes `let x = value?;` — invalid outside a `Result`/`Option` fn. No type
  awareness (§1); preview-only, review every hunk.
- `` `$CMD` -> $($CMD) `` mangles nested backticks. Don't batch-apply.
- The Go wrap matches *every* bare `return err` and assumes `fmt` imported.

Lesson: a bare `run -p/-r` over-matches by construction. ALWAYS preview
without `-U`, scope real rewrites with `inside`/`kind`/`has` via a `scan` YAML
rule, and run the formatter after. Safe-ish one-liners: the Python
`print->logging` and Go-with-`inside` forms; treat the rest as preview-only.
