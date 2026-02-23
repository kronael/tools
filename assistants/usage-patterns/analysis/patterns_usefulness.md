# Usage Pattern Selection - Ordered by Usefulness

## Scoring Summary

| Pattern | Usefulness | Action | Apply | Impact | Evidence | Safety | Notes |
|---------|-----------|--------|-------|--------|----------|--------|-------|
| P1: Iterative Debugging | 10/10 | 3/3 | 3/3 | 2/2 | 1/1 | 1/1 | Universal workflow pattern |
| P5: Real Production Data | 9/10 | 3/3 | 3/3 | 2/2 | 1/1 | 0/1 | High impact but some risk |
| P4: Config-First Dev | 9/10 | 3/3 | 3/3 | 2/2 | 1/1 | 0/1 | Forces better architecture |
| P7: Comparative Analysis | 9/10 | 3/3 | 2/3 | 2/2 | 1/1 | 1/1 | Prevents reinventing wheel |
| P10: Integration Tests | 9/10 | 3/3 | 3/3 | 1/2 | 1/1 | 1/1 | Saves time on mock setup |
| P18: Criticism-Driven | 9/10 | 3/3 | 3/3 | 2/2 | 1/1 | 0/1 | Finds bugs before prod |
| P3: Memory Recording | 8/10 | 3/3 | 2/3 | 2/2 | 1/1 | 0/1 | Project-specific conventions |
| P8: Agent-Based Tasks | 8/10 | 2/3 | 2/3 | 2/2 | 1/1 | 1/1 | Parallel work acceleration |
| P14: Multi-Repo Workflows | 8/10 | 2/3 | 2/3 | 2/2 | 1/1 | 1/1 | Code reuse across projects |
| P9: Minimal Docs | 7/10 | 2/3 | 3/3 | 1/2 | 1/1 | 0/1 | Less maintenance burden |
| P13: Project Renaming | 7/10 | 2/3 | 2/3 | 1/2 | 1/1 | 1/1 | Early naming clarity |
| P19: Schema Evolution | 7/10 | 2/3 | 2/3 | 2/2 | 1/1 | 0/1 | API integration pattern |

## Selected Patterns (ordered by usefulness)

### 1. Iterative Debugging with Short Commands (Score: 10/10)

**Why Most Useful**: This pattern enables maximum development velocity by
treating Claude as a pair programmer. Short commands like "fix it",
"continue", "commit" create rapid feedback loops that compress what would
take minutes of typing into seconds. Works for any programming language,
framework, or problem domain.

**Evidence**: "Users issue extremely short, terse commands like 'fix it',
'continue', 'do it', 'yes', 'commit' to drive iterative development. This
creates a rapid back-and-forth flow where Claude makes changes and user
provides quick feedback."

**Immediate Action**: Tomorrow, stop writing detailed commands. After
Claude makes a change, use single-word commands: "fix it" when tests fail,
"continue" when approach is correct, "commit" when done. Measure your time
to completion on a typical bug fix.

---

### 2. Real Production Data Debugging (Score: 9/10)

**Why Most Useful**: Debugging with actual production logs eliminates the
guessing game of reproducing issues. Claude can analyze real error traces,
timestamps, and system outputs to pinpoint root causes immediately. While
higher risk (potential data exposure), the time savings are massive compared
to synthetic reproduction attempts.

**Evidence**: "Users paste actual production logs, error traces, and system
outputs for Claude to analyze. Often from systemd, Docker, or application
logs with timestamps and specific error messages."

**Immediate Action**: Next time production breaks, copy the error logs
directly into Claude (redact sensitive data first). Include context like
timestamps and system state. Ask Claude to analyze the root cause rather
than trying to reproduce locally.

---

### 3. Configuration-First Development (Score: 9/10)

**Why Most Useful**: Tuning configuration before writing code forces you
to think about architecture and deployment early. This pattern prevents
the common anti-pattern of hardcoding values and retrofitting config later.
Particularly valuable for systems with multiple deployment environments or
feature flags.

**Evidence**: "Users tune configuration files (TOML, environment configs)
before code changes. Configs specify deployment paths, API keys, feature
flags. Pattern: adjust config → test → adjust again."

**Immediate Action**: On your next feature, create the config structure
first with all tuneable parameters in a TOML/YAML file. Write code that
reads these values. Test by adjusting config only, not code. This forces
cleaner separation of concerns.

---

### 4. Comparative Analysis Requests (Score: 9/10)

**Why Most Useful**: Explicitly asking Claude to compare current work
against reference implementations prevents reinventing solutions and catches
subtle bugs. Particularly powerful in multi-project environments where
patterns should be consistent. Saves hours of manual diff review.

**Evidence**: "Users ask Claude to compare current implementation against
reference implementations, often from sibling projects or previous versions.
Pattern: 'compare with ../other-project' or 'verify against first-version'."

**Immediate Action**: Before finishing any feature, identify a similar
implementation (sibling project, previous version, or reference code). Ask
Claude: "Compare my implementation with ../reference-project and identify
any differences in error handling, edge cases, or architecture."

---

### 5. Integration Tests Over Unit Tests (Score: 9/10)

**Why Most Useful**: This pattern eliminates time wasted on elaborate mock
setups that provide false confidence. Integration tests catch real issues
with actual data flows, API contracts, and database interactions. The
trade-off is slower tests, but the bug detection rate is dramatically higher.

**Evidence**: "Users explicitly reject trivial/mock tests in favor of
integration and e2e tests. Pattern: ask about tests → reject mocks → demand
real data testing. 'dont test trivial things, test the whole pipeline'"

**Immediate Action**: Tomorrow, identify one heavily-mocked unit test suite.
Replace it with a single integration test that uses real database/API
instances (in test mode). Measure bug detection rate over the next sprint.

---

### 6. Criticism-Driven Development (Score: 9/10)

**Why Most Useful**: Explicitly requesting criticism activates Claude's
analytical capabilities to find bugs, architectural flaws, and edge cases
before code reaches production. The "criticize then synthesize and address"
pattern creates a built-in review cycle. Catches issues that manual review
often misses.

**Evidence**: "Users explicitly request Claude to criticize code, find bugs,
or evaluate architectural decisions. Often followed by 'synthesize and
address the issues'. 'launcch agents to criticize what we did here. heavily,
then synthesize and address the issues'"

**Immediate Action**: After completing any non-trivial implementation, ask
Claude: "Criticize this implementation heavily. Find bugs, edge cases, and
architectural problems. Then synthesize the top 3 issues and propose fixes."
Do this before opening a PR.

---

### 7. Memory/Wisdom Recording Pattern (Score: 8/10)

**Why Most Useful**: Explicitly telling Claude to "memorize" project
conventions prevents repeated corrections and maintains consistency across
sessions. The # prefix for wisdom recording creates searchable patterns.
Particularly valuable for team-specific conventions that differ from common
practices.

**Evidence**: "Users explicitly tell Claude to 'memorize' or 'remember'
specific facts, conventions, or paths. Often prefixed with # for wisdom
recording (e.g., '#never use threading in python'). 'cpy to ~public html
staking rewards ... and memorize it'"

**Immediate Action**: Next time you correct Claude on a project-specific
convention (paths, naming, tool choices), prefix it with # and say
"memorize this". For example: "#never use /tmp, always use ./tmp in project
root" or "#memorize deployment path is ~/public_html/staking-rewards".

---

### 8. Agent-Based Task Decomposition (Score: 8/10)

**Why Most Useful**: Spawning separate agents for criticism, review, or
parallel tasks accelerates work by enabling concurrent analysis. Instead of
sequential "do X then Y", you can launch multiple agents to work different
angles simultaneously. Particularly powerful for code review and multi-faceted
analysis tasks.

**Evidence**: "Users explicitly request spawning agents for different aspects
of work, particularly for criticism, code review, or parallel tasks. Uses
phrases like 'launch an agent', 'spawn an agent for each chunk'. 'launcch an
agent to show there are bugs in the impl'"

**Immediate Action**: Next time you need multi-angle analysis (security +
performance + correctness), explicitly say: "Launch 3 agents: one to review
security, one for performance bottlenecks, one for correctness. Synthesize
findings." Compare time to sequential analysis.

---

### 9. Multi-Repository Workflows (Score: 8/10)

**Why Most Useful**: Referencing sibling projects for patterns and code
reuse prevents inconsistency across related codebases. The ../project-name
pattern enables rapid pattern sharing. Particularly valuable in microservice
architectures or monorepo-adjacent structures where multiple repos share
conventions.

**Evidence**: "Work spans multiple related repositories. Users reference
sibling projects for patterns, configs, or code to replicate. Path references
like ../project-name are common. 'add it based on
../solana-unstake-auction-bot' 'study ../auction-bot'"

**Immediate Action**: When starting a new service/component, identify the
most similar existing project in a sibling directory. Tell Claude: "Study
../similar-service and replicate its error handling, logging, and config
patterns here." Ensure structural consistency across repos.

---

### 10. Minimal Documentation Philosophy (Score: 7/10)

**Why Most Useful**: Actively resisting documentation creation reduces
maintenance burden and forces code to be self-explanatory. The "no comments",
"no fancy outputs", "cut fluff" approach saves time and prevents outdated
docs. However, requires discipline to maintain code clarity through naming
and structure.

**Evidence**: "Users actively resist documentation creation and verbose
outputs. Preferences: 'no comments', 'no fancy outputs', 'dont mention that
the visuas are by d3 etc... its notninteresting'. 'Cut fluff: describe,
don't sell or educate obvious things'"

**Immediate Action**: Tomorrow, remove all comments from one module that
explain "what" (obvious from code). Keep only comments explaining "why"
(business logic, non-obvious decisions). Test if code is still understandable.
If not, improve naming instead of adding comments.

---

### 11. Project Renaming and Restructuring (Score: 7/10)

**Why Most Useful**: Early recognition that naming is wrong and immediate
wholesale renaming prevents months of confusion and tech debt. The pattern
"realize naming is wrong → rename everything → update all references" is
faster to execute early than to live with bad naming or rename later when
dependencies are vast.

**Evidence**: "Users rename projects, binaries, and reorganize structure
mid-development. Pattern: realize naming is wrong → rename everything →
update all references. 'rename the project to
solana-unstake-liquidation-bot' 'rename the workflow binary to main and
the arb binary to cli'"

**Immediate Action**: On your current project, critically evaluate all
naming (project, binaries, key modules). If anything feels misleading or
verbose, rename it now while impact is minimal. Use Claude to "rename X to
Y everywhere and update all references."

---

### 12. Schema Evolution and Data Format Changes (Score: 7/10)

**Why Most Useful**: Having a systematic approach to API schema changes
prevents cascading breakage. The pattern "upstream changes → update DTOs →
fix transformations → update filters/groupers" provides a checklist for
handling inevitable API evolution. Particularly valuable for systems
integrating third-party APIs.

**Evidence**: "Users work through API schema changes, data format migrations,
and DTO transformations. Pattern: upstream changes → update DTOs → fix
transformations → update filters/groupers. 'the upstream api changed. 1) you
dont need to call crawl before every report call; 2) you won't normally get
429...'"

**Immediate Action**: Next time an upstream API changes, follow this
sequence explicitly with Claude: 1) Update DTOs to match new schema, 2) Fix
all transformation functions, 3) Update filters/groupers, 4) Test with real
data. Track what breaks at each stage to refine your personal checklist.

---

## Patterns NOT Selected (and why)

### Pattern 2: Build-Deploy-Fix Cycle
**Reason**: Too risky. Deploying to production repeatedly while iterating on
fixes can cause outages. Better to use staging environments. Evidence shows
practice but not necessarily good practice.

### Pattern 6: /init Command
**Reason**: Tool-specific pattern with unclear generalizability. Depends on
custom slash command implementation that may not exist in other contexts.

### Pattern 11: Typo-Laden Commands
**Reason**: This is an observation about Claude's robustness, not an
actionable pattern for users to adopt. Users shouldn't intentionally write
typo-laden commands.

### Pattern 12: Discord Logging Integration
**Reason**: Too niche. Only applies if you use Discord for ops notifications.
Low applicability across different project types and organizations.

### Pattern 15: Dockerfile Optimization
**Reason**: Domain-specific (Docker users only). While valuable, doesn't
meet broad applicability criterion. Many projects don't use Docker.

### Pattern 16: Financial/Trading Bot Development
**Reason**: Extremely niche domain. Only applies to financial/crypto
projects. Zero applicability to web apps, CLIs, data pipelines, etc.

### Pattern 17: Data Pipeline with CSV/JSON
**Reason**: Somewhat niche pattern specific to data processing workflows.
While common, doesn't have broad enough applicability compared to top
patterns.

### Pattern 20: Unix Philosophy
**Reason**: Already well-documented in general software wisdom. Not a
discovery from these logs specifically. Evidence shows alignment with
existing philosophy rather than novel pattern.

---

## Usage Notes

The 12 selected patterns are ordered strictly by usefulness score (10→7).
All scored patterns are highly actionable with clear immediate next steps.

Patterns scoring 9-10 should be adopted immediately by most developers.
Patterns scoring 7-8 are valuable but may require more context-specific
adaptation.

Focus on implementing patterns 1-6 first for maximum impact with minimal
risk. These work across nearly all development contexts and provide immediate
productivity gains.
