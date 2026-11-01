---
name: mk
description: Makefiles. NOT for shell scripts (use sh) or build configs (use language skill).
when_to_use: "editing Makefile, writing make targets, tool download targets, pattern rules"
user-invocable: false
---

# Make Style

ALWAYS Read `../software/code.md` before the first edit — it owns naming,
comments, design and the boring-code rules. Below are Make-specific additions.

## Indirection has a much higher bar in Make than in code

Make has its own escaping rules (`$$` for shell `$`, `$$$$` inside `define`), its own
expansion phases (immediate vs deferred), and its own caching model (file mtime vs
.PHONY). Each layer of indirection (macros, eval, computed targets) interacts with
those rules and turns into hard-to-read symbols.

Repeat yourself before reaching for indirection. Three near-identical 4-line recipes
are clearer than one 4-line macro called three times.

Direct rule of thumb: if the indirection requires `$$$$` to work, it's too clever.

A Makefile that builds 1-3 files names them in plain rules: NEVER generic
per-host or per-target machinery (`foreach`, computed targets, a host variable)
for that few.

## N similar targets — per-target variables + one pattern rule

This is the idiomatic Make answer. Each target carries its own URL, SHA, EXTRACT
command via target-specific variables. A single recipe consumes them.

```
$(TOOL_A): URL := https://example.com/a.tgz
$(TOOL_A): SHA := abc123...
$(TOOL_A): EXTRACT = tar -xzf "$$t" -C $(CURDIR)/.hooks a

$(TOOL_B): URL := https://example.com/b.tgz
$(TOOL_B): SHA := def456...
$(TOOL_B): EXTRACT = tar -xzf "$$t" -C $(CURDIR)/.hooks --strip-components=1 b

$(TOOLS):
	@t=$$(mktemp); curl -sL "$(URL)" -o "$$t"; \
		echo "$(SHA)  $$t" | sha256sum -c --quiet; \
		$(EXTRACT); rm -f "$$t"
```

NOT this:

```
define DOWNLOAD
	@t=$$$$(mktemp); curl -sL "$(1)" -o "$$$$t"; ...
endef

$(TOOL_A): ; $(call DOWNLOAD,https://...,abc...,...)
```

`$$$$` is the giveaway — you've gone too far.

## Assignment

- `:=` immediate expansion — default choice. Value frozen when the line is read.
- `=` recursive — defer expansion until the variable is used. Use when value contains
  `$$t` or other shell vars that must survive into the recipe unexpanded.
- Mixing `:=` and `=` across per-target vars is fine and expected.

## Generated files

- ALWAYS make a file the build generates a file target named by its path, with
  the sources it is built from as prerequisites:
  `api/openapi.json: api/app.py $(wildcard api/handlers/*.py)`. NEVER a phony
  name for it (`make openapi`): `make <path>` says what it writes, and the
  mtime check skips a file that is up to date.
- ALWAYS write the target through a temporary file in its recipe
  (`... > $@.tmp && mv $@.tmp $@`), so a failed run leaves no partial file
  that looks up to date.

## Tool downloads

- ALWAYS pin SHA256 alongside URL.
- Verify with `sha256sum -c --quiet` before extracting.
- A downloaded tool is a generated file (§ Generated files): its file target
  (e.g. `.hooks/kustomize`) skips the download when it exists.

## Canonical phony targets

| Target      | Purpose                                      |
|-------------|----------------------------------------------|
| `prepare`   | Install all deps (dev + runtime)             |
| `check`     | Lint + format check (ruff or equivalent)     |
| `right`     | Type check (pyright or equivalent)           |
| `test`      | Fast unit tests                              |
| `integration` | Integration / e2e tests                    |
| `clean`     | Remove build artifacts                       |

CI pipelines call these targets by name — keep them consistent across components.

## .PHONY

- For non-file targets only: `lint`, `test`, `install`, `clean`, etc.
- NEVER `.PHONY` a target that produces a file on disk. It defeats caching.

## No help target

- NEVER a `help` target, a `.DEFAULT_GOAL := help` or `##` descriptions beside
  targets: the target names say what runs, and the README's Commands section
  carries the one-line descriptions (`readme/topology.md` § README.md).
- NEVER regex-collapse runs of spaces in a Makefile — aligned recipe text
  breaks silently. When removing a target, delete only its lines.

## Echo

- ALWAYS let make echo what ran — NEVER `@`-prefix a recipe line beyond the
  few whose echo is noise, such as an `@echo` of a result line.
- Double quotes in `@echo "..."` are correct Make syntax — NEVER convert them
  to single quotes (yamlfmt's single-quote convention applies only to `.yml`).
