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
method; the Stop hook (`hooks/stop.py`) nudges when the last completed period
has sources and no file. arizuko runs the same skill on a cron and adds the
`episodes` lens; here the only lens is `diary`.

## Protocol

1. **Period.** The last fully elapsed unit before now (UTC), never the current
   one: `date -u` and shell math, `date -u -d "<date>" +%G-W%V` for the ISO
   week. A third argument overrides it in the level's format
   (`/compact-memories diary week 2026-W43`), for a backfill; it also
   overwrites an existing file.
2. **Sources.** `week`: the `YYYYMMDD.md` of the week, Monday to Sunday.
   `month`: the `YYYY-W*.md` whose Monday falls in the month. The directory is
   `diary` § Where it lives.
3. **Outcome.** No source: write nothing. The file exists and no period was
   given: write nothing. Else distill and write.
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
