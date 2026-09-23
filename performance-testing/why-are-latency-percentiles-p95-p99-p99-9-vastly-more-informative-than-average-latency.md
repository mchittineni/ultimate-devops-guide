---
title: "Why are latency percentiles (p95, p99, p99.9) vastly more informative than average latency?"
id: 610
category: "Performance Testing"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - performance-testing
  - performance
  - metrics
  - latency
  - percentiles
quiz:
  stem: "Why does an application with an average latency of 50ms still cause widespread user dissatisfaction if its p99 latency is 8 seconds?"
  options:
    - "Browsers refuse to render web pages with average latency under 100ms"
    - "The average masks severe tail-end latency outliers affecting the slowest 1% of calls, which is amplified when a single page load makes multiple backend calls"
    - "p99 latency only measures network packet transmission speed"
    - "Average latency cannot be calculated in distributed microservices"
  answer: 2
  explanation: "Averages conceal extreme tail latency. When a user action triggers dozens of backend microservice calls, the probability of hitting that 8-second p99 tail skyrockets to over 50%."
---

# Why are latency percentiles (p95, p99, p99.9) vastly more informative than average latency?

**Short answer:** Average (mean) latency hides severe outlier degradation behind thousands of fast requests; percentiles (p95, p99) measure the actual user experience of the slowest 5% or 1% of transactions, which disproportionately affect high-value users in distributed systems.

## Detail

The 'flaw of averages' is a major source of monitoring complacency:

### The Mathematical Trap of Averages

Imagine an e-commerce API handling 1,000 requests:

- 990 requests take **10ms** (fast cache hits).
- 10 requests take **10,000ms** (10 seconds - database locks, timeouts).
- **Average Latency**: `(990 * 10 + 10 * 10000) / 1000 = 109.9 ms`.

A dashboard displaying 'Average latency: 110ms' looks healthy to executives, while in reality 10 paying customers experienced an intolerable 10-second freeze. Note that p99 is right on the boundary here (the 990th fastest request is still 10 ms), while p99.9 shows 10 s - which is why the tail you watch has to match how rare the problem is, and why you need enough samples for a high percentile to mean anything.

### The Multi-Call Latency Amplification

In microservices, loading a single page can fan out to dozens of backend calls, and the page is as slow as the slowest one.

- If each of 100 calls independently has a 1% chance of hitting its slow tail:

```text
P(page hits at least one slow call) = 1 - (1 - 0.01)^100 ≈ 63.4%
```

Nearly two-thirds of page loads will experience some call's p99 tail. This is why engineering organizations anchor their SLOs to p95, p99, and p99.9.

**Limitation: percentiles do not aggregate.** You cannot average the p99 of ten servers to get the fleet p99. Record latency as histograms (Prometheus histograms, OpenTelemetry exponential histograms, HdrHistogram) and compute the percentile from the merged distribution.

## Example

Fleet-wide p99 computed correctly from merged histogram buckets in PromQL, next to the mean for comparison:

```promql
# p99 across all instances: sum the buckets first, then take the quantile
histogram_quantile(0.99,
  sum by (le) (rate(http_request_duration_seconds_bucket{job="checkout"}[5m])))

# Mean latency, for contrast - usually far lower and far less useful
sum(rate(http_request_duration_seconds_sum{job="checkout"}[5m]))
  / sum(rate(http_request_duration_seconds_count{job="checkout"}[5m]))
```

## Interview tips

- Averages hide extreme tail latency and outliers.
- Percentiles representing real user distributions (p99 = 99% of requests faster than X).
- Multi-service request amplification: loading a page issues 50+ calls, guaranteeing tail latency hits users.
- Aligning SLAs and SLOs to p95/p99 rather than mean.
- Say that percentiles cannot be averaged across instances - aggregate histograms instead. It is a common, easily spotted mistake.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[How does Docker BuildKit work and what caching and build features does it unlock?]] (`#515`): [How does Docker BuildKit work and what caching and build features does it unlock?](../docker/how-does-docker-buildkit-work-and-what-caching-and-build-features-does-it-unlock.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
