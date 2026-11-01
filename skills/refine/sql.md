# Refine lenses — sql

What a refine pass over SQL goes looking for — `.sql` files and SQL text in
`.py` strings. Read WITH the `sql` skill (write-time rules), NEVER instead of
it. Each lens carries the tag refine step 6 reads to pick the agent type.

## Round trips grow with the batch `simplify`

- ALWAYS count the round trips one unit of work makes after the change: a
  `for … await conn.execute`, one `execute` per statement, or a per-item
  `select` before an `insert` is a finding — one statement per record type,
  the batch as one `jsonb` or array parameter (`sql` § Database Modules).
- ALWAYS read each added subquery or CTE against a join or the one function
  that owns the unit; a Python loop that does what one `UPDATE … FROM` does is
  the same finding.

## Style the skill fixes `simplify`

- ALWAYS grep added SQL for column aliases written with `AS`
  (`rg -n '\bAS\b' <added sql>`, CTE heads excepted) and for a `TEXT` column
  holding a closed set of literals (`sql` § Style, § Database Modules).
- ALWAYS check that each added statement sits directly above the one
  function that runs it, not in a block at the top of the module (`sql`
  § Database Modules).
