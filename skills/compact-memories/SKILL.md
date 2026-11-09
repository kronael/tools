---
name: compact-memories
description: "Distill the last completed week or month of the diary into one file beside the day entries, `YYYY-WNN.md` or `YYYY-MM.md`. NOT for today's entry (use diary) or for reading entries (use recall-memories)."
when_to_use: "roll up the week, roll up the month, diary week, diary month, compact the diary, the Stop hook says a rollup is missing, summarise last week, summarise last month"
user-invocable: true
argument-hint: "diary <week|month> [period]"
---

# Compact Memories

The diary has levels: `YYYYMMDD.md` written as the work happens (`diary`),
`YYYY-WNN.md` for an ISO week, `YYYY-MM.md` for a month — one flat directory,
the period in the name. A level is distilled from the level below it with one
method; the Stop hook (`hooks/stop.py`) checks the last completed week and
last calendar month. It names each missing period, including source weeks
required by that month. arizuko runs the same skill on a cron and adds the
`episodes` lens; here the only lens is `diary`.

## Protocol

1. **Period.** ALWAYS select the last completed ISO week or last calendar month
   in UTC unless a third argument names a period. ALWAYS use the level's format,
   such as `/compact-memories diary week 2026-W43`. An explicit period permits
   rewriting an existing file after the source checks below.
2. **Sources.** ALWAYS read from `diary` § Where it lives. For `week`, ALWAYS
   use its `YYYYMMDD.md` files from Monday through Sunday. For `month`, ALWAYS
   use weekly summaries whose Monday falls in that month. A source week spans
   all seven days, including days in the next month. Before any monthly write,
   ALWAYS wait until UTC midnight seven days after the month's final Monday.
   ALWAYS identify every assigned week with daily entries but no weekly summary.
   ALWAYS create those summaries with explicit week periods, oldest first,
   before writing the month. An explicit monthly period NEVER bypasses readiness.
3. **Outcome.** With no sources, ALWAYS write nothing. If the file exists and
   no period was given, ALWAYS write nothing. Otherwise, ALWAYS distill and write
   only after the source checks pass. NEVER scan older periods or refresh existing
   files automatically.
4. **Distill.** Rank by what the owner said or decided. Keep a correction
   verbatim, a deliverable the owner accepted, a blocker. Drop the agent's own
   conclusions, routine runs and dead ends. The file is shorter than its
   sources. The last bullet of `summary:` is the one thing to work on next.
5. **Write.**

```yaml
---
summary: >
  - Shipped the hook test gate (owner confirmed)
  - Corrected: "hooks Python only" (Nov 2)
  - Next: the W44 rollup waits on the Monday measurement
period: '2026-W43'
type: week
store: diary
sources:
  - 20261020.md
  - 20261022.md
aggregated_at: '2026-10-26T03:08:00Z'
---
```

`period` in the level's format, `sources` bare file names, `summary` not
empty, nothing but frontmatter above the closing `---`.
