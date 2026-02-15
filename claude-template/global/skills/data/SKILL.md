---
name: data
description: Data collectors and ETL. Scrapers, API integrations, real-time feeds, asyncio, state.json, Redis, deduplication, LeakyBucket, backfill.
---

# Collector/Data Collection Service

## Testing Philosophy

- ALWAYS test with real API immediately (mental models are always wrong)
- Test after 10 lines of code, not 100
- Each source has main() for live API testing before integration
- Use test_real_api.py patterns for source verification
- MockArticle fixtures for unit tests, validate against live responses

## Collection Architecture

- ALWAYS use asyncio-based architecture for concurrent collection
- Multiple collectors run concurrently in single asyncio loop
- Sources yield articles via async iterators
- NEVER block event loop with synchronous requests (use aiohttp)
- Slow collectors acceptable only if intervals >> request duration

## State Management

- ALWAYS use state files for recovery (state.json)
- Resume from last_processed_slot/id + 1 on restart
- Save state at regular intervals (every 10,000 items)
- Keep state file portable (JSON, not binary)

## Data Source Patterns

**RSS/Feed**: Use feedparser, implement RssFeedSource base class

**REST API**: JsonSource base class, endpoint-specific parsers, test
fixtures from saved responses

**WebSocket**: WebsocketSource base class, implement reconnection with
restart_on_failure decorator

**Blockchain/RPC**: Parallel fetching (10 concurrent), use gRPC when
available

## Error Handling

- ALWAYS use restart_on_failure decorator for crash recovery
- NEVER trust external APIs (retry with exponential backoff)
- Cache-first approach: Try local cache before RPC fallback
- Graceful degradation when sources fail
- ALWAYS implement timeout/rate limits per source
- LeakyBucket for expensive APIs (ChatGPT, etc.)

## Backfill Strategies

- ALWAYS store raw data for backfill capability (compressed JSON/XZ)
- NEVER delete historical data
- ALWAYS implement incremental snapshots (state saves)
- Enable fast restart without full reprocessing
- Start from specific point with CLI flag (-s slot)

## Storage Patterns

**PostgreSQL**: Structured, queryable data with indexes on frequent queries

**Redis**: Fast cache for hot data (MGET <2ms for 100 accounts vs 1-5s RPC)
- Key namespace: schema:, state:, stake:
- Connection pooling with ConnectionManager

**BigQuery**: Historical analysis, time-series queries, data warehouse

**File-based**: Compressed blocks (XZ level 6), offline mode support

## Rate Limiting

- ALWAYS implement per exchange/API rate limiting
- NEVER exceed documented limits
- Track concurrent requests per endpoint
- Backoff strategies: exponential with max retries
- Intentional blocking requests OK when interval >> request time

## Deduplication

- ALWAYS deduplicate by URL/primary key (database insert check)
- ALWAYS use vector similarity for semantic dedup (Weaviate)
- NEVER trust upstream deduplication
- Implementation: URL set + vector embeddings

## Data Validation

- ALWAYS parse and validate against known schemas
- Define types for all API responses
- Use TypeScript/Pydantic for schema validation
- Make all optional fields Option<T> / Optional[T]
- Provide sensible defaults, log warnings for missing fields
- Validate data types before storage, convert units early

## Collection Modes

**Real-time (streaming)**: WebSocket sources for continuous feeds

**Batch/Periodic**: Polling at fixed intervals (funding rates, prices)

**ALWAYS use async/await for both patterns**

## Configuration

- NEVER hardcode secrets or endpoints (use environment variables)
- ALWAYS store configuration in Google Sheets for dynamic updates
- Enables live reconfiguration without restart
- Docker runtime: -v /srv/run:/srv/run for config mount

## Concurrency

- ALWAYS parallelize independent collection tasks
- NEVER share mutable state without locks
- Use DashMap for lock-free reads
- Redis: Atomic operations (INCR, SET NX)
- Database constraints for deduplication, not in-memory locks

## Monitoring

- ALWAYS log progress at regular intervals (every 1000 items)
- Save state frequently (every 10,000 items)
- Log level: INFO for fetch, WARNING for missing fields
- Use built-in logging, Redis MONITOR for debugging

## Integration Patterns

- Cache fallback: Try Redis MGET first, fall back to RPC
- Cache hits: <1ms, misses: 100-500ms per account
- ALWAYS use universal access patterns (Redis over custom gRPC)
- Key namespacing for multi-tenant: stake:, state:, schema:
