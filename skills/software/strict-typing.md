# Strict typing — un-circumventable config

Settings that stop an LLM (or hurried human) from making code "type-check" by
*weakening the type instead of fixing it*: annotate `Any`/`object`, `cast()`,
`# type: ignore`, `as any`, `!`, or a blanket suppression, and the checker goes
green on a lie. Each setting here turns one such move into an error, so the only
green path is a real type.

Config only — no CI gate / canary / branch-protection here; that is
orchestration and lives elsewhere.

`Any` is not a type, it is the *absence* of type-checking; a tool that permits
it cannot be "strict". Stock pyright **cannot** error on `Any` — so the type
engine is **basedpyright** (a drop-in pyright replacement, `uvx basedpyright`)
whose `reportExplicitAny`/`reportAny` ban it, backed by **ruff `ANN401`** as a
second annotation-level guard. No mypy.

---

## Python

Checker matrix — who bans what:

| Tool | Bans `Any`? | Role |
|---|---|---|
| **basedpyright** | yes — `reportExplicitAny` (writing it) + `reportAny` (using it); both absent from stock pyright | the type engine; drop-in pyright replacement (`uvx basedpyright`) |
| **ruff** | yes — `ANN401` bans `Any` in annotations | second guard + the suppression/annotation lints |
| stock pyright | **no** — `reportAny`/`reportExplicitAny` are unrecognized settings | not enough alone; basedpyright is the strict superset |

Proven blind spot: stock pyright `strict` errors on an *unannotated* param
(`reportUnknownParameterType`) but stays silent on an explicit `def f(x: Any)`.
basedpyright's `reportExplicitAny` closes exactly that; ruff `ANN401` double-covers it.

### basedpyright — `pyproject.toml`

Only the non-default lines. basedpyright is a strict superset of pyright —
pyright `strict` already errors on unannotated params and implicit `Optional`
(verified), and basedpyright keeps those — so this file only adds the `Any`-bans
and the suppression kill-switch on top:

```toml
[tool.basedpyright]
pythonVersion = "3.12"
# the Any-bans — set explicitly, they are the point of this file:
reportAny = "error"                       # using an Any value
reportExplicitAny = "error"               # writing `Any` in an annotation
enableTypeIgnoreComments = false          # default true → makes `# type: ignore` a no-op
reportIgnoreCommentWithoutRule = "error"  # `# pyright: ignore` must name a rule code
```

- `reportAny` + `reportExplicitAny` are what stock pyright lacks; they close the
  `def f(x: Any)` blind spot proven above.
- `enableTypeIgnoreComments = false` deletes the `# type: ignore` hatch outright;
  `reportIgnoreCommentWithoutRule` forces the surviving `# pyright: ignore` to
  name a rule, so a suppression can't be blanket.

### ruff — `pyproject.toml`

```toml
[tool.ruff.lint]
select = [
  "F",    # F401 unused import, F811 redefinition, F841 unused var
  "E", "W",
  "ANN",  # flake8-annotations — ANN401 bans `Any` in annotations; ANN001/201/... require them
  "PGH",  # PGH003 blanket `# type: ignore`, PGH004 blanket `# noqa`
  "RUF",  # RUF100 unused `# noqa`, RUF013 implicit Optional (`x: int = None`)
  "B",    # B006 mutable default arg
  "A",    # A001/A002/A003 shadowing a builtin
  "SLF",  # SLF001 private-member access
  "BLE",  # BLE001 blind `except:`
  "TRY",  # swallowed / re-raised-wrong exceptions
  "S",    # S307 eval
]

# NEVER add per-file-ignores for ANN401/PGH003/PGH004/RUF100 — that reopens
# every hatch this page closed. per-file-ignores IS the circumvention.
```

### Python escape hatch → setting that blocks it

| The move | Blocked by |
|---|---|
| annotate `Any` | basedpyright `reportExplicitAny`; ruff `ANN401` |
| *use* an `Any` value (untyped-lib return, `cast(Any, …)`) | basedpyright `reportAny` |
| leave a fn unannotated | basedpyright `reportUnknownParameterType`; ruff `ANN001/201/...` |
| `# type: ignore` | basedpyright `enableTypeIgnoreComments=false`; ruff `PGH003` |
| bare `# pyright: ignore` | basedpyright `reportIgnoreCommentWithoutRule` |
| `# noqa` (bare/blanket) | ruff `PGH004` + `RUF100` |
| implicit `Optional` (`x: T = None`) | basedpyright; ruff `RUF013` |
| `*args`/`**kwargs` typed `Any` | ruff `ANN401` (star-args not exempt by default) |
| no-op `cast()` | basedpyright `reportUnnecessaryCast` |

---

## TypeScript

`strict: true` bans only *implicit* `any`. Writing `any`, `as any`, `!`, `as`,
`@ts-ignore`, `{}` — all legal under bare `strict`. Closing those needs
**typescript-eslint** with **type-aware** linting (`projectService: true`); a
`tsconfig` alone cannot.

### tsconfig.json

```jsonc
{
  "compilerOptions": {
    "strict": true,                          // noImplicitAny, strictNullChecks, strictFunctionTypes,
                                             // strictBindCallApply, strictPropertyInitialization,
                                             // noImplicitThis, useUnknownInCatchVariables, alwaysStrict
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,        // arr[i] is `T | undefined` — kills the #1 unsound index
    "exactOptionalPropertyTypes": true,      // `?:` ≠ `| undefined`
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,
    "verbatimModuleSyntax": true,
    "isolatedModules": true
  }
}
```

### eslint flat config — `eslint.config.js`

```js
import tseslint from 'typescript-eslint';

export default tseslint.config(
  ...tseslint.configs.strictTypeChecked,     // type-aware; already sets most rules below to error
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: { parserOptions: { projectService: true } },
    // strictTypeChecked + stylistic already error on (don't restate): no-explicit-any
    // (`: any`/`as any`), no-unsafe-* (any VALUES from untyped boundaries, e.g. JSON.parse),
    // no-non-null-assertion (`foo!`), no-unnecessary-type-assertion, no-empty-object-type
    // (`{}`), no-unsafe-function-type (`Function`), no-wrapper-object-types, and
    // ban-ts-comment (bans `@ts-ignore`, requires `@ts-expect-error` + description).
    rules: {
      // the one deviation from the presets — presets default to assertionStyle 'as':
      '@typescript-eslint/consistent-type-assertions':   // ban ALL `x as T` reinterpretation
        ['error', { assertionStyle: 'never' }],
    },
  },
);
```

- The `no-unsafe-*` set is the crux: it flags `any` **values** as they flow, so
  an untyped boundary (`JSON.parse`, a `.d.ts`-less import) can't launder junk
  into a typed variable — touching an `any` is an error even when none was
  written.
- `assertionStyle: 'never'` removes `x as T` entirely. Relax to
  `{ assertionStyle: 'as', objectLiteralTypeAssertions: 'never' }` only if the
  codebase genuinely needs `as const` / DOM casts; `never` is the strong floor.
- `@ts-expect-error` is the only surviving suppression, and it errors once the
  underlying issue is fixed — self-cleaning, unlike the banned `@ts-ignore`.
- Optional: `@eslint-community/eslint-comments` → `no-unlimited-disable` +
  `require-description` bans blanket `/* eslint-disable */`.

### TypeScript escape hatch → rule that blocks it

| The move | Blocked by |
|---|---|
| `: any` / `as any` | `no-explicit-any` |
| launder `any` from an untyped boundary | `no-unsafe-assignment` / `-call` / `-member-access` / `-return` / `-argument` |
| implicit `any` param | tsconfig `noImplicitAny` (in `strict`) |
| `x as T` reinterpret | `consistent-type-assertions: never`; no-op ones `no-unnecessary-type-assertion` |
| `foo!` non-null | `no-non-null-assertion` |
| `{}` / `Function` / `Object` as a type | `no-empty-object-type` / `no-unsafe-function-type` / `no-wrapper-object-types` |
| `@ts-ignore` / `@ts-nocheck` | `ban-ts-comment` (require `@ts-expect-error` + description) |
| unchecked `arr[i]` | tsconfig `noUncheckedIndexedAccess` |
| `?:` treated as always-present | tsconfig `exactOptionalPropertyTypes` |

---

## Residual holes settings cannot close

Honest limits — the model can still, in principle:

1. **Cast to a plausible-but-wrong type.** `cast(User, junk)` (py) survives; only
   *no-op* casts are flagged. TS closes this harder — `assertionStyle: 'never'`
   removes `as` entirely; Python has no equivalent ban on `cast`.
2. **`object` / `unknown` widening.** Legal to annotate but self-limiting: the
   value has no usable members, so any real use fails downstream. No dedicated
   ban needed.
3. **`Any` at an untyped-dependency boundary.** An untyped lib's values arrive as
   `Any`; `reportAny` errors on *using* them, so junk can't flow into typed code.
   The only real fix is stubs (`types-*`) or a typed wrapper — the setting forces
   the fix, it can't invent the types.
