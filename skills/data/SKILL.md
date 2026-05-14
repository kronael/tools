---
name: data
description: Data collectors and ETL. NOT for one-shot fetches (use sh or py).
when_to_use: building a scraper, ETL pipeline, real-time feed, WebSocket data source
---

# Collector/Data Collection

## Testing

- ALWAYS test with real API after 10 lines (mental models are always wrong)
- Each source has main() for live API testing before integration

## Architecture

- asyncio-based, multiple collectors in single loop
- Sources yield articles via async iterators
- NEVER block event loop with synchronous requests

## State Management

- state.json for recovery: resume from last_processed + 1
- Save state every 10,000 items, keep portable (JSON)
- ALWAYS make pipeline writes idempotent (UPSERT by primary key, not INSERT) — retries must not duplicate
- ALWAYS version raw payloads (store source schema_version with data); NEVER drop unknown fields silently — keep in raw blob
- ALWAYS validate required fields + types BEFORE insert (reject to dead-letter, never write partial rows)

## Data Source Patterns

- **RSS**: feedparser, RssFeedSource base
- **REST API**: JsonSource base, test fixtures from saved responses
- **WebSocket**: WebsocketSource base, restart_on_failure decorator
- **Blockchain/RPC**: parallel fetching (10 concurrent), gRPC when available

## Error Handling

- restart_on_failure decorator for crash recovery
- Retry with exponential backoff, NEVER trust external APIs
- Cache-first: local cache before RPC fallback
- LeakyBucket for expensive APIs (ChatGPT, etc.)

## Backfill

- ALWAYS store raw data (compressed JSON/XZ) for backfill
- NEVER delete historical data
- Incremental snapshots, CLI flag (-s slot) for start point

## Storage

- **PostgreSQL**: structured, indexed on frequent queries
- **Redis**: hot data cache (MGET <2ms for 100 accounts vs 1-5s RPC)
  - Key namespace: schema:, state:, stake:
- **BigQuery**: historical analysis, time-series
- **File**: compressed blocks (XZ level 6)

## Deduplication

- URL/primary key (database insert check)
- Vector similarity for semantic dedup (Weaviate)
- NEVER trust upstream deduplication

## Configuration

- NEVER hardcode secrets (env vars)
- Google Sheets for dynamic config (live reconfiguration without restart)

## Concurrency

- ALWAYS parallelize independent tasks
- Database constraints for dedup, not in-memory locks
- Redis atomic ops (INCR, SET NX), DashMap for lock-free reads

## Pipeline (file-based stages)

- Data is numpy/pandas/dataclasses. ALWAYS pure functions in modules. NEVER inheritance for behavior or testability — swap with `monkeypatch`.
- Pipeline = stages of typed files. Each stage owns a directory. Stage N+1 reads stage N. Path = `{batch}/{key_path}/{date}.{pqt|jl}`. Day file = unit of work.
- ALWAYS tidy at ingestion: one row/observation, one col/variable, one table/entity. NEVER re-clean downstream.
- Raw is append-only. ALWAYS rebuild downstream from raw. NEVER UPDATE/DELETE raw.
- Storage is `.jl` or `.pqt`. NEVER CSV, NEVER pickle.
- ALWAYS `df.to_parquet(fn, coerce_timestamps='us', allow_truncated_timestamps=True)`.

## Paths and resume

- ALWAYS one `paths.py` per project. All path builders live there; NEVER hardcode paths elsewhere.
- ALWAYS pair `get_filename` (write) and `parse_filename` (read) in the same module, same strftime format both ways.
- ALWAYS expose `iter_available_*` from the filesystem for resume.
- Loader = path in, DataFrame out. NEVER clean in loaders — that's ingestion.
- Filesystem is pipeline state. NEVER track pipeline progress in state.json. ALWAYS gate work on output existence; continue day-loops past per-day failures.
- `state.json` is for collector resume only (live-feed cursor), distinct from pipeline-stage resume.
