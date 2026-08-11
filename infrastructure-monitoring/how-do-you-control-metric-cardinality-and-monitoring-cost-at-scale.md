---
title: "How do you control metric cardinality and monitoring cost at scale?"
id: 293
category: "Infrastructure Monitoring"
difficulty: "Advanced"
tags:
  - devops
  - infrastructure-monitoring
  - interview-questions
---

# How do you control metric cardinality and monitoring cost at scale?

**Short answer:** Treat every label as a multiplier and govern it. Find the offending series with `topk` on cardinality, drop or aggregate high-cardinality labels at the collection point (`metric_relabel_configs`, OTel processors) rather than at query time, never put unbounded values (user ID, request ID, full URL path, container ID) in a label, downsample and tier retention, and put a cardinality budget plus a limit per target in place so a single bad deploy cannot double your bill. Move genuinely high-cardinality questions to logs, traces, or exemplars - that is what they are for.

## Detail

**Why cardinality is the cost driver.** A time series is uniquely identified by its metric name plus its full label set. Every distinct combination is a separate series with its own index entry and memory footprint. The growth is multiplicative: `http_requests_total` with 20 endpoints × 5 status codes × 3 methods × 200 pods = 60,000 series from _one_ metric. Add `user_id` and it becomes unbounded. In Prometheus each active series costs roughly a few kilobytes of resident memory, so cardinality - not sample rate, and not disk - is what causes the OOM and what most vendors bill on.

**Find it before you fix it.** Use the TSDB status endpoint and `topk` queries to identify the worst metrics, the worst label, and the worst targets. Then decide, per case: is this label ever used in a query? Most high-cardinality labels are never grouped by, only carried.

**Fix at the collection point, in this order:**

1. **Drop the metric.** Whole subsystems of instrumentation are frequently unqueried - cAdvisor's full metric set, kube-state-metrics on non-essential objects, Envoy's per-upstream histograms. `metric_relabel_configs` with `action: drop` on a name regex is the biggest single win, and it is reversible.
2. **Drop the label.** `action: labeldrop` on `id`, `container_id`, `pod_template_hash`, `image_id`, `instance` where the target is fungible. Keep exactly what you group by in real dashboards and alerts.
3. **Bucket the value.** Replace a raw value with a class: URL path templated to `/orders/:id`, status code to `2xx`/`5xx`, latency to a bounded set. Do this in the application's instrumentation where possible - the fix belongs upstream of the scrape.
4. **Aggregate before storage.** Recording rules or an OTel `metricstransform`/`filter` processor that pre-aggregates away a dimension you only ever look at in aggregate. Prometheus Agent mode or a collector pipeline is the right place for fleet-wide policy.
5. **Cap it.** `sample_limit` and `label_limit` per scrape config, and per-tenant limits in Mimir/Thanos/Cortex. A cap turns "one deploy tripled our series count" from a bill into an alert.

**Then reduce what you keep.** Retention tiering - raw at 15s for 15 days, 5-minute downsampled for 90 days, 1-hour for a year - covers almost every real query. Thanos and Mimir do this natively; managed vendors charge you for it. Also scrape less often where the signal does not change fast: node-level metrics at 60s instead of 15s cuts ingest by 4x with no practical loss.

**Route the question to the right tool.** "Which requests did customer X make?" is a **logs or traces** question and belongs in a system built for high cardinality (Loki, Elasticsearch, Tempo, ClickHouse) where the cost model is per-byte-ingested rather than per-series. Metrics answer "how many, how fast, how often" across a bounded set of dimensions. **Exemplars** are the bridge: keep the metric low-cardinality and attach a sampled trace ID so you can jump from the aggregate spike to a specific slow request. Wanting per-user metrics is nearly always a sign the question belongs elsewhere.

**Govern it so it stays fixed.** A cardinality budget per team or service, monitored as a metric itself and alerted on growth rather than on an absolute number. A pull-request check that flags new labels in instrumentation. A quarterly review that deletes dashboards nobody opens - unused dashboards are how unused metrics stay alive. And attribution: cost per team, visible to that team, or nobody ever cleans up.

## Example

```promql
# Where is the cardinality? Ask before you cut.
topk(20, count by (__name__)({__name__=~".+"}))          # worst metrics by series count
topk(10, count by (job)({__name__=~".+"}))               # worst scrape jobs
count(count by (endpoint) (http_requests_total))         # cardinality of one label
prometheus_tsdb_head_series                              # total active series - the cost number

# Growth alert: catch the bad deploy, not the monthly invoice.
- alert: SeriesGrowthSpike
  expr: |
    prometheus_tsdb_head_series
      > 1.3 * avg_over_time(prometheus_tsdb_head_series[1d] offset 1d)
  for: 30m
  annotations:
    summary: "Active series up >30% vs yesterday - check recent deploys"
```

```yaml
# Fix at the collection point, with a hard cap as the backstop.
scrape_configs:
  - job_name: kubernetes-pods
    scrape_interval: 30s
    sample_limit: 20000 # this target cannot flood the TSDB
    label_limit: 30
    metric_relabel_configs:
      # 1. drop metrics nobody queries
      - source_labels: [__name__]
        regex: "container_(tasks_state|memory_failures_total|blkio_.*)"
        action: drop
      # 2. drop labels nobody groups by
      - regex: "id|image_id|container_id|pod_template_hash|uid"
        action: labeldrop
      # 3. bucket an unbounded value into a class
      - source_labels: [path]
        regex: "/orders/[0-9a-f-]+.*"
        target_label: path
        replacement: "/orders/:id"
```

```yaml
# OpenTelemetry Collector: the same policy, fleet-wide, before anything is stored.
processors:
  filter/drop_noisy:
    metrics:
      exclude: { match_type: regexp, metric_names: ["envoy_cluster_upstream_rq_time_.*"] }
  metricstransform/aggregate_away_pod:
    transforms:
      - include: http_server_duration
        action: update
        operations:
          - action: aggregate_labels
            label_set: [service, http_route, http_status_class] # pod dropped deliberately
            aggregation_type: sum
```

```python
# The upstream fix: bounded labels by construction, with an exemplar for the drill-down.
REQ = Counter("http_requests_total", "requests", ["route", "status_class"])  # bounded
REQ.labels(route="/orders/:id", status_class="5xx").inc(exemplar={"trace_id": trace_id})
# NOT: labels(user_id=..., request_id=..., full_path=...) - unbounded, use logs/traces
```

## Interview tips

- Define cardinality as the product of label value counts and give the arithmetic out loud. The multiplication is the insight.
- Say that cardinality, not sample volume or disk, is what drives memory and cost. It is the fact that separates operators from users.
- Give the ordered fix list - drop metric, drop label, bucket the value, pre-aggregate, cap - and stress that it happens at collection, not query, time.
- Name the forbidden labels: user ID, request ID, session ID, full URL path, container ID, timestamp. Interviewers expect this list.
- Route high-cardinality questions to logs and traces, and mention exemplars as the bridge. Wanting per-user metrics is the classic misuse.
- Close on governance: a cardinality budget alerted on growth, a PR check on new labels, and per-team cost attribution. One-off cleanups regress within a quarter.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
