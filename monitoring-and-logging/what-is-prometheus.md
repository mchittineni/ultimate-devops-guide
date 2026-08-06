---
title: "What is Prometheus?"
id: 33
category: "Monitoring and Logging"
difficulty: "Beginner"
tags:
  - devops
  - monitoring-and-logging
  - interview-questions
---

# What is Prometheus?

**Short answer:** Prometheus is an open-source monitoring system that scrapes time-series metrics from instrumented targets over HTTP, stores them locally with a powerful query language (PromQL), and evaluates alerting rules that fire through Alertmanager.

## Detail

**Pull model.** Prometheus scrapes `/metrics` endpoints on a schedule rather than receiving pushes. This makes targets simple, makes "is the target up?" a free signal, and avoids a fan-in bottleneck. Short-lived batch jobs, which cannot be scraped, push to a Pushgateway instead.

**Data model.** Every sample is a metric name plus a set of key/value labels, e.g. `http_requests_total{method="GET",status="200"}`. Labels are what make PromQL aggregation powerful — and high-cardinality labels (user IDs, request IDs) are the classic way to melt a Prometheus server.

**Metric types:** counter (monotonic, use with `rate()`), gauge (goes up and down), histogram (bucketed observations, enables percentile estimation), and summary (client-side quantiles).

**Service discovery** integrates with Kubernetes, EC2, Consul, and file-based configs, so targets appear and disappear automatically as pods are scheduled.

**Ecosystem:** Alertmanager for routing, grouping, silencing, and deduplicating alerts; Grafana for dashboards; exporters (node_exporter, blackbox_exporter, database exporters) for systems that cannot be instrumented directly; Thanos or Mimir for long-term storage, global query, and high availability.

## Example

```promql
# Request rate per second, by status class, over 5m
sum by (status) (rate(http_requests_total{job="api"}[5m]))

# 99th percentile latency from a histogram
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))

# Error ratio
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

## Interview tips

- Explain the pull model and why it is a deliberate design choice.
- Cardinality is the top operational pitfall — mention it before you are asked.
- Prometheus is not durable long-term storage by itself; name Thanos/Mimir/Cortex for that.

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
