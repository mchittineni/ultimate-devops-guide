---
title: "What are Service Level Indicators (SLIs)?"
id: 98
category: "Site Reliability Engineering (SRE)"
difficulty: "Intermediate"
tags:
  - devops
  - site-reliability-engineering
  - interview-questions
---

# What are Service Level Indicators (SLIs)?

**Short answer:** An SLI is a carefully defined quantitative measure of some aspect of service quality - typically expressed as the ratio of good events to total valid events - that reflects what users actually experience.

## Detail

**The standard form:** `good events / valid events`, expressed as a percentage. This ratio form is preferred because it is naturally bounded, aggregates cleanly, and translates directly into an error budget.

**The common SLI categories**

- **Availability** - successful requests / total requests.
- **Latency** - requests faster than a threshold / total requests. Note the framing: a _proportion under a threshold_, not an average, because that is what the user experiences.
- **Quality** - requests served with full functionality / total (useful where degraded responses are possible).
- **Freshness** - data updated within a threshold / total (for pipelines and caches).
- **Correctness** - records processed correctly / total (for batch systems).
- **Coverage** - data successfully processed / data that should have been processed.

**Where to measure.** Closer to the user is better: load balancer or gateway metrics beat application-internal metrics, because they capture failures the application never sees. Client-side or synthetic probes capture even more, including DNS and network problems, at the cost of noise.

**Definition details that matter.** What counts as a "valid" event? Client errors (4xx) are usually excluded from availability - you should not be penalised for malformed requests - but a 429 from your own rate limiter arguably is your failure. Health-check traffic should be excluded. Write these decisions down; ambiguity here makes the SLO meaningless.

## Example

```promql
# Latency SLI: proportion of requests served under 300ms
sum(rate(http_request_duration_seconds_bucket{le="0.3",job="api"}[5m]))
/ sum(rate(http_request_duration_seconds_count{job="api"}[5m]))
```

## Interview tips

- The good/valid ratio formulation is the phrasing SRE interviewers expect.
- Latency as a threshold proportion rather than a percentile is a subtle, high-signal point.
- Be ready to say where you measure and why - closer to the user, always.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you choose an SLO target?]] (`#177`): [How do you choose an SLO target?](../slo-engineering/how-do-you-choose-an-slo-target.md)
- [[What is multi-window multi-burn-rate alerting?]] (`#178`): [What is multi-window multi-burn-rate alerting?](../slo-engineering/what-is-multi-window-multi-burn-rate-alerting.md)
- [[How do you measure a latency SLI correctly?]] (`#179`): [How do you measure a latency SLI correctly?](../slo-engineering/how-do-you-measure-a-latency-sli-correctly.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
