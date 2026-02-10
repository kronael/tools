---
name: trader
description: Trading bot patterns. Use when working on trading bots, order management, exchange APIs, position tracking.
---

# Trader

For: Exchange trading bots with paper mode, WebSocket feeds, order management

## State Management
- State machines: Waiting → Active → StopTake → Done
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
