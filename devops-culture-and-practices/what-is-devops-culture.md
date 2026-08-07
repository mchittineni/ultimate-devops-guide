---
title: "What is DevOps Culture?"
id: 126
category: "DevOps Culture and Practices"
difficulty: "Beginner"
tags:
  - devops
  - devops-culture-and-practices
  - interview-questions
---

# What is DevOps Culture?

**Short answer:** DevOps culture is the set of shared values that make the practices work - shared ownership of production, blamelessness, continuous learning, collaboration over handoffs, and treating operational quality as everyone's responsibility.

## Detail

**The pillars**, often summarised as CALMS:

- **Culture** - one team with one goal, not development throwing releases over a wall to operations.
- **Automation** - remove manual toil so people work on problems worth human attention.
- **Lean** - small batches, fast flow, limited work in progress, and relentless removal of waiting time.
- **Measurement** - decisions from data: DORA metrics, SLOs, and telemetry from production.
- **Sharing** - knowledge, tooling, and responsibility flow across team boundaries.

**What it looks like day to day**

- Developers carry the pager for what they build, and therefore care about logs, health checks, and rollback.
- Operations engineers are involved in design, not just handed a finished artifact.
- Failure is treated as information. Post-mortems are blameless and published.
- Experimentation is safe because changes are small and reversible.
- Documentation and internal tooling are valued work, not overhead.

**Changing a culture.** You cannot mandate it. What works is making the desired behaviour easier than the alternative: build the pipeline that makes small deploys trivial, put developers on call with genuinely good alerting, run blameless reviews yourself until they are normal, and publish metrics that show improvement. Start with one willing team and let the results create demand.

**The anti-patterns:** a separate "DevOps team" acting as a gatekeeper, blame-driven incident reviews, heroes rewarded for firefighting rather than prevention, and "we do DevOps, we have Jenkins."

## Interview tips

- CALMS is a useful structure, but back each letter with a behaviour, not just the word.
- The "DevOps team as a new silo" anti-pattern is worth naming; interviewers often live it.
- Best answer to "how do you change culture?": make the right thing the easy thing, and show data.

---

[⬅ Back to DevOps Culture and Practices](./README.md) · [All topics](../README.md)
