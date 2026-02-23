# Claude Code Usage Patterns - Raw Data

## Pattern 1: Iterative Debugging with Short Commands
**Frequency**: Very High
**Description**: Users issue extremely short, terse commands like "fix it",
"continue", "do it", "yes", "commit" to drive iterative development. This
creates a rapid back-and-forth flow where Claude makes changes and user
provides quick feedback.
**Example**:
- "fix it" → Claude makes changes → "commit" → "deploy"
- "continue" → "yes" → "good"
**Source**: Both (extremely common in both files)

## Pattern 2: Build-Deploy-Fix Cycle
**Frequency**: High
**Description**: Users repeatedly cycle through building, deploying to
production environments, encountering errors, and fixing them in rapid
succession. Deployment targets are often specific directories like
~/public_html.
**Example**: "build and deploy" → "into public html" → error logs → "fix it"
→ "deploy"
**Source**: Both

## Pattern 3: Memory/Wisdom Recording Pattern
**Frequency**: Medium
**Description**: Users explicitly tell Claude to "memorize" or "remember"
specific facts, conventions, or paths. Often prefixed with # for wisdom
recording (e.g., "#never use threading in python").
**Example**:
- "cpy to ~public html staking rewards ... and memorize it"
- "#never use /tmp use a local tmp"
- "memorize not to coauthor commits"
**Source**: Both

## Pattern 4: Configuration-First Development
**Frequency**: Medium-High
**Description**: Users tune configuration files (TOML, environment configs)
before code changes. Configs specify deployment paths, API keys, feature
flags. Pattern: adjust config → test → adjust again.
**Example**: "tune config so that we quote very aggressively to be able to
measure how much volume we can amas"
**Source**: Both

## Pattern 5: Real Production Data Debugging
**Frequency**: High
**Description**: Users paste actual production logs, error traces, and system
outputs for Claude to analyze. Often from systemd, Docker, or application
logs with timestamps and specific error messages.
**Example**: Pasting multi-line systemd logs with "Nov 15 23:03:09 hel1
solana_unstake_liquidation_bot[4041985]: error: unexpected argument..."
**Source**: Both

## Pattern 6: /init Command for Session Start
**Frequency**: Medium
**Description**: Users invoke "/init" at the beginning of sessions, often
appearing twice consecutively. This appears to be a project/context
initialization command.
**Example**: "/init" followed immediately by another "/init"
**Source**: Both

## Pattern 7: Comparative Analysis Requests
**Frequency**: Medium
**Description**: Users ask Claude to compare current implementation against
reference implementations, often from sibling projects or previous versions.
Pattern: "compare with ../other-project" or "verify against first-version".
**Example**:
- "rather compare the changes you made to signing vs. fisrt-version"
- "study ../auction-bot ... I want you to revew the current code paths 1-by-1"
**Source**: Both

## Pattern 8: Agent-Based Task Decomposition
**Frequency**: Medium
**Description**: Users explicitly request spawning agents for different
aspects of work, particularly for criticism, code review, or parallel tasks.
Uses phrases like "launch an agent", "spawn an agent for each chunk".
**Example**:
- "launcch an agent to show there are bugs in the impl"
- "ok... launcch agents to criticize what we did here. heavily, then
synthesize and address the issues"
**Source**: Local (more prevalent)

## Pattern 9: Minimal Documentation Philosophy
**Frequency**: Medium
**Description**: Users actively resist documentation creation and verbose
outputs. Preferences: "no comments", "no fancy outputs", "dont mention that
the visuas are by d3 etc... its notninteresting".
**Example**:
- "no CMD !" (in Dockerfile)
- "no coments"
- "Cut fluff: describe, don't sell or educate obvious things"
**Source**: Both

## Pattern 10: Integration Test Over Unit Test
**Frequency**: Medium
**Description**: Users explicitly reject trivial/mock tests in favor of
integration and e2e tests. Pattern: ask about tests → reject mocks → demand
real data testing.
**Example**:
- "dont test trivial things, test the whole pipeline"
- "so they dont test anything?" (rejecting mock tests)
**Source**: Both

## Pattern 11: Typo-Laden Commands
**Frequency**: High
**Description**: User messages contain frequent typos, abbreviations, and
grammatical errors, but Claude successfully interprets intent. Shows casual,
rapid input style.
**Example**:
- "wtf why are yoi creating branchea?"
- "remembers youre not testing the creation"
- "shoudnt memlry be just an overlay"
**Source**: Both (very common)

## Pattern 12: Discord Logging Integration
**Frequency**: Low-Medium
**Description**: Projects integrate Discord for operational notifications.
Users tune what gets logged to Discord vs regular logs, focusing on high-value
events only.
**Example**: "balance changes happen fast and the discord logigng does not
make sense... print the message after a timeout of 20s and only print the last
message with the sum"
**Source**: Both

## Pattern 13: Project Renaming and Restructuring
**Frequency**: Medium
**Description**: Users rename projects, binaries, and reorganize structure
mid-development. Pattern: realize naming is wrong → rename everything → update
all references.
**Example**:
- "rename the project to solana-unstake-liquidation-bot"
- "rename the workflow binary to main and the arb binary to cli"
**Source**: Both

## Pattern 14: Multi-Repository Workflows
**Frequency**: Medium
**Description**: Work spans multiple related repositories. Users reference
sibling projects for patterns, configs, or code to replicate. Path references
like ../project-name are common.
**Example**:
- "add it based on ../solana-unstake-auction-bot"
- "study ../auction-bot"
- "use the marinade data and augment by the stakes.csv"
**Source**: Both

## Pattern 15: Dockerfile Optimization Cycles
**Frequency**: Medium
**Description**: Iterative Dockerfile development with focus on multi-stage
builds, minimal images, correct working directories. Users are security-
conscious (reject insecure workarounds).
**Example**:
- "I want security ! . cant you rather use newer debian?"
- "dont do this I want safety!"
- Multi-stage build iterations with specific workdir requirements
**Source**: Both

## Pattern 16: Financial/Trading Bot Development
**Frequency**: Medium-High
**Description**: Many projects involve trading bots, lending bots, liquidation
systems, funding rate arbitrage. Focus on: slippage, APY calculation, market
making, risk management.
**Example**:
- "the sizing formula should be base_size + size_coef * quoted_bps"
- APY calculation debugging for staking rewards
- Liquidation price calculations
**Source**: Both

## Pattern 17: Data Pipeline with CSV/JSON
**Frequency**: Medium
**Description**: Workflows involve downloading data to CSV, processing,
generating reports (often PDFs), and presenting via web interfaces. Queue-
based processing for async operations.
**Example**:
- "download the csv and build a pdf report"
- Queue states: pending → generating-csv → generating-pdf → done
- "/tmp/capture.png" for visual data analysis
**Source**: Both

## Pattern 18: Criticism-Driven Development
**Frequency**: Medium
**Description**: Users explicitly request Claude to criticize code, find bugs,
or evaluate architectural decisions. Often followed by "synthesize and address
the issues".
**Example**:
- "criticize the agnets in lue of the buildin agents... which are utterly
useless?"
- "I like the tool, but try running it with config and config.2 and criticize
its accuracy"
**Source**: Both

## Pattern 19: Schema Evolution and Data Format Changes
**Frequency**: Medium
**Description**: Users work through API schema changes, data format migrations,
and DTO transformations. Pattern: upstream changes → update DTOs → fix
transformations → update filters/groupers.
**Example**:
- "the upstream api changed. 1) you dont need to call crawl before every
report call; 2) you won't normally get 429..."
- Grouping data into buckets with time_from/time_to transformations
**Source**: Both

## Pattern 20: Unix Philosophy and Simplicity
**Frequency**: High
**Description**: Strong preference for Unix-style simplicity: short names, no
redundancy, plain functions over classes, direct feedback, simple relative
paths from fixed working directories.
**Example**:
- "Shorter is better"
- "Old Unix style simplicity"
- "use plain functions organized in modules"
- "never use basename $0, __dirname"
**Source**: Both (aligns with CLAUDE.md conventions)

---

## Meta-Patterns

### Communication Style
- Extremely terse, command-like instructions
- Heavy use of ellipsis (...)
- Questions often rhetorical or checking Claude's understanding
- Frequent profanity when frustrated ("wtf", "fuck")
- Mix of technical precision and casual language

### Development Velocity
- Very rapid iteration cycles (seconds between commands)
- Production deployments happen multiple times per session
- Little time for planning - "figure it out as we go" approach
- Immediate production testing rather than staging

### Tool Ecosystem
- Heavy Docker usage (multi-stage builds, Debian/bookworm images)
- Rust and Python dominated (with some TypeScript/Node)
- systemd for service management
- TOML for configuration
- Make for build orchestration
- Git with specific commit message conventions

### Domain Focus
- Blockchain/crypto (Solana, staking, liquidations, LST protocols)
- Financial systems (lending, trading, arbitrage, funding rates)
- Data collection and reporting systems
- Automation and bot development
