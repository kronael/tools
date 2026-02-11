---
name: sql
description: SQL queries and schemas. JOIN USING, column aliases without AS, migrations, schema changes, database design.
---

# SQL

## Style
- No AS for column aliases: `MAX(rtime) max_rtime`
- Use `JOIN ... USING (col)` when joining on same-named columns, not `ON a.col = b.col`
- Prefer direct JOINs over `WHERE x IN (SELECT ...)` subqueries

## Migrations
- User adds indexes (remind, don't add yourself)
- One migration per change, never modify existing migrations
