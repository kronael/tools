---
name: sql
description: SQL queries and schemas. USE when editing .sql files or writing SQL. JOIN USING, column aliases without AS, migrations, schema changes. NOT for ORM-only code with no raw SQL (use the host language skill).
---

# SQL

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
- Multiple: one per line, indented 2 spaces under keyword

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
- `update` does upsert when logic requires it
- Deviate only for multi-op patterns (e.g. `get_or_create`)
- `$1, $2` for simple queries (1-3 params), `sql()` helper for dicts/inserts

## Migrations
- User adds indexes (remind, don't add yourself)
- One migration per change, never modify existing
- Wrap in `DO $migration$ BEGIN ... END; $migration$;` with version check
- Stored procedure params: `_param` suffix, locals: `_var` suffix
- Dynamic SQL: `format()` with `%I` (identifiers), `%s` (values)
