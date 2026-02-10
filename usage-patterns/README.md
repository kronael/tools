# Claude Code Usage Patterns

Extracted from 1.3MB of production logs analyzing 57 projects.

## TL;DR - Start Here

**Top 3 to try immediately**:
1. **Iterative Debugging** (Pattern 1) - Use single-word commands like "fix
   it", "continue", "commit" for rapid feedback loops
2. **Criticism-Driven Development** (Pattern 6) - Request harsh criticism
   before every PR to find bugs early
3. **Integration Tests First** (Pattern 5) - Skip elaborate mocks, test with
   real data flows

**Quick Priority Guide**:
- Patterns 1-6 (scores 9-10/10): High impact, broad applicability, immediate
  adoption
- Patterns 7-12 (scores 7-8/10): Valuable but may need context-specific
  adaptation

All patterns are ordered by **usefulness priority** based on: actionability,
applicability, impact, evidence strength, and safety.

---

## Pattern 1: Iterative Debugging with Short Commands

**Usefulness Score: 10/10**

### The Pattern
Treat Claude as a pair programmer using extremely short commands: "fix it",
"continue", "do it", "yes", "commit". Create rapid back-and-forth flow where
Claude makes changes and you provide instant feedback.

### Why This Works
Compresses what would take minutes of detailed typing into seconds. Works for
any language, framework, or problem domain. Maximum development velocity
through minimal friction.

### Evidence from Logs
"Users issue extremely short, terse commands like 'fix it', 'continue', 'do
it', 'yes', 'commit' to drive iterative development. This creates a rapid
back-and-forth flow where Claude makes changes and user provides quick
feedback."

### How To Adopt
Stop writing detailed commands after Claude makes a change. Use:
- "fix it" when tests fail
- "continue" when approach is correct
- "commit" when done
- "yes" to confirm suggestions

Measure your time to completion on a typical bug fix before and after.

---

## Pattern 2: Real Production Data Debugging

**Usefulness Score: 9/10**

### The Pattern
Paste actual production logs, error traces, and system outputs directly into
Claude for analysis. Use real data from systemd, Docker, application logs with
timestamps and specific error messages.

### Why This Works
Eliminates the guessing game of reproducing issues. Claude can analyze real
error traces, timestamps, and system outputs to pinpoint root causes
immediately. Time savings are massive compared to synthetic reproduction
attempts.

**Risk**: Potential data exposure. Always redact sensitive information first.

### Evidence from Logs
"Users paste actual production logs, error traces, and system outputs for
Claude to analyze. Often from systemd, Docker, or application logs with
timestamps and specific error messages."

### How To Adopt
Next time production breaks:
1. Copy error logs directly (redact sensitive data first)
2. Include context: timestamps, system state, recent changes
3. Ask Claude to analyze root cause
4. Compare time spent vs. local reproduction attempts

---

## Pattern 3: Configuration-First Development

**Usefulness Score: 9/10**

### The Pattern
Tune configuration files (TOML, environment configs) before writing code.
Configs specify deployment paths, API keys, feature flags. Pattern: adjust
config → test → adjust again.

### Why This Works
Forces thinking about architecture and deployment early. Prevents hardcoding
values and retrofitting config later. Particularly valuable for systems with
multiple deployment environments or feature flags.

### Evidence from Logs
"Users tune configuration files (TOML, environment configs) before code
changes. Configs specify deployment paths, API keys, feature flags. Pattern:
adjust config → test → adjust again."

### How To Adopt
On your next feature:
1. Create config structure first with all tuneable parameters (TOML/YAML)
2. Write code that reads these values
3. Test by adjusting config only, not code
4. This forces cleaner separation of concerns

---

## Pattern 4: Comparative Analysis Requests

**Usefulness Score: 9/10**

### The Pattern
Explicitly ask Claude to compare current implementation against reference
implementations from sibling projects or previous versions. Pattern: "compare
with ../other-project" or "verify against first-version".

### Why This Works
Prevents reinventing solutions and catches subtle bugs. Particularly powerful
in multi-project environments where patterns should be consistent. Saves hours
of manual diff review.

### Evidence from Logs
"Users ask Claude to compare current implementation against reference
implementations, often from sibling projects or previous versions. Pattern:
'compare with ../other-project' or 'verify against first-version'."

### How To Adopt
Before finishing any feature:
1. Identify similar implementation (sibling project, previous version,
   reference code)
2. Ask Claude: "Compare my implementation with ../reference-project and
   identify any differences in error handling, edge cases, or architecture"
3. Address discrepancies or document intentional divergence

---

## Pattern 5: Integration Tests Over Unit Tests

**Usefulness Score: 9/10**

### The Pattern
Explicitly reject trivial/mock tests in favor of integration and e2e tests.
Ask about tests → reject mocks → demand real data testing. "Don't test trivial
things, test the whole pipeline."

### Why This Works
Eliminates time wasted on elaborate mock setups that provide false confidence.
Integration tests catch real issues with actual data flows, API contracts, and
database interactions. Bug detection rate is dramatically higher.

**Trade-off**: Slower tests (60-120s vs. <5s), but worth it for confidence.

### Evidence from Logs
"Users explicitly reject trivial/mock tests in favor of integration and e2e
tests. Pattern: ask about tests → reject mocks → demand real data testing.
'dont test trivial things, test the whole pipeline'"

### How To Adopt
Tomorrow:
1. Identify one heavily-mocked unit test suite
2. Replace with single integration test using real database/API instances (in
   test mode)
3. Measure bug detection rate over next sprint
4. Separate fast unit tests (`make test`) from slow integration (`make smoke`)

---

## Pattern 6: Criticism-Driven Development

**Usefulness Score: 9/10**

### The Pattern
Explicitly request Claude to criticize code, find bugs, or evaluate
architectural decisions. Often followed by "synthesize and address the
issues". Example: "Launch agents to criticize what we did here. Heavily, then
synthesize and address the issues."

### Why This Works
Activates Claude's analytical capabilities to find bugs, architectural flaws,
and edge cases before code reaches production. Creates built-in review cycle.
Catches issues that manual review often misses. No social cost - AI doesn't
have feelings.

### Evidence from Logs
"Users explicitly request Claude to criticize code, find bugs, or evaluate
architectural decisions. Often followed by 'synthesize and address the
issues'. 'launcch agents to criticize what we did here. heavily, then
synthesize and address the issues'"

### How To Adopt
After completing any non-trivial implementation:
1. Ask Claude: "Criticize this implementation heavily. Find bugs, edge cases,
   and architectural problems."
2. Request: "Synthesize the top 3 issues and propose fixes"
3. Do this before opening a PR
4. Track how many production bugs this catches

---

## Pattern 7: Memory/Wisdom Recording

**Usefulness Score: 8/10**

### The Pattern
Explicitly tell Claude to "memorize" or "remember" specific facts, conventions,
or paths. Often prefixed with # for wisdom recording (e.g., "#never use
threading in python"). Example: "cpy to ~public html staking rewards ... and
memorize it".

### Why This Works
Prevents repeated corrections and maintains consistency across sessions.
Particularly valuable for team-specific conventions that differ from common
practices. Creates searchable patterns in wisdom files.

### Evidence from Logs
"Users explicitly tell Claude to 'memorize' or 'remember' specific facts,
conventions, or paths. Often prefixed with # for wisdom recording (e.g.,
'#never use threading in python'). 'cpy to ~public html staking rewards ...
and memorize it'"

### How To Adopt
Next time you correct Claude on a project-specific convention:
1. Prefix with # and say "memorize this"
2. Examples:
   - "#never use /tmp, always use ./tmp in project root"
   - "#memorize deployment path is ~/public_html/staking-rewards"
   - "#never use threading in Python, always use asyncio"
3. Review wisdom files periodically to ensure patterns persist

---

## Pattern 8: Agent-Based Task Decomposition

**Usefulness Score: 8/10**

### The Pattern
Spawn separate agents for criticism, review, or parallel tasks. Uses phrases
like "launch an agent", "spawn an agent for each chunk". Example: "Launch an
agent to show there are bugs in the impl".

### Why This Works
Enables concurrent analysis instead of sequential "do X then Y". Particularly
powerful for code review and multi-faceted analysis tasks. Can work different
angles simultaneously.

### Evidence from Logs
"Users explicitly request spawning agents for different aspects of work,
particularly for criticism, code review, or parallel tasks. Uses phrases like
'launch an agent', 'spawn an agent for each chunk'. 'launcch an agent to show
there are bugs in the impl'"

### How To Adopt
Next time you need multi-angle analysis:
1. Say: "Launch 3 agents: one to review security, one for performance
   bottlenecks, one for correctness"
2. Wait for all agents to complete
3. "Synthesize findings and prioritize top issues"
4. Compare time to sequential analysis

---

## Pattern 9: Multi-Repository Workflows

**Usefulness Score: 8/10**

### The Pattern
Reference sibling projects for patterns, configs, or code to replicate. Path
references like ../project-name are common. Example: "Add it based on
../solana-unstake-auction-bot", "Study ../auction-bot".

### Why This Works
Prevents inconsistency across related codebases. Enables rapid pattern
sharing. Particularly valuable in microservice architectures or monorepo-
adjacent structures where multiple repos share conventions.

### Evidence from Logs
"Work spans multiple related repositories. Users reference sibling projects
for patterns, configs, or code to replicate. Path references like
../project-name are common. 'add it based on
../solana-unstake-auction-bot' 'study ../auction-bot'"

### How To Adopt
When starting a new service/component:
1. Identify most similar existing project in sibling directory
2. Tell Claude: "Study ../similar-service and replicate its error handling,
   logging, and config patterns here"
3. Ensure structural consistency across repos
4. Document divergence when intentional

---

## Pattern 10: Minimal Documentation Philosophy

**Usefulness Score: 7/10**

### The Pattern
Actively resist documentation creation and verbose outputs. Preferences: "no
comments", "no fancy outputs", "don't mention that the visuals are by d3
etc... it's not interesting". "Cut fluff: describe, don't sell or educate
obvious things."

### Why This Works
Reduces maintenance burden and forces code to be self-explanatory. Saves time
and prevents outdated docs. However, requires discipline to maintain code
clarity through naming and structure.

### Evidence from Logs
"Users actively resist documentation creation and verbose outputs. Preferences:
'no comments', 'no fancy outputs', 'dont mention that the visuas are by d3
etc... its notninteresting'. 'Cut fluff: describe, don't sell or educate
obvious things'"

### How To Adopt
Tomorrow:
1. Remove all comments from one module that explain "what" (obvious from code)
2. Keep only comments explaining "why" (business logic, non-obvious decisions)
3. Test if code is still understandable
4. If not, improve naming instead of adding comments

---

## Pattern 11: Project Renaming and Restructuring

**Usefulness Score: 7/10**

### The Pattern
Early recognition that naming is wrong and immediate wholesale renaming.
Pattern: realize naming is wrong → rename everything → update all references.
Example: "Rename the project to solana-unstake-liquidation-bot", "Rename the
workflow binary to main and the arb binary to cli".

### Why This Works
Prevents months of confusion and tech debt. Faster to execute early than to
live with bad naming or rename later when dependencies are vast.

### Evidence from Logs
"Users rename projects, binaries, and reorganize structure mid-development.
Pattern: realize naming is wrong → rename everything → update all references.
'rename the project to solana-unstake-liquidation-bot' 'rename the workflow
binary to main and the arb binary to cli'"

### How To Adopt
On your current project:
1. Critically evaluate all naming (project, binaries, key modules)
2. If anything feels misleading or verbose, rename it NOW while impact is
   minimal
3. Use Claude to "rename X to Y everywhere and update all references"
4. Commit separately from feature work

---

## Pattern 12: Schema Evolution and Data Format Changes

**Usefulness Score: 7/10**

### The Pattern
Systematic approach to API schema changes. Pattern: upstream changes → update
DTOs → fix transformations → update filters/groupers. Example: "The upstream
api changed. 1) you don't need to call crawl before every report call; 2) you
won't normally get 429..."

### Why This Works
Provides checklist for handling inevitable API evolution. Prevents cascading
breakage. Particularly valuable for systems integrating third-party APIs.

### Evidence from Logs
"Users work through API schema changes, data format migrations, and DTO
transformations. Pattern: upstream changes → update DTOs → fix transformations
→ update filters/groupers. 'the upstream api changed. 1) you dont need to call
crawl before every report call; 2) you won't normally get 429...'"

### How To Adopt
Next time an upstream API changes:
1. Update DTOs to match new schema
2. Fix all transformation functions
3. Update filters/groupers
4. Test with real data
5. Track what breaks at each stage to refine your personal checklist

---

## Adoption Strategy

Don't adopt all 12 at once. Suggested progression:

**Week 1**: Patterns 1, 6 (Iterative Debugging + Criticism-Driven)
- Lowest risk, immediate benefit
- Learn rapid feedback loops and ego detachment

**Week 2**: Patterns 2, 5 (Production Data + Integration Tests)
- Builds on rapid iteration skills
- Clear measurable impact

**Week 3**: Patterns 3, 4 (Config-First + Comparative Analysis)
- Improves architecture and consistency
- Prevents common mistakes

**Week 4+**: Patterns 7-12 as context requires
- Project-specific adoption
- Evaluate which fit your workflow

---

## Meta-Pattern: Velocity Over Ceremony

All 12 patterns share a common theme: **optimize for individual velocity at
the expense of coordination mechanisms**.

Trade-offs:
- High velocity for small teams (1-3 developers)
- Reduced ceremony and documentation overhead
- Tight feedback loops more valuable than gates
- Risk mitigation through rapid iteration, not prevention

**When to use these patterns**:
- Solo developer or 2-3 person team
- Tight feedback loops more valuable than coordination
- Can tolerate brief failures (good rollback, monitoring)
- Internal tools or low-stakes systems

**When to avoid**:
- Large teams (>5 developers) need coordination
- Customer-facing products where trust matters
- Regulated industries requiring audit trails
- Junior developers (patterns assume confidence, experience)

---

## Missing Evidence

What we couldn't measure from logs:
- Whether patterns provide actual competitive advantage
- Success rate when others adopt these patterns
- Long-term sustainability (do users abandon after trying?)
- Control group comparison (conventional teams)

**Honest assessment**: This is pattern identification from logs, not rigorous
study. Treat as hypotheses to test, not proven practices. Your mileage may
vary.
