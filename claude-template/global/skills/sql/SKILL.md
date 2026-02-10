---
name: sql
description: SQL patterns. Use when writing SQL queries, migrations, or database schemas.
---

# SQL

## Style
- No AS for column aliases: `MAX(rtime) max_rtime`
- Use `JOIN ... USING (col)` when joining on same-named columns, not `ON a.col = b.col`
- Prefer direct JOINs over `WHERE x IN (SELECT ...)` subqueries

## Migrations
- User adds indexes (remind, don't add yourself)
- One migration per change, never modify existing migrations
