# Contexts

A context is an aspect of the project this change touches, cut so that one
command family can prove everything inside it. It is not a directory and not a
file type — those are how a bucket is *named*, not why it exists.

## Cutting them

- ALWAYS cut by the command that would settle a claim: what resolves a
  reference, what counts occurrences, what deploys, what the type checker
  reads. Two claims settled by the same command belong to one context.
- ALWAYS place every changed path and every harvested claim in exactly one
  context; a path in two contexts is two subs editing one file.
- ≤4. A fifth is a sign the cut followed the tree's layout rather than the
  change's.

## What each sub is handed

Beyond `brief.md`'s four blocks, a context's brief names:

- **its paths** — what changed, and the read-only neighbours carrying the idiom
- **its documents** — every spec, `README`, `ARCHITECTURE.md`, `CLAUDE.md`
  section and prior subagent report that asserts something about this context.
  These are upstream and they are wrong more often than the code: ALWAYS have
  the sub re-measure what they state rather than build on it.
- **its command family** — the one that settles claims here, named explicitly,
  so the sub does not reach for grep by reflex
- **its lenses** — for a code context, the `<skill>.md` files in this directory
  and `defaults.md`; for the document set, the `readme.md` lens and
  the `claims.md` sections that apply; for the rest, those `claims.md` sections

## The recurring ones

Named because they keep producing the same failures, not as a checklist —
derive the real ones from the change.

**Deployment.** Playbooks, roles, host vars, units, Dockerfiles, `cfg/`.
Settled by resolving each path from the handler that actually runs it, never by
grepping the playbook that looks canonical. This is where a hand-written
artifact beside the shared role hides, and where an acceptance grep misses the
one reference that matters.

**The document set.** Specs, `README.md`, `ARCHITECTURE.md`, `CLAUDE.md`,
indices. Settled by measuring the tree now. Every number in it has an owner and
the rest cite it; a spec's own acceptance command is itself a claim to check for
coverage. A document's opening sentence is its least-checked claim — a
verification pass aims commands at the details someone disputed, and the
sentence a reader builds their model from was never disputed. A spec describing
a subsystem the tree does not have is the loudest finding this context returns.

**Data and schema.** Migrations, db modules, listeners, the runner that applies
them. Settled by enumerating what the runner reads, not what the directory
holds.

**The tool or plugin surface.** Registries, allowlists, dispatch chains,
receipt ledgers. Settled by counting the places one addition has to touch —
that number is the extensibility claim, and it is the one worth measuring.

**Code, by language.** The existing `<skill>.md` lenses. One kind of context,
dispatched exactly like the others.

**The commit range.** Subjects, trailers, authorship, branch state, worktrees.
Settled in main context at step 11, never delegated — a sub cannot fix what it
already committed.

## Deriving one for an unfamiliar project

Ask what a reviewer would have to run to disprove the change's boldest
sentence. That command names the context. If no command can disprove it, the
sentence is the finding.
