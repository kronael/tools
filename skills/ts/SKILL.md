---
name: ts
description: TypeScript/Node.js. NOT for .tsx (use tsx).
when_to_use: editing .ts files or writing TypeScript
---

# TypeScript Style

Requires the `software` skill's `code.md` for shared naming, style, and design
rules. Below are TypeScript-specific additions and deltas.

## Code Style
- ALWAYS use the `function` keyword for top-level functions where possible; arrow functions only for callbacks and inline lambdas
- Adhere to `gst` lint rules; match existing style when changing code
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
- NEVER JSDoc on self-explanatory functions
- Library barrel files: `export * from './module'`

## Logging
- NestJS: built-in Logger (wraps Pino)
- Standalone: Pino directly

## Validation
- ALWAYS validate external I/O with class-validator when practical
- NEVER trust external APIs/user input with `as Type`
- Nested objects: `@Type(() => NestedClass)` + `@ValidateNested()`

## Testing
- ALWAYS a JSDoc block above every `test(...)` / `it(...)` call: what it
  does, what preconditions it assumes, what it verifies — one sentence per
  point. (The "NEVER JSDoc self-explanatory functions" rule does NOT apply
  to test cases — a test's intent and preconditions are never self-evident
  from its body.)
- Unit: `*.test.ts` next to code (Bun), E2E: `*.spec.ts` in `playwright/`
- **CRITICAL**: Configure `bunfig.toml` root to exclude Playwright files from Bun:
  ```toml
  [test]
  root = "src"
  ```
- `make e2e`: Playwright, `make smoke`: against running server, `bun test`: unit only
