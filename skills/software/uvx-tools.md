# Distributing Python tools

## Distributable Python tools — single-file uvx scripts when possible

For tools that fit, prefer a **single-file PEP 723 script** with inline
`/// script` metadata. `uvx` runs it with no clone, no install, no entry
points:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click", "httpx"]
# ///
import click

@click.command()
def main(): ...

if __name__ == '__main__':
    main()
```

Run anywhere: `uv run https://example.com/script.py` or
`uvx --from <raw-url>`. No `pyproject.toml`, no Docker, no package
ceremony. Use this whenever a tool fits comfortably in one file —
reach for a package layout only when justified.

### Use a package layout when ANY apply

- multiple modules with cross-imports
- bundled non-Python assets (templates, fixtures)
- own test suite
- shared internal lib with sync seam
- intended for `pip install` / pinning

```toml
[project.scripts]
mytool = "mytool.mytool:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["mytool", "lib"]
```

Run from anywhere off GitHub:
```
uvx --from git+https://github.com/<owner>/<repo> mytool ...
```

- The CLI module name conventionally matches the package name
  (`mypkg/mypkg.py:main`) so `uvx mypkg` lines up cleanly.
- Local dev: `uvx --from . mytool ...` reproduces the github flow.
- Bundle assets inside the package dir — hatchling picks them up via
  `packages = [...]`.

