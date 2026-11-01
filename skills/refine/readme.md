# Refine lenses — readme

What a refine pass over documentation goes looking for — README, ARCHITECTURE,
`docs/**`, an HTML explainer page. Read WITH the `readme` skill (write-time
rules), NEVER instead of it. Each lens carries the tag refine step 6
reads to pick the agent type.

## Facts drift from the repo `correctness`

- A doc is checked when written; the repo moves on. ALWAYS grep every cited
  test name, symbol, path and count, and check every claim against the newest
  results (`readme/sync.md` § Protocol, step 5). NEVER run a style
  pass alone — it polishes a page that is wrong.

## Generated style `simplify`

- Prose tells are the `humanize` catalogue. A page's structural tells — headers,
  boxes, layout, sources, links, diagrams, contrast — are `writing/page.md`.
- ALWAYS grep the changed docs for history narration — `rg -n -i 'previously|
  used to|no longer|renamed from|as before|backward|legacy|rollback'` — each
  hit is a finding: state what is true now (WISDOM § Documentation).
- ALWAYS weigh a changed doc's length against the feature it describes: a page
  longer than the code path it explains is a finding, cut to the invariants.
  Count prose and tables, never the code excerpts a spec quotes.

## One reader at a time `correctness`

- ALWAYS read the doc set once per reader type, each working as that reader
  would: newcomer, evaluator, one integrator per SDK language, auditor. A
  product bug a reader hits goes to `BUGS.md` (`bugs` skill), NEVER into a
  doc fix that writes around it.
