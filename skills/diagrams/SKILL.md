---
name: diagrams
description: ASCII architecture and workflow diagrams using Unicode box-drawing chars. NOT for Excalidraw or SVG (use the create skill, diagram mode).
when_to_use: creating component diagrams, flow charts, dependency maps, architecture overviews in plain text
---

# Diagrams

## Toolchain

Draw with Unicode box-drawing chars, pipe through `udfix` to correct junctions:

```
echo '<diagram>' | udfix
```

`udfix` is at `udfix/` in this repo — install with `make install`.

## Characters

```
─ │          straight lines
┌ ┐ └ ┘      corners
├ ┤ ┬ ┴ ┼   junctions (udfix auto-corrects these)
► ◄ ▲ ▼      arrows (directional, not rewritten by udfix)
```

## ALWAYS

- ALWAYS run output through `udfix` before finalising
- ALWAYS use `►` / `◄` / `▲` / `▼` for arrows, not `->` or `<-`
- ALWAYS label boxes with short noun phrases, not verbs
- ALWAYS left-align content — ASCII diagrams look bad centred

## NEVER

- NEVER mix half-width and full-width Unicode in the same diagram
- NEVER draw junctions by hand — let udfix fix them

## Layout pattern

```
┌────────────┐     ┌────────────┐
│  producer  │────►│  consumer  │
└────────────┘     └────────────┘
                         │
                   ┌─────▼──────┐
                   │   store    │
                   └────────────┘
```

Vertical flow: top → bottom. Horizontal: left → right. Data flows with arrows.
