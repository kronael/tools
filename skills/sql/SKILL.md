---
name: sql
description: SQL queries, schemas, migrations and PL/pgSQL functions. NOT for ORM-only code (use go, py, ts, or rs).
when_to_use: "editing .sql files or writing SQL queries; database module, db function signature, batch write, round trips, one call per operation, jsonb_to_recordset, unnest, = ANY; PL/pgSQL function, LANGUAGE sql, stored function, functions schema; migration, DO block, IF NOT EXISTS, migration runner; advisory lock, row lock, FOR UPDATE, ON CONFLICT, deadlock, hash compare"
---

# SQL

ALWAYS Read `../software/code.md` before the first edit — it owns naming,
comments, design and the boring-code rules. Below are SQL-specific additions.

## Style
- No AS for column aliases: `MAX(rtime) max_rtime`
- `JOIN ... USING (col)` not `ON a.col = b.col` when same-named
- Direct JOINs over `WHERE x IN (SELECT ...)` subqueries
- `WHERE enabled` not `WHERE enabled = true`
- `ON CONFLICT ... DO UPDATE SET` each assignment on new line
- `RETURNING` on its own line
- Scalar subqueries: parens on own lines
- CTEs stacked before main query

## Embedded SQL Formatting
- Clause keywords (SELECT, FROM, WHERE, GROUP BY) at same indent level
- Single column/condition: same line as keyword
- Multiple: one per line, indented 2 spaces under keyword — ALWAYS the same for
  a function's parameters and its `RETURNS TABLE` columns: one item per line

```python
# single-line clauses
'SELECT tenant_id'
' FROM subscriptions'
' WHERE expires_at > NOW()'

# multi-line clauses
'SELECT'
'  tenant_id,'
'  COALESCE(SUM(max_slots), 0) total'
' FROM subscriptions'
' WHERE expires_at > NOW()'
' GROUP BY tenant_id'
```

## Database Modules
- ALWAYS store a closed set of values (status, outcome, channel) as `SMALLINT`
  with an `IntEnum` in the code, and pass the enum — NEVER a `TEXT` column of
  string literals such as `'done'`/`'dead'`.
- Function names mirror SQL verbs plus what they return or change: `select_message_url`, `insert_observations`, `update_checked_at`, `delete_finished` — NEVER a bare noun like `url_of` or `sent`
- ALWAYS make one system operation (a commit, a claim, a feed page) ONE
  database call. Count round trips, not statements: one per operation, two or
  three at the outside, a fixed number that does not grow with the batch. The
  operation's statements go into one PL/pgSQL function (§ Functions) that the
  code calls once — NEVER a code function that runs them one `execute` at a
  time, NEVER `executemany` for what one statement can take.
- ALWAYS take and return lists of the program's record types (`list[Document]`
  in, `list[Receipt]` out); a caller without a natural batch passes a list of
  one. NEVER a single-row twin beside the list function.
- ALWAYS pass a batch as one parameter: `jsonb` for heterogeneous records, read
  with `jsonb_to_recordset`; a SQL array for plain keys, read with `= ANY($1)`
  or `unnest` — both travel in asyncpg's binary protocol. NEVER one round trip
  per row.
- ALWAYS put a SQL statement directly above the one function that runs it (or inline when short and used once), NEVER grouped at the top of the module
- `update` does upsert when logic requires it
- Deviate only for an operation function, named for its operation (`commit`, `claim`, `feed_page`)
- `$1, $2` for simple queries (1-3 params), `sql()` helper for dicts/inserts

## Functions
- ALWAYS `LANGUAGE plpgsql` — NEVER `LANGUAGE sql`, even for a one-statement body.
- ALWAYS structure an operation as small named `table_verb` functions
  (`jobs_archive`, `documents_write`, `seqs_number`) that the top function,
  named for the operation (`commit`, `claim`), calls in order.
- Functions are not versioned migrations: ALWAYS their own numbered files in
  the migrations directory, after the versioned ones and without a version
  guard (`100-functions.sql` drops and creates the functions schema,
  `101-...` onward create the functions), so the existing runner re-creates
  them on every start. A changed rule is an edit to the file — NEVER a new
  version, NEVER new runner code.
- Params: `_param` suffix, locals: `_var` suffix
- Dynamic SQL: `format()` with `%I` (identifiers), `%s` (values)

## Migrations
- User adds indexes (remind, don't add yourself)
- One migration per change, never modify existing
- ALWAYS tables only — a function goes in its own file (§ Functions).
- ALWAYS one `DO $migration$ BEGIN ... END; $migration$;` block per file, so
  one transaction: return unless `max(version)` is N-1, change, record N.
- NEVER `IF EXISTS` / `IF NOT EXISTS` on a schema object, nor a catalog query
  standing in for one — ALWAYS create it plainly and let a second creation fail.
- ALWAYS the one runner that applies every numbered file in name order on
  every start; versioned migrations guard themselves, function files do not —
  NEVER a second tool or a runner stage for the functions.

## Concurrency
- NEVER an advisory or global lock for row concurrency — ALWAYS row locks:
  compare inside the write (`ON CONFLICT ... DO UPDATE ... WHERE t.hash IS
  DISTINCT FROM EXCLUDED.hash`, `UPDATE ... WHERE hash = $2`), sort a batch by
  its key before writing, and `SELECT ... FOR UPDATE` only where code must read
  before it decides.
- ALWAYS compute a content hash in the application and compare it in SQL —
  NEVER hash in the statement.
- ALWAYS retry the whole call on a deadlock, a bounded number of times — NEVER
  one statement of it.

## Lints
- No ast-grep pack: ast-grep has no SQL grammar. Enforce the style above with
  sqlfluff or native tooling.
