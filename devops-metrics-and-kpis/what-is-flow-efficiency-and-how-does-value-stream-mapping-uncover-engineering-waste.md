---
title: "What is Flow Efficiency and how does Value Stream Mapping uncover engineering waste?"
id: 653
category: "DevOps Metrics and KPIs"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - devops-metrics-and-kpis
  - metrics
  - value-stream
  - flow-efficiency
  - kanban
quiz:
  stem: "If a software feature took 100 hours from initial branch creation to production deployment, but an engineer only spent 10 hours actively writing code and tests, what is the Flow Efficiency?"
  options:
    - "90%"
    - "10%"
    - "100%"
    - "50%"
  answer: 2
  explanation: "Flow Efficiency is Active Work Time (10 hrs) divided by Total Lead Time (100 hrs), resulting in 10%. The remaining 90% was spent waiting idle in queues."
---

# What is Flow Efficiency and how does Value Stream Mapping uncover engineering waste?

**Short answer:** Flow Efficiency is the percentage of total lead time that an engineering task spends actively being worked on versus waiting idle in queues (waiting for review, QA, or deployment); Value Stream Mapping visualizes these stages to expose queue bottlenecks.

## Detail

In many organizations, a feature takes 6 weeks to ship (Lead Time), but the developer only spent **8 hours actively writing code** (Active Work Time)!

### The Flow Efficiency Formula

```text
flow efficiency = active work time / (active work time + wait time) x 100%
```

Flow efficiencies in the 5-15% range are commonly reported for software teams, meaning work sits idle in queues most of the time:

- Waiting in the backlog.
- Waiting for PR code review.
- Waiting for QA assignment.
- Waiting for the next monthly release train.

### Value Stream Mapping (VSM)

A structured workshop that maps every step from customer request to production release, measuring:

- Process Time (active work).
- Lead/Wait Time (idle queues).
- Quality (% Complete & Accurate).
  Because wait time dominates, shrinking queues (smaller batches, WIP limits, faster reviews, removing hand-offs) shortens lead time far more than making the active work faster.

**Limitations.** "Active" versus "waiting" is rarely recorded precisely - tickets left "In Progress" while someone waits on a reviewer inflate active time - so treat the figure as a rough diagnostic and look at trends. And 100% flow efficiency is not the goal: some slack is what lets a team absorb urgent work without everything else stalling.

## Example

A value stream map for one feature, with the flow-efficiency arithmetic:

```text
Stage            Process time   Wait before next stage     %C&A
Backlog -> dev   -              12 days                    -
Develop          6 h            2 days (review)            90%
Code review      1 h            1 day  (QA queue)          85%
QA               3 h            9 days (release train)     95%
Release          0.5 h          -                          100%

Active   = 6 + 1 + 3 + 0.5                  = 10.5 h
Waiting  = 24 working days x 8 h            = 192 h
Flow efficiency = 10.5 / (10.5 + 192)       ≈ 5.2%
Biggest lever: the 9-day release-train wait, not development.
```

## Interview tips

- Formula: Active Work Time divided by Total Lead Time.
- Industry reality: flow efficiency is typically under 10% (work sits idle in queues).
- Value stream mapping exposing wait states (PR reviews, manual approvals, QA queues).
- Focusing on reducing wait states rather than pressuring developers to write code faster.
- Mention WIP limits and Little's Law (lead time = WIP / throughput): cutting work in progress is the most direct way to cut queue time.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
