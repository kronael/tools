# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Themes

Tools are organized by design philosophy tangents.

### Ratpoison (MAX INFLOW)

Optimized for **MAX INFLOW of information**, not outflow or ease of use.

**Ratpoison** is a keyboard-only window manager. Tools in this tangent:
- **Optimized for input speed**: Get information INTO the computer fast
- **Tools come to the terminal**: Stay in your app, don't navigate away
- **Minimal navigation**: Direct command execution, no split across difficult-to-navigate apps
- **Single-purpose**: One tool, one task, easy to invoke
- **Keyboard-driven**: fzf, number keys, single-letter shortcuts
- **No visual cruft**: Minimal UI, no decorations, just function
- **Scriptable**: Composable bash scripts, no fat dependencies

**Tools**: `gt` (git tools)

## Tools Structure

Each tool lives in its own directory with:
```
tool/
├── tool           # Main executable (bash script)
├── Makefile       # install/clean targets
└── README.md      # Usage and examples
```

**Installation pattern**:
- Installs to `~/.local/bin/`
- `make install` - installs the tool
- `make clean` - removes the tool

## gt - Git Tools

Single busybox-style script (`gt/gt`). Symlinks detect
invocation name and dispatch to subcommands.

```bash
gt co [pattern]    # Branch checkout (gco, gto=fetch+checkout)
gt p [branch]      # Push to origin (gtp)
gt r [pattern]     # Rebase -i on origin (gtr=fetch+rebase)
gt install         # Create symlinks in script's directory
```

**Symlinks**: `gco`, `gto` (checkout -u), `gtp`, `gtr` (rebase -u)

**Shared flags**: `-u` fetch first, `-n` dry-run, `?` force fzf

**gt checkout**: fzf fuzzy match, recent branches first (reflog),
strips `origin/`, auto-selects single match.

**gt push**: auto-detects current branch, strips all prefixes,
supports `branch:commit`, forwards git push flags.

**gt rebase**: same branch selection as checkout, runs
`git rebase -i origin/<branch>`.

**Implementation**: helpers at top, flags parsed, then main logic.
Clear sections: # Parse flags, # Select branch, # Execute.

## Coding Philosophy: Write Boring Code

**"Debugging is twice as hard as writing the code. If you write the code as cleverly as possible, you are, by definition, not smart enough to debug it."** - Brian Kernighan

All code follows "boring code" principles:

**Readability > Performance > Cleverness**
- Simple, straightforward logic
- Obvious flow from top to bottom
- Comments mark sections, not complex logic
- If it needs a comment to explain, simplify the code

**Predictable and Consistent**
- Same patterns throughout
- One way to do things, not many
- Consistent naming, formatting, structure
- No surprises, no clever tricks

**Easy to Debug**
- Linear flow, minimal branching
- Clear variable names describe content
- Functions do one thing
- Error messages show what failed and why

**Avoid STUPID code**:
- **S**ingleton abuse
- **T**ight coupling
- **U**ntestability
- **P**remature optimization
- **I**ndescriptive naming
- **D**uplication

## Development

**Adding new tools**:
1. Create `toolname/` directory
2. Add executable script, Makefile, README.md
3. Follow ratpoison principles (keyboard-first, minimal)
4. Follow boring code principles (simple, predictable)
5. Update main README.md

**Bash style**:
- Helper functions at top, main logic at bottom
- Clear section comments: # Parse flags, # Execute
- Use functions for reusable logic
- Pipe-based composition (dedupe, strip, fzf)
- POSIX-compatible where possible
- Short, descriptive function names
- [[ ]] for conditions, { } for grouping
