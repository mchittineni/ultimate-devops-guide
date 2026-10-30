---
title: "What are the SPACE and DevEx frameworks and how do they complement DORA metrics?"
id: 786
category: "DevOps Metrics and KPIs"
difficulty: "Intermediate"
tags:
  - devops
  - devops-metrics-and-kpis
  - interview-questions
  - developer-productivity
  - space
  - devex
  - dora
quiz:
  stem: "Which statement best describes how the SPACE framework should be applied?"
  options:
    - "Pick the single SPACE dimension that is easiest to automate and use it to rank engineers"
    - "Measure several dimensions at once, mixing system data with survey data, and never rely on activity counts alone"
    - "Replace DORA metrics entirely with lines of code and commit counts"
    - "Use it only for individual performance reviews"
  answer: 2
  explanation: "SPACE's core guidance is to use metrics from at least three of its five dimensions together, combine perceptual (survey) and system data, and avoid treating activity metrics such as commits or PR counts as productivity on their own."
---

# What are the SPACE and DevEx frameworks and how do they complement DORA metrics?

**Short answer:** DORA measures the outcome of the delivery _system_ (throughput and instability). **SPACE** (2021) is a framework for measuring developer productivity across five dimensions - Satisfaction and well-being, Performance, Activity, Communication and collaboration, Efficiency and flow - insisting that no single metric captures productivity. **DevEx** (2023) narrows that to the three things that shape how work _feels_ to developers: feedback loops, cognitive load, and flow state. Used together, DORA tells you _what_ is happening to delivery and SPACE/DevEx tell you _why_.

## Detail

**SPACE** (Forsgren, Storey, Maddila, Zimmermann, Houck, and Butler, _ACM Queue_ 2021):

| Dimension                       | Example signals                                               |
| ------------------------------- | ------------------------------------------------------------- |
| Satisfaction and well-being     | survey satisfaction, burnout, would-recommend-team            |
| Performance                     | outcomes: change failure rate, reliability, customer impact   |
| Activity                        | PRs, deploys, reviews - counts, never used alone              |
| Communication and collaboration | review turnaround, onboarding time, knowledge spread          |
| Efficiency and flow             | lead time, interruptions, hand-offs, uninterrupted focus time |

The guidance that matters: pick metrics from **at least three dimensions**, mix **perceptual (survey) and system data**, and measure at team level. Its main warning is against activity metrics masquerading as productivity.

**DevEx** (Noda, Storey, Forsgren, and Greiler, _ACM Queue_ 2023) is more prescriptive:

- **Feedback loops** - how fast builds, tests, reviews, and deploys answer the developer.
- **Cognitive load** - how much a developer must hold in their head to get work done (tooling sprawl, unclear docs, too many owned services).
- **Flow state** - how often developers get uninterrupted, focused time.

Each dimension is measured both by perception ("how satisfied are you with build times?") and by workflow data (actual build times).

**How they fit with DORA.** DORA's own research model already includes well-being and burnout as outcomes, and the 2025 report's team archetypes combine delivery metrics with friction and burnout. In practice: DORA metrics from systems of record, a quarterly DevEx-style survey, and SPACE as the checklist that stops you over-indexing on any one dimension. Vendor frameworks such as the DX Core 4 (speed, effectiveness, quality, impact) package the same ideas into a fixed metric set.

**Limitations.** Surveys need trust, anonymity, and decent response rates; they measure perception, which lags change. Frameworks give you dimensions, not targets - choosing and defining the metrics is still your job, and tying any of them to individual reviews destroys the data.

## Example

A balanced scorecard covering DORA plus three SPACE dimensions, each with a system and a survey signal:

```yaml
scorecard: team-checkout
cadence: quarterly
delivery_dora:
  - deployment_frequency
  - lead_time_for_changes_p50
  - change_failure_rate
  - failed_deployment_recovery_time_p50
  - rework_rate
satisfaction:
  survey: "I would recommend this team's way of working (1-5)"
  system: unplanned_after_hours_pages_per_person
efficiency_and_flow:
  survey: "I regularly get 2+ hours of uninterrupted focus time (1-5)"
  system: [ci_p50_minutes, pr_review_wait_p50_hours]
cognitive_load:
  survey: "I can deploy and debug my services without asking another team (1-5)"
  system: services_owned_per_engineer
rules: team-level only; trends not rankings; never in performance reviews
```

## Interview tips

- Expand the SPACE acronym correctly and say the key rule: at least three dimensions, survey plus system data.
- Contrast the layers: DORA = delivery outcomes, DevEx = developer friction, SPACE = the multi-dimensional lens over both.
- Volunteer the anti-pattern: activity metrics (commits, PRs, lines of code) as productivity.
- Expect the follow-up "how would you measure the impact of an AI coding tool?" - this framework set is the answer's foundation.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
