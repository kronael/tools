---
name: data
description: Data collection patterns. Use when building collectors, scrapers, ETL pipelines, API integrations.
---

# Data Collection

## Architecture
- Asyncio-based, multiple collectors in single loop
- NEVER block event loop (use aiohttp)
- Sources yield via async iterators

## State Management
- State files (state.json) for recovery
- Resume from last_processed + 1
- Save state every 10,000 items

## Error Handling
- restart_on_failure decorator for crash recovery
- Cache-first: local cache before RPC fallback
- LeakyBucket for expensive APIs

## Backfill
- Store raw data compressed (XZ level 6)
- NEVER delete historical data
- CLI flag for start point (-s slot)

## Storage
- Redis: MGET <2ms vs 1-5s RPC, key namespace (schema:, state:)
- File-based: compressed blocks, offline mode support

## Deduplication
- Database primary key checks
- Vector similarity for semantic dedup (Weaviate)

## Config
- Google Sheets for dynamic config, hot-reload
- Docker: -v /srv/run:/srv/run for config mount
