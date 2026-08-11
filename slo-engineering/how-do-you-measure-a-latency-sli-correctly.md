---
title: "How do you measure a latency SLI correctly?"
id: 179
category: "SLO Engineering"
difficulty: "Advanced"
tags:
  - devops
  - slo-engineering
  - interview-questions
---

# How do you measure a latency SLI correctly?

**Short answer:** Express latency as a ratio of requests faster than a threshold - "99% of checkout requests complete within 300ms" - rather than as an average or a percentile value. Threshold-based ratios are aggregatable, tie directly to an error budget, and avoid the arithmetic errors that come from averaging percentiles across instances.

## Detail

**Averages hide the users who suffer.** A 120ms mean can contain a 4-second tail affecting 2% of requests. Percentiles are better, but a p99 _value_ as an SLI creates two problems: you cannot average p99 across instances or time buckets (the result is meaningless), and "p99 < 300ms" gives no natural error budget.

**The good-events pattern.** Count requests under the threshold as "good" and divide by total. This composes correctly across instances, regions, and time, and it converts latency into exactly the same budget arithmetic as availability. In Prometheus, `histogram_quantile` on a bucket boundary is unnecessary - read the cumulative bucket directly.

**Choose the bucket boundary before you need it.** Native histograms aside, classic Prometheus histograms only resolve at defined bucket edges, so the SLI threshold must coincide with a bucket boundary. Add explicit buckets at your candidate thresholds (0.1, 0.25, 0.3, 0.5, 1, 2.5) when instrumenting, or you will be interpolating.

**Measure where the user is.** Server-side timing excludes DNS, TLS handshake, network transit, and client rendering. If the SLO is about user experience, the load balancer or CDN is a better vantage point than the application, and real-user monitoring is better still. Say which vantage point you chose and why.

**Differentiate by endpoint class.** A single latency threshold across a search endpoint, a static asset, and a report export is meaningless. Group by user journey with separate thresholds; exclude long-poll, streaming, and websocket routes explicitly rather than letting them ruin the ratio.

**Do not forget failed requests.** A request that returns 500 in 5ms is fast but not good. Latency SLIs should count only successful requests as candidates for "good", or combine both conditions so errors cannot flatter the number.

## Example

```promql
# Latency SLI: fraction of successful checkout requests served in under 300ms
# Requires a histogram bucket with le="0.3"
sum(rate(http_request_duration_seconds_bucket{job="checkout",code!~"5..",le="0.3"}[28d]))
  /
sum(rate(http_request_duration_seconds_count{job="checkout",code!~"5.."}[28d]))
```

```yaml
# Instrument with buckets that match your thresholds - decide them up front
histogram:
  name: http_request_duration_seconds
  buckets: [0.05, 0.1, 0.2, 0.3, 0.5, 1, 2.5, 5, 10]
```

## Interview tips

- Lead with "latency as a ratio, not a percentile value" - it is the distinguishing insight.
- Mention that percentiles cannot be averaged; interviewers use that as a probe.
- Have an opinion on vantage point (client, edge, server) and on excluding failed and streaming requests.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
