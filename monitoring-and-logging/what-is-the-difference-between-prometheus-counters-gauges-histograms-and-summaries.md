---
title: "What is the difference between Prometheus Counters, Gauges, Histograms, and Summaries?"
id: 560
category: "Monitoring and Logging"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - prometheus
  - metrics
  - histogram
  - promql
quiz:
  stem: "Why do site reliability engineers prefer Prometheus Histograms over Summaries when calculating cluster-wide p99 latency SLOs?"
  options:
    - "Summaries use twice as much network bandwidth as Histograms"
    - "Histograms store bucket counters that can be mathematically aggregated across hundreds of distributed pods, whereas quantiles calculated by Summaries cannot be combined"
    - "Summaries cannot measure latency values greater than one second"
    - "Histograms automatically fix slow database queries"
  answer: 2
  explanation: "Summaries calculate quantiles on the client machine; statistically, you cannot average percentiles across multiple nodes. Histograms expose raw bucket counts that PromQL can aggregate across the entire cluster."
---

# What is the difference between Prometheus Counters, Gauges, Histograms, and Summaries?

**Short answer:** Counters are monotonically increasing values that only reset on restart; Gauges are instantaneous values that go up and down; Histograms sample observations into client-side buckets enabling server-side aggregations; Summaries calculate client-side quantiles but cannot be aggregated across instances.

## Detail

Selecting the right metric type is critical for accurate PromQL querying:

### The Metric Types

1. **Counter**: Only increments (or resets to 0 on restart).
   - Use for: Request counts, error counts, bytes sent.
   - Queried via `rate()` or `increase()`.
2. **Gauge**: Snapshot value that can rise and fall.
   - Use for: Memory usage, CPU temperature, active concurrent connections.
3. **Histogram**: Divides observations (e.g. latency) into configurable bucket ranges (`le="0.1"`, `le="0.5"`, `le="1.0"`) plus `_count` and `_sum`.
   - **Advantage**: Can be aggregated across multiple pods/instances using `histogram_quantile(0.99, sum(rate(http_duration_bucket[5m])) by (le))`.
4. **Summary**: Directly calculates streaming quantiles (p50, p90, p99) on the client side.
   - **Disadvantage**: **Cannot be aggregated** across multiple instances (you cannot mathematically average p99 percentiles from 10 different servers).

**Histogram trade-offs.** Classic histograms only estimate quantiles by interpolating within a bucket, so accuracy depends on choosing buckets around your SLO thresholds, and every bucket is a separate series (cardinality cost). **Native histograms** in Prometheus use exponential buckets stored as a single series, giving better resolution at lower cost, but they need client and server support end to end. Summaries remain useful for a single-instance, fixed-quantile need where aggregation is never required.

## Example

```python
from prometheus_client import Counter, Gauge, Histogram, Summary

REQUESTS = Counter("http_requests_total", "Requests served", ["route", "code"])
IN_FLIGHT = Gauge("http_requests_in_flight", "Requests currently being handled")
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["route"],
                    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2.5])
PAYLOAD = Summary("http_request_size_bytes", "Request body size")  # _count and _sum only in the Python client

@IN_FLIGHT.track_inprogress()
def handle(route, body):
    with LATENCY.labels(route=route).time():
        PAYLOAD.observe(len(body))
        REQUESTS.labels(route=route, code="200").inc()
```

```promql
rate(http_requests_total[5m])                                                    # counter -> per-second rate
http_requests_in_flight                                                          # gauge -> read directly
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))  # aggregatable p99
```

## Interview tips

- Counters only increase (queried with `rate`); Gauges fluctuate freely.
- Histograms use configurable buckets allowing multi-instance quantile aggregation.
- Summaries calculate quantiles on the client and cannot be mathematically averaged across pods.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?]] (`#687`): [How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?](../infrastructure-monitoring/how-does-node-exporter-collect-linux-host-hardware-and-os-metrics-for-prometheus.md)
- [[What is Multi-Window Multi-Burn-Rate alerting and why does it eliminate alert fatigue?]] (`#642`): [What is Multi-Window Multi-Burn-Rate alerting and why does it eliminate alert fatigue?](../site-reliability-engineering/what-is-multi-window-multi-burn-rate-alerting-and-why-does-it-eliminate-alert-fatigue.md)
- [[What are the Four Golden Signals of Monitoring and how do you monitor them in distributed systems?]] (`#644`): [What are the Four Golden Signals of Monitoring and how do you monitor them in distributed systems?](../site-reliability-engineering/what-are-the-four-golden-signals-of-monitoring-and-how-do-you-monitor-them-in-distributed-systems.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
