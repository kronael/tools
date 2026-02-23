---
name: web
description: Deploy web apps to krons.fiu.wtf
---

# Web App (krons.fiu.wtf)

## Location

```
/srv/data/takopi/web/
```

Mounted into takopi container at `/web/`.

## How It Works

Vite dev server runs inside the container on port 49165.
Nginx proxies `krons.fiu.wtf` -> `hel1v5:49165`.

Vite watches for file changes and auto-reloads — no restart
needed when editing HTML/CSS/JS.

Any directory with an `index.html` becomes a page:
- `/web/intro/index.html` -> https://krons.fiu.wtf/intro/
- `/web/app_name/index.html` -> https://krons.fiu.wtf/app_name/

## Commands

```bash
# full restart (via telegram /refresh command)
# kills vite, entrypoint loop auto-restarts it

# view container logs
docker logs takopi --tail 50
```

No restart needed for file changes — vite picks them up
automatically. Use `/refresh` only if vite gets stuck.

## Adding an App

1. Create `app_name/index.html` in `/web/`
2. Available at https://krons.fiu.wtf/app_name/
3. No restart needed — vite serves it immediately
