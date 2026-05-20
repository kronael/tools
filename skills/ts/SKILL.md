---
name: ts
description: TypeScript/Node.js. NOT for .tsx (use tsx).
when_to_use: editing .ts files or writing TypeScript
---

# TypeScript Style

## Code Style
- Arrow functions: `const f = (args): result => { ... }`
- Single-letter vars only in trivial one-line callbacks (`arr.find(v => v.id === x)`)
- ALWAYS name types — NEVER inline/anonymous object types (tests exempt)
- Minimize type proliferation: reuse existing types, consolidate similar shapes
- ALWAYS braces for if/for bodies (NEVER single-line without braces)

### Array Operations
- NEVER spread when unnecessary — `filter()`, `map()`, `slice()` already create new arrays
- NEVER `arr.push(...otherArr)` — blows call stack at >65k items. Use `concat` or loop

## Types
- ALWAYS `satisfies T` over `as T` to validate without widening. NEVER `as` to escape a type error.
- ALWAYS brand domain IDs (`type UserId = string & {__brand:'UserId'}`) when two string IDs would otherwise be interchangeable.
- ALWAYS discriminated unions for state, NEVER boolean flag combos. ALWAYS exhaust with `default: const _:never = x` in switches.
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
- Unit: `*.test.ts` next to code (Bun), E2E: `*.spec.ts` in `playwright/`
- **CRITICAL**: Configure `bunfig.toml` root to exclude Playwright files from Bun:
  ```toml
  [test]
  root = "src"
  ```
- `make e2e`: Playwright, `make smoke`: against running server, `bun test`: unit only
