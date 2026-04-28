---
name: ts
description: TypeScript/Node.js. .ts/.tsx files, package.json, Next.js, React, Bun, Tailwind, class-validator, Playwright, arrow functions.
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

## Design
- Never methods just for grouping; use modules
- Inline single-use one-liners; don't wrap trivial expressions
- No JSDoc on self-explanatory functions
- Library barrel files: `export * from './module'`

## Logging
- NestJS: built-in Logger (wraps Pino)
- Standalone: Pino directly

## Validation
- ALWAYS validate external I/O with class-validator when practical
- NEVER trust external APIs/user input with `as Type`
- Nested objects: `@Type(() => NestedClass)` + `@ValidateNested()`

## Frontend Stack

### React / Next.js
- **Next.js 15** with App Router (`app/` directory)
- Server Components by default, `"use client"` only for interactive leaves

### Package Management
- **Bun** for packages and unit test runner
- **uv** for Python (backend)

### Styling
- ALWAYS Tailwind theme variables, NEVER hardcoded colors
- Theme vars in `globals.css`: `bg-background`, `bg-card`, `text-foreground`, `border-border`
- Fix colors in `globals.css`, not with hardcoded workarounds

### Simple Interactions
- **HTMX** over React for forms, simple AJAX, server-rendered pages

## Testing
- Unit: `*.test.ts` next to code (Bun), E2E: `*.spec.ts` in `playwright/`
- **CRITICAL**: Configure `bunfig.toml` root to exclude Playwright files from Bun:
  ```toml
  [test]
  root = "src"
  ```
- `make e2e`: Playwright, `make smoke`: against running server, `bun test`: unit only
