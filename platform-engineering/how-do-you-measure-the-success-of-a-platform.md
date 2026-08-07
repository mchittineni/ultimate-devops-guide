---
title: "How do you measure the success of a platform?"
id: 228
category: "Platform Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# How do you measure the success of a platform?

**Short answer:** Combine delivery outcomes (the four DORA metrics), adoption (share of teams and new services on the golden path, self-service completion rate), developer experience (a short recurring survey plus time-to-first-deploy for a new engineer), and efficiency (platform cost per team, and platform-engineer time spent on toil versus product work). No single number is sufficient, and output metrics like "features shipped" measure nothing.

## Detail

**The four layers, and what each catches:**

| Layer           | Metrics                                                                      | Catches                                 |
| --------------- | ---------------------------------------------------------------------------- | --------------------------------------- |
| Delivery (DORA) | deployment frequency, lead time, change failure rate, MTTR                   | whether the platform speeds up delivery |
| Adoption        | % new services on the path, % on supported versions, tickets vs self-service | whether anyone wants it                 |
| Experience      | developer satisfaction, time to first deploy, top friction points            | whether it is pleasant to use           |
| Efficiency      | cost per team, toil share of platform team time, incident load               | whether it is sustainable               |

**Adoption is the metric a platform team cannot fake.** Delivery metrics can improve for unrelated reasons; a survey can be gamed by asking the wrong people. The percentage of new services that voluntarily choose the golden path, and the share of existing services still on a supported template version, are hard to argue with.

**Time to first successful deploy is the single best onboarding proxy.** Measure it for a genuinely new engineer, from repository creation to production. It exposes gaps in documentation, permissions, and defaults that no other metric surfaces, and it is easy to explain to leadership.

**Self-service completion rate makes the ticket problem visible.** Of attempts to provision something, what fraction completed without platform-team involvement? A falling rate points at a specific broken capability. Pair it with a count of platform support requests grouped by cause - each recurring cause is a design or documentation defect.

**Survey sparingly and act visibly.** A short quarterly survey (5–8 questions, one free-text "what slows you down most?") gets responses; a long one does not. The critical part is closing the loop: publish what you heard and what you changed, or response rates collapse. Frameworks such as SPACE and DevEx exist to keep the questions balanced across satisfaction, flow, and cognitive load.

**Beware metrics that drive the wrong behaviour.** Deployment frequency alone rewards trivial deploys; MTTR alone rewards closing incidents rather than fixing causes; "tickets closed" rewards a service desk over automation. Always pair a speed metric with a stability metric - that pairing is the whole point of DORA.

**Report in the language of the business** when talking to leadership: cycle time and change failure rate translate into shipping speed and incident cost; platform cost per team translates into efficiency. Reporting internal component delivery to an executive audience is how platform teams lose funding.

## Example

```text
Platform scorecard - Q3 2026 (published to all engineering)

Delivery         deployment frequency     4.1/day/team   ▲ from 2.6
                 lead time (commit->prod) 22 min p50     ▲ from 51 min
                 change failure rate      9%             ▼ from 14%
                 MTTR                     31 min p50     ▼ from 47 min

Adoption         new services on path     31/34 (91%)
                 on supported template    28/42 (67%)    target 85% by Q4
                 self-service completion  88%            ▲ from 71%
                 support requests         64 (top cause: secret rotation, 19)

Experience       developer CSAT           4.1/5 (n=37, 79% response)
                 time to first deploy     3 h 40 m (new hire, measured twice)
                 top friction             staging data freshness

Efficiency       platform cost / team     $2,140 / month (published per team)
                 platform toil share      34% of team time  target < 25%

Actions taken from last quarter's survey: ephemeral envs shipped, docs rewritten
for deploy debugging. Not done: secret rotation (moved to Q4, now top request).
```

## Interview tips

- Give the four layers rather than a list of metrics; the structure is what is being assessed.
- "Adoption is the metric you cannot fake" and "always pair speed with stability" are the two lines to land.
- Expect: "what would you do if adoption were low?" - treat it as product feedback, interview the teams routing around you, and fix the missing capability.

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
