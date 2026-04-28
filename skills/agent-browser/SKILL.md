---
name: agent-browser
description: Browse the web for any task — research topics, read articles, interact with web apps, fill forms, take screenshots, extract data, and test web pages. Use whenever a browser would be useful, not just when the user explicitly asks. USE when a real browser is needed (login flows, screenshots, page interaction). NOT for plain HTTP fetches (use a script directly).
allowed-tools: Bash(agent-browser:*)
---

# Browser Automation with agent-browser

## Core workflow

1. `agent-browser open <url>`
2. `agent-browser snapshot -i` (interactive elements with refs like `@e1`)
3. Interact using refs
4. Re-snapshot after navigation or significant DOM changes

## Commands

```bash
# Navigation
agent-browser open <url> | back | forward | reload | close

# Snapshot
agent-browser snapshot [-i interactive] [-c compact] [-d depth] [-s selector]

# Interact (use @refs from snapshot)
agent-browser click|dblclick|hover @e1
agent-browser fill @e2 "text"          # Clear and type
agent-browser type @e2 "text"          # Type without clearing
agent-browser press Enter
agent-browser check|uncheck @e1
agent-browser select @e1 "value"
agent-browser scroll down 500
agent-browser upload @e1 file.pdf

# Get info
agent-browser get text|html|value @e1
agent-browser get attr @e1 href
agent-browser get title|url
agent-browser get count ".item"

# Screenshot/PDF
agent-browser screenshot [path.png] [--full]
agent-browser pdf output.pdf

# Wait
agent-browser wait @e1 | 2000 | --text "Success" | --url "pattern" | --load networkidle

# Semantic locators (alternative to refs)
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"

# Auth state
agent-browser state save|load auth.json

# Storage
agent-browser cookies [set name value | clear]
agent-browser storage local [set k v]
agent-browser eval "document.title"
```

## Coordinate clicks (canvas, maps, custom renderers)

**Always use `mouse` for coordinate-based clicks** — JS `MouseEvent` has
`isTrusted=false` and is blocked by security-conscious apps. `mouse` sends
real CDP input events with `isTrusted=true`.

```bash
agent-browser mouse move 930 120
agent-browser mouse down
agent-browser mouse up
```
