---
name: trader
description: Trading bots. State machines, paper trading, WebSocket feeds, order management, exchange APIs, position tracking, Google Sheets config. NOT for general data scraping (use data).
when_to_use: exchange APIs, paper trading, trading bots
---

# Trader

## State Management
- State machines: Waiting -> Active -> StopTake -> Done
- Iterate symbols from config, not WebSocket positions
- Track at three levels: global, ledger, open order count

## Paper Trading
- Direction-aware balance checking (BUY=USDT, SELL=base)
- Subtract initial holdings in paper mode

## Exchange API
- Fallback polling when WebSocket stale

## Order Sizing
- Round to exchange precision (floor maker, ceil taker)

## Config
- Google Sheets/database, hot-reload every 10-30s
