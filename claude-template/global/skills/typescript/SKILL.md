---
name: typescript
description: TypeScript development patterns. Use when working on .ts/.tsx files, package.json, or TypeScript/Node.js projects.
---

# TypeScript Style

## Code Style
- Arrow functions: `const f = (args): result => { ... }`
- Avoid `function` keyword where arrow functions suffice
- Match existing code style when changing code
- Prefer named interfaces/types over inline object types
  - Bad: `cache.get<{ status: number; message: string }>()`
  - Good: `interface CachedError { status: number; message: string }` then `cache.get<CachedError>()`
- Minimize type proliferation: reuse existing types, consolidate similar shapes
- Prefer named functions over anonymous for complex return types
  - Bad: `const calc = (): { value: number; equity: number } => ...`
  - Good: `interface CalcResult { value: number; equity: number }` then typed function
- Skip for trivial cases or test code where overhead isn't justified

## Design
- Never use methods just for grouping; use modules instead
- Inline single-use one-liners; don't wrap `x?.map(fn)` in a function
- Avoid IIFEs in object literals; define values beforehand if needed
- No JSDoc on self-explanatory functions (clear name + few lines = no comment)
- Library barrel files (index.ts): use `export * from './module'` for re-exports

## Validation
- ALWAYS validate external I/O with class-validator when practical
- Never trust external APIs, user input, or database results with `as Type`
- Use `validateAndReturn()` from @marinade.finance/cli-common:
  ```typescript
  import { validateAndReturn } from '@marinade.finance/cli-common'
  import { IsString, Type, ValidateNested } from 'class-validator'

  class ApiResponse {
    @IsString()
    status: string
  }

  const data = await response.json()
  const validated = await validateAndReturn(data, ApiResponse)
  ```
- For nested objects use `@Type(() => NestedClass)` and `@ValidateNested()`
- Internal data (already validated) can skip validation
- See TYPESCRIPT_COMMON_REFERENCE.md for available utilities

## Frontend Stack

### React / Next.js
- **Next.js 15** with App Router (`app/` directory)
- **React Server Components** by default
- Use `"use client"` directive for interactive components
- Route groups: `(auth)`, `(dashboard)` for layout organization

### Package Management & Runtime
- **Bun** for package management (`bun install`, `bun add`)
- **Bun** as test runner for unit tests
- **uv** for Python (backend)

### Styling
- **Tailwind CSS** with custom theme system
- **ALWAYS use theme variables** - never hardcode colors (HEX, Tailwind palette, or arbitrary):
  ```tsx
  // Bad - hardcoded colors
  className="bg-[#1C1C1C] text-gray-50 border-gray-800"

  // Good - theme variables
  className="bg-card text-foreground border-border"
  ```
- Theme variables in `globals.css` (HSL values without wrapper):
  - `bg-background`, `bg-card`, `bg-secondary`, `bg-muted`
  - `text-foreground`, `text-muted-foreground`, `text-accent`
  - `border-border`, `text-success`, `text-destructive`
- **If colors look wrong**: Fix theme in `globals.css`, don't use hardcoded workarounds
- Custom theme: `tailwind.config.ts` extends with CSS variables

### Simple Interactions
- **HTMX** for simple interactions without heavy JS
- Prefer HTMX over React for:
  - Form submissions
  - Simple AJAX requests
  - Server-side rendering with minimal client-side logic

## Testing

### Test File Patterns
- Unit tests: `*.test.ts` next to code (Bun)
- E2E tests: `*.spec.ts` in `playwright/` directory (Playwright)
- Python: `test_*.py` (pytest convention)

### Bun Configuration
**CRITICAL**: Bun test picks up `*.spec.ts` files by default (Playwright naming).

Configure `bunfig.toml` to separate unit and E2E tests:
```toml
[test]
root = "src"  # Only scan src/ for tests, not e2e/ or playwright/
```

### Playwright E2E Tests
```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './playwright',
  use: { baseURL: process.env.BASE_URL || 'http://localhost:3004' },
  webServer: {
    command: 'make dev',
    url: 'http://localhost:3004',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

Commands:
- `make e2e` - Run Playwright tests (self-contained, spins up dev server)
- `make smoke` - Run against running server (faster for smoke testing)
- `bun test` - Run unit tests only (Bun test runner)

### Test Object Matching
- Config objects must match target type exactly
