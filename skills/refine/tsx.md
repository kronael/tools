# Refine lenses — tsx

What a React/Next.js refine pass goes looking for. Read WITH the `tsx` skill
(write-time rules), NEVER instead of it. Each lens carries the tag the refine
skill's `model=` rule reads.

## Effect emission identity `correctness`

- A `useEffect` that emits (analytics, logging, a toast, a mutation) and dedups
  on a hand-written key — `` `${amount}|${winner}|${exclude}` `` — silently
  merges distinct events into one. Every field the author did not list is a
  collision, and a collision is a dropped event, not an error: two different
  user actions produce one row and nothing complains.
- ALWAYS derive the emission identity from the thing that changed — serialize
  the request object the query was keyed by, or use the response object's own
  reference. NEVER hand-list fields.
- ALWAYS grep for a template-literal key built from two or more interpolations
  near a `useRef`; that pair is the shape of the bug.

## Deps are not a gate `correctness`

- A dependency list only decides WHEN an effect re-runs. Whether anything is
  emitted is decided by the ref-held key inside it, so a 16-entry dep list
  gates nothing.
- ALWAYS read the dep list and the emission key as two separate sets and diff
  them. The bugs live in the gap: a value in the deps but not the key (re-runs,
  emits nothing), or in the key but not the deps (stale when it emits).

## React Query response identity `correctness`

- Structural sharing (the default) changes a query's `data` reference only when
  the content actually changed. ALWAYS use `data` identity as the "a new
  response was delivered" signal — a refetch returning identical data is then
  silent for free, with no key to maintain.

## keepPreviousData vs render scope `correctness`

- `placeholderData: keepPreviousData` means that mid-refetch the PREVIOUS
  response is still in hand while other render-scope values (inputs, derived
  params) already hold the NEW context. Pairing them writes a row that
  describes neither state.
- ALWAYS require an `isFetching` guard before an effect emits anything that
  combines query data with other render-scope values.
