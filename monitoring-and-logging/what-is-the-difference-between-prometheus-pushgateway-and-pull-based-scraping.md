---
title: "What is the difference between Prometheus Pushgateway and Pull-based scraping?"
id: 557
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - prometheus
  - metrics
  - pushgateway
  - monitoring
quiz:
  stem: "What critical operational hazard occurs if Prometheus Pushgateway is used to ingest metrics from continuously running services?"
  options:
    - "Prometheus automatically shuts down after 100 pushes"
    - "Pushgateway retains and serves the last reported metric indefinitely, masking service outages because metrics never disappear"
    - "Pushgateway only supports UDP packets"
    - "Metrics sent to Pushgateway cannot be queried using PromQL"
  answer: 2
  explanation: "Pushgateway does not age out or expire metrics. If an instance dies, Pushgateway continues returning its last pushed values to Prometheus forever, masking failures."
---

# What is the difference between Prometheus Pushgateway and Pull-based scraping?

**Short answer:** Prometheus natively pulls metrics at configured scrape intervals from HTTP endpoints; Pushgateway is an intermediary buffer designed strictly for short-lived batch jobs that terminate before the scraper can query them.

## Detail

Prometheus uses a **pull-based** model because it allows the monitoring server to detect whether a target is healthy (`up == 0`), controls scrape frequency, and avoids overwhelming the monitoring backend.

### When to Use Pushgateway

Pushgateway exists solely for **ephemeral batch jobs** (e.g. a nightly 15-second database cleanup script):

1. The batch job completes, pushes its execution metrics to Pushgateway, and terminates.
2. Prometheus periodically scrapes Pushgateway like any other long-running HTTP target.

### Why Pushgateway is NOT an InfluxDB / StatsD Replacement

- **No Automatic Expiration**: Metrics sent to Pushgateway remain there forever until explicitly deleted via API. If a failed job stops reporting, Pushgateway continues serving its last recorded metric indefinitely, masking the failure. The fix is to push a `last_success_timestamp` gauge and alert on its age.
- **Single Point of Failure**: Turning Prometheus into a push architecture creates a massive bottleneck that degrades performance and bypasses health monitoring.
- **Lost `up` signal and instance labels**: Prometheus sees only the Pushgateway as the target, so `up` reflects the gateway, not the job; scrape it with `honor_labels: true` so the pushed `job`/`instance` labels are kept.

For long-running services that cannot be scraped (behind NAT, in another network), use a Prometheus Agent or OpenTelemetry Collector with remote write, or Prometheus 3's OTLP receiver - not Pushgateway.

## Example

```bash
# End of a nightly batch job: push a success timestamp and the row count, grouped by job
cat <<EOF | curl --fail --data-binary @- http://pushgateway:9091/metrics/job/db_cleanup
# TYPE db_cleanup_last_success_timestamp_seconds gauge
db_cleanup_last_success_timestamp_seconds $(date +%s)
# TYPE db_cleanup_rows_deleted gauge
db_cleanup_rows_deleted 48213
EOF
```

```yaml
# Prometheus: scrape the gateway keeping pushed labels, and alert when the job stops succeeding
scrape_configs:
  - job_name: pushgateway
    honor_labels: true
    static_configs: [{ targets: ["pushgateway:9091"] }]
# rule: time() - db_cleanup_last_success_timestamp_seconds > 26 * 3600  -> "cleanup has not succeeded in 26h"
```

## Interview tips

- Prometheus is fundamentally pull-based; detects target outages via pull failure (`up == 0`).
- Pushgateway is strictly for short-lived batch/cron jobs.
- Anti-pattern: using Pushgateway as a general-purpose metric ingestion buffer.
- Stale metrics persisting in Pushgateway unless deleted.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?]] (`#687`): [How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?](../infrastructure-monitoring/how-does-node-exporter-collect-linux-host-hardware-and-os-metrics-for-prometheus.md)
- [[What are the Four Golden Signals of Monitoring and how do you monitor them in distributed systems?]] (`#644`): [What are the Four Golden Signals of Monitoring and how do you monitor them in distributed systems?](../site-reliability-engineering/what-are-the-four-golden-signals-of-monitoring-and-how-do-you-monitor-them-in-distributed-systems.md)
- [[What are Blackbox vs Whitebox monitoring and when should each be used?]] (`#688`): [What are Blackbox vs Whitebox monitoring and when should each be used?](../infrastructure-monitoring/what-are-blackbox-vs-whitebox-monitoring-and-when-should-each-be-used.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
