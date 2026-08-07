---
title: "What are Service Level Objectives (SLOs)?"
id: 97
category: "Site Reliability Engineering (SRE)"
difficulty: "Intermediate"
tags:
  - devops
  - site-reliability-engineering
  - interview-questions
---

# What are Service Level Objectives (SLOs)?

**Short answer:** An SLO is an internal target for a service level indicator over a defined window - for example, "99.9% of requests succeed over 28 days" - that sets the reliability bar and generates the error budget.

## Detail

**The three related terms**

- **SLI** - the measurement (proportion of successful requests, proportion of requests under 300 ms).
- **SLO** - the target for that measurement (99.9% over 28 rolling days).
- **SLA** - a contractual promise to customers, with financial consequences. Always looser than the internal SLO, so you have margin.

**Writing a good SLO**

- Base it on the **user's experience**, not on infrastructure. "Checkout completes successfully" beats "CPU under 80%."
- Choose a window: 28 or 30 rolling days is standard. Rolling windows avoid the artificial reset of calendar months.
- Pick a target from actual user need and current performance, not aspiration. Setting 99.99% on a system that delivers 99.5% just guarantees a permanently exhausted budget.
- Include latency as well as availability - a slow service is an unreliable service.
- Fewer, meaningful SLOs beat many ignored ones. Start with one or two per critical user journey.

**The error budget** is `1 − SLO`. At 99.9% over 30 days, that is 43.2 minutes of allowed failure. Burn-rate alerts fire when you are consuming the budget too quickly: a multi-window, multi-burn-rate alert (fast burn over 1 hour, slow burn over 6 hours) is the standard pattern, and it is far less noisy than threshold alerting.

## Example

```promql
# SLI: availability over 28 days
sum(rate(http_requests_total{job="api",status!~"5.."}[28d]))
/ sum(rate(http_requests_total{job="api"}[28d]))

# Fast-burn alert: consuming 30 days of budget in ~2 days
(
  sum(rate(http_requests_total{status=~"5.."}[1h])) / sum(rate(http_requests_total[1h]))
) > 14.4 * 0.001
```

## Interview tips

- Distinguish SLI/SLO/SLA crisply - this is the most-asked SRE question.
- Multi-window burn-rate alerting is the detail that shows you have implemented SLOs, not just read about them.
- Emphasise measuring from the user's perspective; infrastructure-based SLOs are the common mistake.

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
