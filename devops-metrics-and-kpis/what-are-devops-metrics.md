---
title: "What are DevOps Metrics?"
id: 101
category: "DevOps Metrics and KPIs"
difficulty: "Beginner"
tags:
  - devops
  - devops-metrics-and-kpis
  - interview-questions
---

# What are DevOps Metrics?

**Short answer:** DevOps metrics measure the performance of the software delivery system itself. The four DORA metrics - deployment frequency, lead time for changes, change failure rate, and time to restore - are the industry standard, complemented by reliability and flow metrics.

## Detail

**The four DORA metrics**

| Metric                          | Definition                                | Top-band performance            |
| ------------------------------- | ----------------------------------------- | ------------------------------- |
| Deployment frequency            | How often you deploy to production        | On demand, multiple times a day |
| Lead time for changes           | Commit to running in production           | Less than one day               |
| Change failure rate             | Percentage of deploys causing degradation | Roughly 5%                      |
| Failed deployment recovery time | Time to restore after a failed change     | Less than one hour              |

Two measure **throughput**, two measure **stability** - and the central DORA finding is that they rise together. Teams that deploy more often also fail less, because small changes are safer. A fifth metric, **reliability** (operational performance against SLOs), was later added.

**Know that the tiers were retired.** DORA renamed "time to restore service" to _failed deployment recovery time_, and the 2025 State of DevOps report abandoned the elite/high/medium/low ranking entirely, replacing it with seven team archetypes that pair delivery performance with human factors - burnout, friction, and perceived product value. The numbers above are still a useful scale for orienting yourself; they are no longer a league table you get placed in.

**Complementary measures**

- **Flow** - cycle time, work in progress, flow efficiency (active time versus waiting time), queue lengths.
- **Quality** - escaped defects, test coverage trends, flaky test rate.
- **Operational** - MTTD, MTTA, MTTR, alert volume, percentage of alerts that were actionable.
- **Developer experience** - build times, time to first commit for a new joiner, and survey-based measures such as the SPACE framework.

**How to use them well.** Metrics are for the team to improve its own system, not for comparing teams or individuals. Every metric is gameable - deployment frequency rises if you split one deploy into ten, change failure rate falls if you redefine "failure." Use them in balanced pairs, look at trends rather than absolute values, and always pair a quantitative metric with a qualitative signal.

## Interview tips

- Name all four DORA metrics precisely; getting this list right is table stakes.
- The throughput/stability pairing and the fact they correlate positively is the insight worth stating.
- Volunteer the gaming risk before being asked - it shows you have used these in practice.

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
