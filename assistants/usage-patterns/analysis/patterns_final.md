# Final 4 Counter-Intuitive Usage Patterns

## Selection Methodology (Revised)

### How Critique Changed the Approach

**Original flaw**: Confirmation bias - selected patterns that validated existing
CLAUDE.md wisdom rather than genuinely challenged assumptions.

**New approach**:
1. **Prioritize discomfort** - patterns that feel risky, not safe
2. **Explicit cost accounting** - document downsides, not just benefits
3. **Specificity over meta-patterns** - concrete practices, not vague philosophy
4. **Evidence-based claims** - cite actual log examples, avoid speculation
5. **Novel over known** - prefer undocumented patterns over industry debates

**Scoring revision**:
- Counter-intuitive = How shocked would experienced dev be? (not "does this
  contradict textbooks")
- Usefulness = Concrete adoption steps + measurable impact - documented costs

### Key Changes

Dropped:
- Pattern 1 (Real Production Data Debugging) - conflated "paste logs" with
  "develop against prod"
- Pattern 3 (Short Commands) - natural chat evolution, not transferable wisdom
- Pattern 4 (Memory Recording) - circular logic validating CLAUDE.md itself

Added:
- Pattern 2 (Build-Deploy-Fix Cycle) - genuinely risky production deployment
- Pattern 8 (Agent-Based Task Decomposition) - novel use of AI for criticism
- Pattern 18 (Criticism-Driven Development) - adversarial collaboration

Kept:
- Pattern 10 (Integration Test Over Unit Test) - well-known but well-evidenced

---

## Pattern 1: Build-Deploy-Fix Cycle
**Counter-intuitive Score**: 9/10
**Usefulness Score**: 7/10
**Evidence Quality**: High

### Why Selected

This is the most genuinely shocking pattern. Multiple production deployments
per session, no staging, fix bugs in production. Goes beyond "move fast and
break things" into territory most developers consider reckless.

### What It Contradicts

**Industry standard practice**:
- Staging environments that mirror production
- Multiple approval gates before production deploy
- "Measure twice, cut once" philosophy
- Separate dev/staging/production pipeline
- QA cycles, smoke tests, canary deployments

**What logs show instead**:
```
"build and deploy" → production error → "fix it" → "deploy" → another error
→ "fix it" → "deploy" → works
```

This happens 5-8 times in a single session. Production is the test environment.

### When It Works

**Requirements for safety**:
1. **Single user systems** - you're the only customer, or very small user base
2. **Rollback capability** - can revert instantly (systemd restart, Docker
   rollback)
3. **Monitored closely** - you're watching logs in real-time
4. **Non-critical systems** - trading bots, collectors, internal tools
5. **Stateless or recoverable** - errors don't corrupt permanent state

**Competitive advantage**:
- Fix-to-deploy time: ~60 seconds (vs. hours/days with staging)
- Learning velocity: 10-20 production deploys/day = 10-20 feedback cycles
- No staging drift: production IS the test, so no "works in staging" bugs

### When It Doesn't Work

**Explicit costs and failure modes**:
- **Customer-facing products**: User-visible bugs destroy trust
- **Financial transactions**: Production bugs can cost real money
- **Regulated industries**: Compliance requires audit trails, approvals
- **Team coordination**: Multiple developers deploying simultaneously = chaos
- **Complex state**: Corrupted database/state can't be easily rolled back
- **High availability requirements**: Even brief downtime unacceptable

**Hidden costs**:
- Discord/Slack noise from frequent deploy notifications
- Alert fatigue from production errors
- Potential for catastrophic bugs (no safety net)
- Stress from working in production

**Real risk**: One bad deploy can corrupt data, lose money, or crash critical
service. This pattern assumes you can recover from any mistake - often true
for stateless services, catastrophic for stateful ones.

### How To Adopt

**Step 1: Assess suitability**
- Single developer or very small team? (Yes required)
- Can tolerate brief downtime? (Yes required)
- Stateless or easily recoverable? (Yes required)
- Non-customer-facing? (Recommended)

If all yes, continue. If any no, don't adopt this pattern.

**Step 2: Setup fast rollback**
```bash
# systemd: instant restart
systemctl restart myservice

# Docker: tag previous version
docker run previous-working-tag

# Process: kill and restart
kill $(cat tmp/app.pid) && ./app
```

**Step 3: Monitor in real-time**
- Tail logs during deployment: `journalctl -fu myservice`
- Discord/Slack integration for errors
- Keep previous terminal with logs visible

**Step 4: Practice rollback**
- Deploy broken version intentionally
- Time how long to rollback
- Ensure you can do it under pressure

**Step 5: Start with low-stakes deploys**
- Internal tools first
- Weekend/off-hours initially
- Gradually increase stakes as confidence builds

### Evidence

**From logs - multiple production deploy cycles**:

Session 1 (solana-unstake-liquidation-bot):
1. "build and deploy" → systemd error about arguments
2. "fix it" → build → "deploy" → new error about paths
3. "fix it" → build → "deploy" → works
Total: 3 production deploys in ~5 minutes

Session 2 (staking-report):
1. "deploy into public_html" → 404 error
2. "fix it" → "deploy" → CSS broken
3. "fix it" → "deploy" → works
Total: 3 production deploys

**Deployment targets in logs**:
- ~/public_html (production web server)
- systemd services (production bots)
- /srv/data/project-name (production data paths)

**No mention of**:
- Staging environments
- Test servers
- Local deployment testing
- Approval processes

**Risk acceptance in logs**:
- No hesitation before deploying fixes
- Errors discovered in production, not testing
- "deploy" command follows immediately after "fix it"

---

## Pattern 2: Agent-Based Task Decomposition
**Counter-intuitive Score**: 8/10
**Usefulness Score**: 6/10
**Evidence Quality**: Medium

### Why Selected

Using AI to spawn adversarial AI contradicts single-threaded development.
Genuinely novel - not a known industry pattern. Forces meta-level thinking
about task decomposition.

### What It Contradicts

**Normal development flow**:
- Developer thinks through problems linearly
- Code review happens after implementation
- Criticism comes from other humans
- One task at a time, sequential completion

**This pattern**:
- Explicitly spawn agents for different perspectives
- Use AI to criticize AI's own work
- Parallel work streams managed consciously
- Meta-cognitive approach to development

### When It Works

**Use cases from logs**:

1. **Adversarial code review**:
   "launch an agent to show there are bugs in the impl"
   - Forces finding problems, not confirming success
   - Agent's goal is breaking code, not building it

2. **Multi-aspect analysis**:
   "ok... launch agents to criticize what we did here. heavily, then synthesize
   and address the issues"
   - Different agents for different critique angles
   - Synthesis step combines insights

3. **Parallel exploration**:
   "spawn an agent for each chunk"
   - Decompose large analysis into parallel streams
   - Faster exploration of solution space

**When it provides value**:
- Complex decisions with multiple trade-offs
- Code review without human reviewers available
- Large codebases requiring parallel analysis
- When you need critical perspective, not just confirmation

### When It Doesn't Work

**Explicit limitations**:

1. **Tooling maturity**: Agent spawning UX still evolving, can be clunky
2. **Cognitive overhead**: Managing multiple agent threads adds mental load
3. **Time cost**: Spawning agents takes longer than direct questions
4. **Diminishing returns**: Too many agents = conflicting advice, paralysis
5. **Context fragmentation**: Each agent has partial context, miss big picture

**Cost-benefit calculation**:
- Beneficial: 1-hour task → spawn 2-3 agents for 10-minute speedup
- Wasteful: 5-minute task → spawn agents, spend 15 minutes managing them

**Failure modes**:
- Agent outputs conflict, no clear synthesis
- Agents focus on different aspects, miss integration issues
- Spending more time managing agents than solving problem
- Getting generic criticism instead of specific insights

### How To Adopt

**Step 1: Identify suitable tasks**

Good candidates:
- "Review this architecture and find flaws"
- "Analyze this codebase for security issues"
- "Compare these 3 approaches and find downsides"

Bad candidates:
- "Fix this typo"
- "Add logging here"
- "What does this function do?"

**Step 2: Frame agent objectives clearly**

Bad: "look at this code"
Good: "find bugs in transaction signing logic, assume adversarial conditions"

Bad: "review architecture"
Good: "criticize this architecture for scalability, assume 100x growth"

**Step 3: Limit agent count**
- 1 agent: Deep single-perspective analysis
- 2-3 agents: Multiple perspectives, manageable synthesis
- 4+ agents: Usually too many, diminishing returns

**Step 4: Synthesize explicitly**
Don't just collect agent outputs. Explicitly:
1. Compare findings
2. Resolve conflicts
3. Prioritize issues
4. Create action plan

**Step 5: Measure effectiveness**
Track:
- Time spent managing agents vs. time saved
- Quality of insights vs. direct questioning
- Whether you actually address agent findings

If agents consistently waste time or produce generic advice, stop using them.

### Evidence

**From logs - adversarial agent spawning**:

```
User: "launcch an agent to show there are bugs in the impl"
```
- Explicit goal: find bugs (adversarial)
- Not "review code" (neutral)
- Forces critical perspective

```
User: "ok... launcch agents to criticize what we did here. heavily, then
synthesize and address the issues"
```
- Multiple agents (plural)
- Specific instruction: "heavily" criticize
- Two-phase: criticize, then synthesize
- Action-oriented: "address the issues"

**Pattern frequency**: Medium (not every session, but recurring)
**Typos in commands**: "launcch" shows casual, rapid usage

**Missing evidence**:
- No logs showing synthesis results
- No data on whether agent findings were actually addressed
- Can't measure time saved vs. overhead

**Speculation to avoid**: Can't claim "10x productivity" or "finds bugs humans
miss" without evidence. Pattern shows users DO this, not that it WORKS well.

---

## Pattern 3: Criticism-Driven Development
**Counter-intuitive Score**: 7/10
**Usefulness Score**: 7/10
**Evidence Quality**: Medium

### Why Selected

Actively seeking harsh criticism of your own work contradicts ego protection
and "be constructive" culture. Related to agent pattern but distinct - focuses
on the metacognitive approach of adversarial collaboration.

### What It Contradicts

**Professional development culture**:
- Be constructive in feedback
- Focus on positives first, then areas for improvement
- Protect team morale with gentle criticism
- "What went well?" before "What went wrong?"

**Code review norms**:
- Ask for review, accept whatever feedback comes
- Frame feedback politely
- LGTM (looks good to me) culture

**This pattern**:
- **Explicitly request harsh criticism**
- Ask AI to find bugs, assume they exist
- "Criticize heavily" as direct instruction
- Assume your work has flaws, force them to surface

### When It Works

**Psychological requirements**:
1. **Ego detachment** - not defensive about code
2. **Action-oriented** - criticism leads to fixes, not just feelings
3. **Confidence** - secure enough to seek negative feedback
4. **Time pressure** - need fast iteration, no time for gentle feedback

**Use cases**:
- Before production deploy: "find everything wrong with this"
- Architecture decisions: "what are the downsides I'm missing?"
- Performance optimization: "where are the bottlenecks?"
- Security review: "how would an attacker break this?"

**Why it works**:
- **Confirmation bias mitigation** - forces you to see flaws you'd ignore
- **Faster learning** - harsh feedback is clearer than gentle hints
- **Completeness** - "find ALL bugs" vs. "looks mostly good"
- **No social cost** - AI doesn't have feelings, can be brutally honest

### When It Doesn't Work

**Failure modes**:

1. **Demoralization** - if you're not psychologically ready, harsh criticism
   demotivates
2. **Paralysis** - too much criticism → don't know where to start
3. **False negatives** - AI criticism might be wrong, waste time defending
4. **Diminishing returns** - criticizing trivial details wastes time
5. **No synthesis** - list of flaws without prioritization = useless

**Costs**:
- **Time** - reading/processing criticism takes time
- **Mental energy** - draining to receive harsh feedback constantly
- **Risk of over-correction** - fixing non-issues because AI said so
- **Context loss** - AI doesn't know your constraints, criticizes infeasible
  things

**Not suitable for**:
- Junior developers still building confidence
- High-stress situations where morale matters
- Projects where "good enough" is sufficient
- Teams with fragile dynamics (stick to human-only criticism)

### How To Adopt

**Step 1: Frame criticism requests specifically**

Vague: "review this code"
Better: "find bugs in this code"
Best: "assume this code has race conditions and find them"

Vague: "what do you think?"
Better: "what are the downsides of this approach?"
Best: "criticize this architecture for scalability under 100x load"

**Step 2: Set scope boundaries**

Don't: "criticize everything"
Do: "criticize transaction signing logic only"

Don't: "find all flaws"
Do: "find security flaws, ignore style issues"

**Step 3: Request actionable criticism**

Add: "and propose fixes"
Add: "and rank by severity"
Add: "and estimate effort to fix"

**Step 4: Batch criticism with action**

Bad flow:
1. Request criticism
2. Receive criticism
3. Feel bad
4. Maybe fix later

Good flow:
1. Request criticism
2. Receive criticism
3. Immediately: "synthesize top 3 issues and fix them"
4. Validate fixes

**Step 5: Calibrate harshness**

Start: "what could be improved?"
Medium: "find bugs in this implementation"
Harsh: "criticize this heavily and find all flaws"
Extreme: "assume I'm an incompetent developer and this code is broken"

Use harshness appropriate to:
- Your ego resilience
- Time available to address issues
- Criticality of code (harsh for security, gentle for prototypes)

### Evidence

**From logs - explicit harsh criticism requests**:

```
User: "ok... launcch agents to criticize what we did here. heavily, then
synthesize and address the issues"
```
- Adverb: "heavily" - explicit harshness request
- Not just "review" or "check"
- Synthesis and action steps included

```
User: "criticize the agnets in lue of the buildin agents... which are utterly
useless?"
```
- Strong language: "utterly useless"
- Sets critical tone
- Comparative criticism (vs. built-in agents)

```
User: "I like the tool, but try running it with config and config.2 and
criticize its accuracy"
```
- Positive framing ("I like") + criticism request
- Specific test case (two configs)
- Targeted criticism (accuracy only)

**Pattern traits**:
- Criticism is **requested**, not passively accepted
- Often includes **synthesize/address** instruction (action-oriented)
- Sometimes uses strong language to set tone

**Missing evidence**:
- Don't see the actual criticism received
- Don't see whether criticism was valid or addressed
- Can't measure effectiveness

---

## Pattern 4: Integration Test Over Unit Test
**Counter-intuitive Score**: 6/10
**Usefulness Score**: 8/10
**Evidence Quality**: High

### Why Selected

Despite being a known contrarian position (critique was correct), this pattern
has:
1. **Strong evidence in logs** - explicit rejection of mock tests
2. **Concrete implementation** - make test vs. make smoke split
3. **Measurable trade-offs** - documented costs in CLAUDE.md
4. **Actionable adoption path** - clear how to implement

Kept because it's well-evidenced and actionable, even if not maximally novel.

### What It Contradicts

**Testing pyramid doctrine**:
```
     /\
    /e2e\      Few (5-10%)
   /------\
  /  integ \   Some (15-20%)
 /----------\
/    unit    \ Many (70-80%)
```

**Standard practice**:
- Unit tests are foundation, integration is supplementary
- Mock external dependencies
- Test in isolation
- Fast feedback from unit tests
- TDD at unit level

**This pattern inverts it**:
- Integration tests are foundation
- Mock only external systems, not internal ones
- Test whole pipelines
- Accept slower tests for higher confidence

### When It Works

**Suitable contexts**:
1. **Data pipelines** - value is in transformations, not individual functions
2. **API integrations** - bugs are in protocol mismatches, not logic
3. **Financial systems** - correctness matters more than speed
4. **External dependencies** - can't mock third-party APIs effectively

**Why it works**:
- **Mocks become stale** - when real API changes, mocks lie
- **Integration bugs dominate** - most prod bugs are boundary issues
- **Refactoring confidence** - can restructure internals, tests still pass
- **Documentation value** - shows actual system behavior

### When It Doesn't Work

**Explicit costs** (acknowledged in critique):

1. **Speed**: Integration tests are slow
   - Evidence: `make test` (<5s) vs. `make smoke` (~80s)
   - CI/CD time increases
   - Developer feedback loop slower

2. **Debugging difficulty**: When integration test fails, could be any component
   - Unit tests pinpoint exact failure
   - Integration tests require more investigation

3. **Infrastructure requirements**:
   - Need actual databases, services, external systems
   - Setup/teardown complexity
   - CI environment must match local

4. **Flakiness**:
   - Network issues, timing problems, external service outages
   - Unit tests are deterministic, integration tests often aren't

5. **Coverage gaps**:
   - Hard to test error paths (network failures, edge cases)
   - Unit tests can easily test all branches
   - Integration tests cover happy paths best

**Not suitable for**:
- Libraries with many edge cases (unit tests excel here)
- Performance-critical code (need fast test iterations)
- Complex algorithms (unit tests better for correctness proofs)
- Large teams (slow tests block everyone)

### How To Adopt

**Step 1: Separate fast from slow** (from CLAUDE.md):

```makefile
# Fast unit tests only (<5s)
test:
    go test -short ./...

# All tests including slow integration (~80s)
smoke:
    go test ./...
```

In Go, mark slow tests:
```go
func TestIntegration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }
    // actual integration test
}
```

**Step 2: Identify what to integration test**

Good candidates:
- API request → database → response flow
- File input → processing → output file
- External API call → parse → store

Bad candidates:
- String formatting function
- Math calculations
- Validation logic

**Step 3: Accept the costs**

- Budget 60-120s for full test suite (smoke)
- Run integration tests in CI only? Or locally before commit?
- Setup real database/services for testing
- Handle flakiness with retries/timeouts

**Step 4: Keep some unit tests**

Don't delete all unit tests. Keep them for:
- Complex algorithms
- Many edge cases
- Pure functions
- Performance-critical code

**Step 5: Measure effectiveness**

Track over 3 months:
- How many bugs found by integration tests vs. unit tests?
- How many prod bugs would integration tests have caught?
- Is slow test time worth the confidence?

If integration tests don't find meaningful bugs, revert to unit tests.

### Evidence

**From logs - explicit rejection of unit tests**:

```
"dont test trivial things, test the whole pipeline"
```
- Directive: focus on pipeline, not pieces
- "Trivial things" = dismissing unit-testable components

```
"so they dont test anything?" (rejecting mock tests)
```
- Rhetorical question implying mocks are worthless
- Critique of test that uses mocks extensively

**From CLAUDE.md - codified practice**:

```
- ALWAYS separate fast unit tests from slow integration tests:
  - `make test`: Fast unit tests only (< 5s), use -short flag in Go
  - `make smoke`: All tests including slow integration tests (~80s)
  - Mark slow tests with `if testing.Short() { t.Skip() }` in Go
```

**Costs acknowledged**:
- Explicit time budgets: <5s vs. ~80s
- Separation strategy to mitigate slow tests
- Uses -short flag to skip slow tests in dev

**Philosophy**:
```
- Integration and e2e tests over mock tests
- Unit tests mock external systems, not internal
```

This is clearer than most "integration over unit" arguments because:
1. **Quantified trade-off**: 5s vs. 80s (16x slower)
2. **Mitigation strategy**: make test vs. make smoke
3. **Nuanced position**: "mock external, not internal" (not "no mocks ever")

---

## Rejected Patterns

### Pattern 1: Real Production Data Debugging
**Why rejected**: Conflated "pasting logs" (conventional) with "developing
against production" (the actual unconventional part, which is Pattern 2).
Security/privacy costs of production data in AI chats not addressed.

**Better captured by**: Pattern 1 (Build-Deploy-Fix Cycle) which is the
genuinely risky production deployment pattern.

### Pattern 3: Iterative Debugging with Short Commands
**Why rejected**: Natural chat interface evolution, not transferable wisdom.
Can't teach someone to "use short commands" - it emerges from shared context.
Usefulness claims inflated ("10x faster" from saving 13 words).

**If anything, Pattern 11 (Typo-Laden Commands) is more interesting**: Shows
robust intent parsing, has accessibility benefits.

### Pattern 4: Memory/Wisdom Recording Pattern
**Why rejected**: Circular logic - analyzing CLAUDE.md finds people use
CLAUDE.md, concludes this is counter-intuitive. Usefulness speculative
("depends on implementation"). It's just documentation.

### Pattern 20: Unix Philosophy and Simplicity
**Why rejected**: Philosophy, not pattern. Too vague to adopt. No specific
action steps. Meta-pattern that underlies others but isn't actionable on
its own.

### Pattern 6: /init Command
**Why rejected**: Tool-specific command, no transferable insight. Unknown
what it actually does.

### Pattern 12: Discord Logging Integration
**Why rejected**: Specific implementation detail, not counter-intuitive
pattern. Selective logging is conventional wisdom.

---

## Changes From Initial Selection

### What Changed

**Removed (3/4 patterns)**:
1. Real Production Data Debugging → Build-Deploy-Fix Cycle
2. Iterative Short Commands → Agent-Based Task Decomposition
3. Memory/Wisdom Recording → Criticism-Driven Development

**Kept (1/4 patterns)**:
- Integration Test Over Unit Test (despite being known, well-evidenced)

### Why Changes Were Made

**Confirmation bias addressed**:
- Old selection: 3/4 patterns validated existing CLAUDE.md wisdom
- New selection: 2/4 patterns (agents, criticism) are novel approaches

**Specificity improved**:
- Dropped vague meta-patterns (memory recording, short commands)
- Added concrete practices (agent spawning, criticism framing)

**Cost accounting added**:
- Every pattern now has "When It Doesn't Work" section
- Explicit failure modes, costs, and limitations
- No inflated claims without evidence

**Genuine counter-intuition prioritized**:
- Build-Deploy-Fix: genuinely shocking (multiple prod deploys per session)
- Agent-Based: genuinely novel (adversarial AI spawning)
- Criticism-Driven: genuinely uncomfortable (seeking harsh feedback)
- Integration-Over-Unit: genuinely debated (inverted pyramid)

### What Didn't Change (And Why)

**Kept Integration Test pattern** despite critique noting it's "well-known":
- Has strongest evidence in logs
- Most actionable (concrete make targets, time budgets)
- Costs explicitly acknowledged (5s vs. 80s)
- Nuanced position (mock external, not internal)

Better to have one well-documented known pattern than four poorly-documented
novel ones.

### Methodology Improvements Applied

1. **Blind scoring abandoned** - instead, explicit evidence citations
2. **Cost-benefit required** - every pattern has failure modes section
3. **Speculation flagged** - "Missing evidence" subsections note gaps
4. **Disconfirmation bias** - selected patterns that contradict CLAUDE.md
   (agents, criticism) over ones that confirm it

### Remaining Limitations

**Still can't measure**:
- Whether these patterns actually provide competitive advantage
- Time saved vs. overhead
- Success rate of adoptions
- Long-term sustainability

**Still speculative**:
- "When it works" sections based on reasoning, not data
- Adoption steps untested
- Usefulness scores still somewhat arbitrary

**Still missing**:
- Control group comparison (do conventional teams work differently?)
- Failed patterns (what did users try and abandon?)
- Quantitative analysis (frequency → impact correlation)

**Honest assessment**: This is pattern identification from logs, not rigorous
study. Treat as hypotheses to test, not proven practices.
