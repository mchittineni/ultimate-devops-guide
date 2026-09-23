---
title: "What is high cardinality in metrics systems and why does it crash time-series databases?"
id: 559
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - monitoring
  - prometheus
  - cardinality
  - metrics
  - tsdb
quiz:
  stem: "Which label assignment in a Prometheus metric will most likely cause a catastrophic high-cardinality memory crash?"
  options:
    - "`http_requests_total{environment="production"}`"
    - "`http_requests_total{http_method="POST"}`"
    - "`http_requests_total{user_uuid="8f9a2c3d-e4b5-4a6c-9d8e-1f2a3b4c5d6e"}`"
    - "`http_requests_total{status_code="500"}`"
  answer: 3
  explanation: "UUIDs are unbounded and unique per customer, creating a brand new time-series in the TSDB index for every single user, quickly causing memory exhaustion."
---

# What is high cardinality in metrics systems and why does it crash time-series databases?

**Short answer:** High cardinality occurs when a metric label has an unbounded set of unique values (such as `user_id`, `email`, or `ip_address`), causing the TSDB to create millions of separate time-series streams until memory is exhausted.

## Detail

In time-series databases like Prometheus, M3DB, or Cortex, every unique combination of key-value label pairs constitutes a distinct time-series stream stored in RAM:

$$\text{Total Series} = \text{Metric} \times (\text{Label}_1 \text{ values}) \times (\text{Label}_2 \text{ values}) \times \dots$$

### The Cardinality Explosion

- **Low Cardinality (Good)**: `http_requests_total{method="GET", status="200", region="us-east"}`
  - Methods: 4, Statuses: 10, Regions: 3 $\rightarrow 4 \times 10 \times 3 = 120$ series.
- **High Cardinality (Dangerous)**: `http_requests_total{user_id="123456"}`
  - 1,000,000 users $\rightarrow$ **1,000,000 separate time-series**.

Prometheus must keep every active series in the in-memory head block and maintain forward and inverted (postings) indexes for its labels. Memory grows with the series count - multiplicatively as labels combine - so an unbounded label turns into a steady climb until queries time out and Prometheus is OOM-killed. Churn makes it worse: series that appear briefly (a label containing a pod name or request ID) still cost index memory until the head block is compacted.

### Best Practice

Never put unbounded identifiers (UUIDs, IP addresses, emails, timestamps) into metric labels. Keep high-cardinality fields in **logs** or **trace attributes**, and use exemplars to link a metric to a sample trace. The trade-off is that some questions ("error rate for customer X") then need a log or trace query rather than a cheap metric lookup - for a small set of large tenants, a bounded `tier` or `top_tenant` label is a reasonable compromise.

## Example

```promql
# Find the offenders before they crash the server
prometheus_tsdb_head_series                                   # total active series
topk(10, count by (__name__)({__name__=~".+"}))               # metrics with the most series
count(count by (user_id) (http_requests_total))               # distinct values of one label
```

```yaml
# Stop the damage at ingest: drop the label and cap the target
scrape_configs:
  - job_name: api
    sample_limit: 50000 # a scrape exceeding this fails instead of flooding the TSDB
    metric_relabel_configs:
      - action: labeldrop
        regex: user_uuid|request_id|session_id
```

## Interview tips

- Cardinality being the number of unique time-series created by label combinations.
- Unbounded dimensions (user IDs, IPs, UUIDs) triggering exponential series creation.
- TSDB memory exhaustion (OOM kill) and inverted index bloating.
- Moving high-cardinality metadata into logs or distributed traces instead of metric labels.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?]] (`#687`): [How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?](../infrastructure-monitoring/how-does-node-exporter-collect-linux-host-hardware-and-os-metrics-for-prometheus.md)
- [[What are the Four Golden Signals of Monitoring and how do you monitor them in distributed systems?]] (`#644`): [What are the Four Golden Signals of Monitoring and how do you monitor them in distributed systems?](../site-reliability-engineering/what-are-the-four-golden-signals-of-monitoring-and-how-do-you-monitor-them-in-distributed-systems.md)
- [[What is eBPF-based infrastructure monitoring and how does Cilium provide kernel-level network observability?]] (`#689`): [What is eBPF-based infrastructure monitoring and how does Cilium provide kernel-level network observability?](../infrastructure-monitoring/what-is-ebpf-based-infrastructure-monitoring-and-how-does-cilium-provide-kernel-level-network-observability.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
