---
name: data
description: Data collectors and ETL. Scrapers, API integrations, real-time feeds, asyncio, state.json, Redis, deduplication, LeakyBucket, backfill. USE for scrapers, ETL, real-time feeds with state recovery. NOT for one-shot fetches (use cli or sh).
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
