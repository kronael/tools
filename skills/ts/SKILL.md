---
name: ts
description: TypeScript on Bun or Node.js. NOT for .tsx (use tsx).
when_to_use: editing .ts files, writing TypeScript; new TypeScript project, bun init, bun test, biome.json, tsc --noEmit, tsconfig, package.json, NestJS, Pino
---

# TypeScript Style

ALWAYS Read `../software/code.md` before the first edit — it owns naming,
comments, design and the boring-code rules. Below are TypeScript-specific
additions and deltas.

Read on demand, in this directory:
- `node-cluster.md` — running one CPU-bound Node/NestJS service as N workers
  with `node:cluster`: idle-first dispatch of raw socket handles over IPC,
  pulled Prometheus metrics, worker count from the pod CPU limit.
- `v8-deopt.md` — a hot path that measures slower than it should: proving
  megamorphism with `%HaveSameMap` and `--log-ic`, isolating the phase before
  profiling, and when to stop.
## Runtime and packages
- ALWAYS the newest Bun as package manager, in every JS/TS project: `bun
  install`, `bun.lock` committed, `bunx` for one-offs. NEVER a second
  lockfile (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`) beside it
- **CRITICAL**: `bun run` shells node-shebang bins (`vite`, `tsc`, `eslint`,
  `playwright`) out to the system `node`. ALWAYS set `bunfig.toml`:
  ```toml
  [run]
  bun = true
  ```
  else the project silently depends on whatever `node` is on PATH. Ad hoc:
  `bun --bun run x`, `bunx --bun x`
- Bun RUNS the Node toolchain, it does not replace it — Vite, tsc, eslint and
  Playwright stay Node-ecosystem tools. `bun build` only when Bun's bundler is
  the actual target
- Frontends and script projects are Bun-only: Vite + `bun test` + Playwright,
  `engines.bun`, CI on `oven-sh/setup-bun`. NEVER `.nvmrc`, `engines.node` or
  a Node CI step there
- Backends that deploy on Node: floor at Node 24 (current LTS) wherever it is
  declared — `engines.node: ">=24"`, `.nvmrc` = `24`, CI `node-version: 24`,
  images `node:24-slim` / `node:24-alpine` — same major at every site
- NEVER leave an older major in place because it still builds — bump it with
  the change that touches the file

## Code Style
- ALWAYS use the `function` keyword for top-level functions where possible; arrow functions only for callbacks and inline lambdas
- ALWAYS follow the project's lint config (`biome.json` in a new project); match existing style when changing code
- Single-letter vars only in trivial one-line callbacks (`arr.find(v => v.id === x)`)
- ALWAYS name reusable or domain-significant object types; NEVER name a one-use alias that only hides `Pick` or `Omit` — ALWAYS inline that utility projection
- Minimize type proliferation: reuse existing types, consolidate similar shapes
- NEVER repeat a module or domain name in a type when import context makes it unambiguous — ALWAYS use the shortest precise name
- Single-line guards: omit braces, body indented on next line:
  ```
  if (x)
    return y
  ```
- Multi-line bodies: ALWAYS braces
- NEVER `if (x) { return y }` on one line — either braces+newline or no braces+newline

### Array Operations
- NEVER spread when unnecessary — `filter()`, `map()`, `slice()` already create new arrays
- NEVER `arr.push(...otherArr)` — blows call stack at >65k items. Use `concat` or loop

## Types
- NEVER annotate a return type or a const's type that inference already produces — exported or not. ALWAYS judge every line a change adds or rewrites, including one that predates the change.
- ALWAYS keep the annotation only where inference cannot reach it: recursion, overloads, a type predicate, an empty `[]`, a `let x!` with no initializer, a return type that types the parameters of the function it returns, one value fed by several literals of a discriminated union (one `: T` beats a `satisfies` per site), a value that must widen (`const mode: Mode = "fast"`), and exports under `isolatedDeclarations`.
- ALWAYS swap the annotation on a single literal that must stay narrow for `satisfies T` — `({ phase: "idle" }) satisfies State`, `[...] as const satisfies readonly T[]`. NEVER keep `: T` only to stop one literal widening.
- ALWAYS `satisfies T` over `as T` to validate without widening. NEVER `as` to escape a type error.
- ALWAYS brand domain IDs (`type UserId = string & {__brand:'UserId'}`) when two string IDs would otherwise be interchangeable.
- ALWAYS use discriminated unions for mutually exclusive state; NEVER force a union onto independent results — ALWAYS use a named result object with one field per result
- For fixed-shape result objects, ALWAYS use required `T | undefined` fields; NEVER use optional fields unless key presence carries meaning
- ALWAYS use `value != null` for an intentionally nullish guard; NEVER expand it into separate null and undefined checks
- ALWAYS exhaust discriminated-union switches with `default: const _:never = x`
- NEVER `any` — use `unknown` and narrow. ALWAYS `import type { T }` for type-only imports.

## Design
- NEVER methods just for grouping — use modules
- ALWAYS inline single-use one-liners; NEVER wrap trivial expressions
- Library barrel files: `export * from './module'`

## Performance
- NEVER reason about speed from TS types — V8 erases them and specialises on runtime shapes alone
- ALWAYS read the `software` skill's `js-perf.md` before tuning a hot path: shape discipline, elements kinds, deopts, typed arrays, Wasm/N-API batching

## Logging
- NestJS: built-in Logger (wraps Pino)
- Standalone: Pino directly

## Validation
- ALWAYS validate external I/O with class-validator when practical
- NEVER trust external APIs/user input with `as Type`
- Nested objects: `@Type(() => NestedClass)` + `@ValidateNested()`

## Lints
- Structural rules in `skills/ts/lints/` (ast-grep), proven by `make lints`:
  `ts-no-push-spread`, `ts-no-redundant-spread` (both from Array Operations).
- Native linters own the rest — Biome (`noExplicitAny`), or the eslint an
  existing project already runs, plus tsc. ast-grep only fills the
  kronael-specific gap; NEVER duplicate a Biome or eslint rule here.

## Testing
- ALWAYS a JSDoc block above every `test(...)` / `it(...)` call. Its content
  is `software/testing.md`'s scenario-to-outcome rule — the test exception
  `code.md` names.
- Unit: `*.test.ts` next to code (Bun), E2E: `*.spec.ts` in `playwright/`
- **CRITICAL**: Configure `bunfig.toml` root to exclude Playwright files from Bun:
  ```toml
  [test]
  root = "src"
  ```
- `make e2e`: Playwright, `make smoke`: against running server, `bun test`: unit only

## Tooling
- New project: ALWAYS Bun as runtime, package manager and test runner, Biome
  as linter and formatter, `tsc --noEmit` for types — `bun init`, then
  `bun add -d @biomejs/biome && bunx biome init`. NEVER scaffold on
  npm/pnpm/yarn, eslint, prettier, jest or vitest.
- An existing project keeps its tooling until the owner asks for a migration —
  NEVER switch it as a side effect of another change.
- Targets (`mk` skill names): `prepare` = `bun install`, `check` =
  `bunx biome check .`, `right` = `bunx tsc --noEmit`, `test` = `bun test`.
  The strict `biome.json` and `tsconfig.json`: `software/strict-typing.md`.
- ALWAYS pin the bun runtime with a `.bun-version` file — CI `setup-bun` reads
  it via `bun-version-file`, mise reads it as an idiomatic version file. NEVER
  assume bun auto-switches: the runtime ignores the file, it's a convention.
- An older local bun canNOT parse a lockfileVersion-2 `bun.lock` (written by bun
  ≥1.4): it silently ignores it and rewrites a v1 lockfile. NEVER commit that
  downgrade — `git checkout bun.lock` and `bun upgrade` to match CI's pin.
