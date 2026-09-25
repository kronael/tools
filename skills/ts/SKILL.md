---
name: ts
description: TypeScript/Node.js. NOT for .tsx (use tsx).
when_to_use: editing .ts files or writing TypeScript
---

# TypeScript Style

Requires the `software` skill's `code.md` for shared naming, style, comments, and design
rules. Below are TypeScript-specific additions and deltas.

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
- Adhere to `gst` lint rules; match existing style when changing code
- Single-letter vars only in trivial one-line callbacks (`arr.find(v => v.id === x)`)
- ALWAYS name types — NEVER inline/anonymous object types (tests exempt)
- Minimize type proliferation: reuse existing types, consolidate similar shapes
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
- ALWAYS annotate exported function return types; ALWAYS use inference for obvious local functions and callbacks.
- ALWAYS `satisfies T` over `as T` to validate without widening. NEVER `as` to escape a type error.
- ALWAYS brand domain IDs (`type UserId = string & {__brand:'UserId'}`) when two string IDs would otherwise be interchangeable.
- ALWAYS discriminated unions for state, NEVER boolean flag combos. ALWAYS exhaust with `default: const _:never = x` in switches.
- NEVER `any` — use `unknown` and narrow. ALWAYS `import type { T }` for type-only imports.

## Design
- NEVER methods just for grouping — use modules
- ALWAYS inline single-use one-liners; NEVER wrap trivial expressions
- Library barrel files: `export * from './module'`

## Logging
- NestJS: built-in Logger (wraps Pino)
- Standalone: Pino directly

## Validation
- ALWAYS validate external I/O with class-validator when practical
- NEVER trust external APIs/user input with `as Type`
- Nested objects: `@Type(() => NestedClass)` + `@ValidateNested()`

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
- ALWAYS pin the bun runtime with a `.bun-version` file — CI `setup-bun` reads
  it via `bun-version-file`, mise reads it as an idiomatic version file. NEVER
  assume bun auto-switches: the runtime ignores the file, it's a convention.
- An older local bun canNOT parse a lockfileVersion-2 `bun.lock` (written by bun
  ≥1.4): it silently ignores it and rewrites a v1 lockfile. NEVER commit that
  downgrade — `git checkout bun.lock` and `bun upgrade` to match CI's pin.
