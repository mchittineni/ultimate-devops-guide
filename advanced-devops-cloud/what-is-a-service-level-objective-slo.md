---
title: "What is a Service Level Objective (SLO)?"
id: 149
category: "Advanced DevOps & Cloud"
difficulty: "Beginner"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is a Service Level Objective (SLO)?

**Short answer:** An SLO is the internal reliability target for a service level indicator over a defined window - the number the team commits to, from which the error budget is derived.

## Detail

**The anatomy of a complete SLO statement:** _"99.9% of HTTP requests to the checkout API, measured at the load balancer excluding 4xx client errors, complete successfully over a rolling 28-day window."_ It names the indicator, the target, the measurement point, the exclusions, and the window. Anything less is ambiguous when it matters.

**Choosing the target**

- Base it on user need and current measured performance, not aspiration. If you deliver 99.5% today, committing to 99.99% guarantees a permanently exhausted budget and a policy everyone ignores.
- Consider the cost curve: each additional nine typically multiplies cost. 100% is never the right target because it prohibits all change.
- Different user journeys deserve different targets. Checkout and the marketing site are not equally critical.

**The window.** A 28- or 30-day rolling window is standard. Rolling avoids the artificial amnesty of a calendar-month reset.

**The error budget** - `1 − SLO` - is what makes the SLO operationally useful. It converts reliability into a quantity that can be spent, tracked, and used to arbitrate between shipping features and improving stability, according to a policy agreed in advance.

**Keep the number of SLOs small.** Two or three per critical user journey, reviewed quarterly against real user experience and complaint data. Dozens of SLOs nobody looks at are worse than three that drive decisions.

## Interview tips

- Give a complete, precisely-worded SLO statement - the specificity itself is the answer.
- "100% is the wrong target" plus the cost-curve reasoning is the SRE point to land.
- Mention reviewing SLOs periodically; a target set once and never revisited stops reflecting reality.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
