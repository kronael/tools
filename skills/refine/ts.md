# Refine lenses — ts

What a TypeScript refine pass goes looking for. Read WITH the `ts` skill
(write-time rules), NEVER instead of it. A `.tsx` bucket reads this file too.
Each lens carries the tag the refine skill's `model=` rule reads.

## A green test run is not a typecheck `correctness`

- Jest configured with `babel-jest` type-checks nothing — it strips types
  without reading them, so type errors survive a fully green test run. Any
  esbuild/swc-based transform behaves the same way.
- ALWAYS run the project's typecheck as its OWN command (`tsc --noEmit`, or the
  `typecheck` script) at Validate and again at Verify. NEVER accept a passing
  `test` as evidence that types hold.
- ALWAYS check the configured transform before trusting a suite. If the project
  has no typecheck target at all, that absence is itself the finding.
