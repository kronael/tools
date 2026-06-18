---
name: ceo-eval
description: "Business adoption evaluation. NOT for technical production readiness (use cto-eval)."
when_to_use: "CEO evaluation, ROI analysis, make vs buy, should we invest, vendor risk, license risk, strategic fit, total cost of ownership, TCO, business case, product owner evaluation"
---

# CEO Eval

Business-value evaluation of a technology or project. Goal: assess whether adoption creates value, what it costs, and what risks it carries at the organizational level.

## Dimensions

ROI · TCO · vendor lock-in · license risk · strategic fit · community health · make vs buy · risk profile

## Checklist

### 1. License Analysis

**This is the first check because it can be a hard blocker.**

| License | Commercial use | Modify & keep private | Embed in proprietary product |
|---------|---------------|----------------------|------------------------------|
| MIT / Apache-2.0 | ✅ | ✅ | ✅ |
| BSD-2/3 | ✅ | ✅ | ✅ |
| LGPL-2.1/3 | ✅ | ✅ | ✅ (dynamic link only) |
| GPL-2/3 | ✅ | ❌ must open source | ❌ must open source entire product |
| AGPL-3 | ✅ | ❌ must open source | ❌ includes SaaS usage |
| BSL (Busl) | ✅ up to limit | restricted | restricted |
| Proprietary | depends | ❌ | ❌ |
| No license | ❌ | ❌ | ❌ (copyright default) |

**Action if GPL/AGPL:** Either (a) use only internally with no distribution, (b) fork and relicense (check if possible), or (c) do not adopt for any product you distribute.

### 2. Vendor & Dependency Lock-in

**Questions to answer:**
- Is this tool locked to a single cloud provider / paid service?
- If the upstream project disappears tomorrow, how long until we're broken?
- What's the migration cost to an alternative?
- Is the protocol/API an open standard or proprietary?

```
Lock-in matrix:
              | Protocol open? | Alt implementations? | Self-hostable?
Ideal         |      ✅        |         ✅           |      ✅
Acceptable    |      ✅        |         ❌           |      ✅
Risky         |      ❌        |         ❌           |      ✅
Dangerous     |      ❌        |         ❌           |      ❌
```

**Red flag:** Tool only works with Vendor X's paid API, AND Vendor X can change the protocol, AND there's no alternative.

### 3. Total Cost of Ownership (TCO)

Estimate over 2 years:

| Cost Item | Estimate |
|-----------|---------|
| Integration time (hours × rate) | |
| Ongoing maintenance (patches, upgrades) | |
| Incident response when it breaks | |
| Training / onboarding new team members | |
| Licensing / subscription fees | |
| Infrastructure (if self-hosted) | |
| Cost of NOT having this (lost productivity) | |

**Compare against alternatives:**
- Build from scratch (TCO includes full engineering time)
- Competing OSS tools
- Commercial SaaS equivalent

**Rule of thumb:** If "free" OSS tool requires 2 engineers for 3 months to integrate + maintain, it's $200K+ TCO before it delivers a dollar of value.

### 4. Time-to-Value

- How long from "decide to adopt" to "first production value"?
- Is there a working demo/binary you can run in < 30 minutes?
- Are there known adopters in production with similar use cases?
- What's the learning curve for your team?

**Signal:** A tool with no getting-started guide that takes > 1 day to get running locally has a high abandonment rate.

### 5. Community & Support Health

```sh
# Check these
gh repo view <org>/<repo> --json stargazerCount,forkCount,openIssues,updatedAt

# Or manually check:
# - Last commit date
# - Open issues: are they being responded to?
# - Contributors: 1 or many?
# - Release cadence: abandoned vs active
# - Security advisories: any unpatched?
```

| Metric | Healthy | Concerning |
|--------|---------|-----------|
| Last commit | < 3 months | > 1 year |
| Issue response | < 1 week | > 1 month or none |
| Contributors | > 3 active | 1 person (bus factor) |
| Security patches | Prompt | Ignored |
| Releases | Regular | None in 1+ year |

**Bus factor 1 = high risk.** If the maintainer gets hit by a bus, you own this software.

### 6. Strategic Fit

- Does this move us closer to or further from our core competencies?
- Is this in our team's technology stack, or does it introduce a new language/runtime?
- Does adopting this create a differentiated advantage, or is it commodity infrastructure?
- Are our competitors already using this? (positive signal = de-risked)
- Does this align with our 3-year architecture direction?

**Red flag:** Adopting technology that your team has no experience with, for a non-critical use case, during a sprint with delivery pressure.

### 7. Risk Profile

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Upstream breaks API | ... | ... | Fork / pin version |
| Maintainer abandons | ... | ... | Evaluate fork cost |
| Security CVE | ... | ... | Track advisories |
| License change | ... | ... | Audit on each major version |
| Vendor raises prices | ... | ... | Self-host option? |

**Aggregate risk:** Low (all mitigations in place) / Medium (1-2 unmitigated) / High (critical path dependency with no exit).

### 8. Make vs Buy Decision Framework

```
Should we build this ourselves?

1. Is this core to our competitive advantage?
   - YES → consider building (own the roadmap)
   - NO  → prefer buying/adopting OSS

2. Does an OSS solution solve 80%+ of our need?
   - YES → adopt, live with the 20%
   - NO  → build the delta, not the whole thing

3. What's the build cost vs adopt cost?
   - Build < adopt × 2 → consider building
   - Build > adopt × 2 → adopt and contribute upstream

4. Can we afford to maintain this forever?
   - NO → do not build (you create a legacy burden)
   - YES → building is acceptable
```

**Most common mistake:** Building something that already exists because "it doesn't do exactly what we want." The cost of divergence from upstream grows exponentially over time.

## Verdict Template

```
## CEO Eval: <project> v<version>

**Verdict:** [ADOPT / ADOPT WITH CONSTRAINTS / PILOT / DO NOT ADOPT]

**Business case:** [1-2 sentence ROI justification]

**License:** [permissive / copyleft + implication / proprietary]

**Lock-in risk:** [low / medium / high] — [why]

**TCO estimate (2yr):** [rough number or range]

**Time-to-value:** [X days/weeks to first production value]

### Conditions
- ...

### Risks to monitor
- ...

### Recommendation
[Plain English recommendation that a non-technical stakeholder can act on]
```

## Decision Rubric

| Verdict | Meaning |
|---------|---------|
| **ADOPT** | Clear positive ROI, manageable risk, good strategic fit |
| **ADOPT WITH CONSTRAINTS** | Good ROI but specific licensing, lock-in, or risk conditions to satisfy first |
| **PILOT** | Uncertain ROI; run a time-boxed pilot (e.g. 30 days) to validate before committing |
| **DO NOT ADOPT** | Negative ROI, unacceptable license risk, or anti-strategic |
