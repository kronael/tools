# TypeScript Common Packages Reference

Quick reference for @marinade.finance/typescript-common monorepo utilities.

## Validation & Parsing

**cli-common**: JSON/YAML parsing with class-validator
```typescript
import { validateAndReturn } from '@marinade.finance/cli-common'
const validated = await validateAndReturn(plainData, MyDto)
```
- `validateAndReturn(data, dto)` - Transform & validate
- `parseAndValidateJson()`, `parseAndValidateYaml()` - Parse string & validate
- Custom decorators: `@IsBigInt()`, `@IsPositiveBigInt()`

## General Utilities

**ts-common**: Core utilities
- String: `truncateAsString()`, `makeStr()`
- JSON: `jsonStringify()` - Handles bigint/Decimal
- Arrays: `chunkArray()`, `batchFetch()`, `batches()`, `asyncBatches()`
- Async: `waitFor()`, `sleep()`, `doWithLock()` - Named mutex
- Math: `minBigInt()`, `maxBigInt()`, `minDecimal()`, `maxDecimal()`
- Errors: `ErrorWithCause`, `HttpError`

## NestJS Integration

**auth-common**: JWT authentication
- `AuthGuard`, `AuthConfig`, `JwtPayload`

**database-common**: PostgreSQL with Slonik
- `DatabaseModule`, `DatabaseService`

**queue-common**: PostgreSQL-backed job queue
- `QueueModule`, `QueueService`

**logging-common**: Pino with Elastic APM
- `getPinoElasticConfigBuilder()`

**telemetry-common**: Prometheus + APM
- Metrics: `HTTP_REQUESTS_TOTAL`, `QUEUE_DEPTH`, etc.
- `@CaptureSpan()`, `setApmContext()`

**ratelimit-common**: Rate limiting
- `@RateLimit()` decorator, `RateLimitGuard`

## Blockchain/Web3

**web3js-kit**: Solana Web3.js v2+
- `@IsAddress()`, `@IsAddressArray()` - Address validation

**web3js-1x**: Solana Web3.js v1.x
- Account/wallet, transactions, stake/vote accounts

**anchor-common**: Anchor Framework
- Extended provider, wallet, validator

**bankrun-utils**, **web3js-1x-testing**: Test utilities

## Testing

**jest-shell-matcher**: Custom Jest matchers for shell testing

---

For detailed API, see package source: `/home/ondra/links/mnde/typescript-common/packages/`
