---
name: mk
description: Makefiles. NOT for shell scripts (use sh) or build configs (use language skill).
when_to_use: "editing Makefile, writing make targets, tool download targets, pattern rules"
user-invocable: false
---

# Make Style

ALWAYS read the `software` baseline (`software/code.md`) first for shared naming,
style, and design rules. Below are Make-specific additions.

## Indirection has a much higher bar in Make than in code

Make has its own escaping rules (`$$` for shell `$`, `$$$$` inside `define`), its own
expansion phases (immediate vs deferred), and its own caching model (file mtime vs
.PHONY). Each layer of indirection (macros, eval, computed targets) interacts with
those rules and turns into hard-to-read symbols.

Repeat yourself before reaching for indirection. Three near-identical 4-line recipes
are clearer than one 4-line macro called three times.

Direct rule of thumb: if the indirection requires `$$$$` to work, it's too clever.

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

## Tool downloads

- Always pin SHA256 alongside URL.
- Verify with `sha256sum -c --quiet` before extracting.
- Use a file target (e.g. `.hooks/kustomize`), never `.PHONY`. Make's file-mtime
  cache then naturally skips re-downloads.

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

- For non-file targets only: `help`, `lint`, `test`, `install`, `clean`, etc.
- Never `.PHONY` a target that produces a file on disk. It defeats caching.

## help target

The help target uses `@echo "    target      description"` with aligned
double-quoted strings. **NEVER** regex-collapse multiple spaces in Makefiles
— `re.sub(r'  +', ' ', ...)` or equivalent will silently destroy this
alignment. When removing a target, delete only its lines; never post-process
the whole file.

```makefile
help:
	@echo "Usage:"
	@echo "    prepare      installs dependencies"
	@echo "    right        type check (pyright)"
	@echo "    test         fast unit tests"
```

Double quotes in `@echo "..."` are correct Make syntax — do NOT convert them
to single quotes (yamlfmt single-quote convention applies only to `.yml` files).

## Recipe shell escaping

- `$$` to escape `$` for the shell. `$$(mktemp)` becomes `$(mktemp)` in shell.
- `\` line continuations with `;` between commands. Each unjoined line runs in its
  own shell — variables don't carry across.
- `@` prefix suppresses echo. Use sparingly; usually you want to see what ran.
