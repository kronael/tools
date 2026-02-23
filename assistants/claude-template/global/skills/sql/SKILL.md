---
name: sql
description: SQL queries and schemas. JOIN USING, column aliases without AS, migrations, schema changes, database design.
---

# SQL

## Style
- No AS for column aliases: `MAX(rtime) max_rtime`
- Use `JOIN ... USING (col)` when joining on same-named columns, not `ON a.col = b.col`
- Prefer direct JOINs over `WHERE x IN (SELECT ...)` subqueries
- `WHERE enabled` not `WHERE enabled = true` (boolean columns are truthy)
- `ON CONFLICT ... DO UPDATE SET` each assignment on new line
- `RETURNING` on its own line
- CTEs: `WITH name AS (...)` stacked before main query

## Embedded SQL Formatting
- SELECT and clause keywords (FROM, WHERE, GROUP BY, etc.) at same indent level
- Single column/condition: same line as keyword
- Multiple columns/conditions: one per line, indented 2 spaces under keyword
- Concatenated strings or triple-quoted — either fine

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
- Function names mirror SQL verbs: `select`, `insert`, `update`, `delete`
- Map directly to SQL operations
- `update` does upsert (ON CONFLICT) when the logic requires it
- Deviate only when it doesn't map to a single SQL op (e.g. `get_or_create`)
- Use `$1, $2` directly for simple queries (1-3 params), `sql()` helper for dicts/inserts

## Migrations
- User adds indexes (remind, don't add yourself)
- One migration per change, never modify existing migrations
- Wrap in `DO $migration$ BEGIN ... END; $migration$;` with version check
- Stored procedure params: `_param` suffix, local variables: `_var` suffix
- Dynamic SQL: `format()` with `%I` (identifiers), `%s` (values)
