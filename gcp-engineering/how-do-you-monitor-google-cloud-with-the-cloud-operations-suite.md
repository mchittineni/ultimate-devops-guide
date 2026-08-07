---
title: "How do you monitor Google Cloud with the Cloud Operations Suite?"
id: 212
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - gcp-engineering
  - interview-questions
---

# How do you monitor Google Cloud with the Cloud Operations Suite?

**Short answer:** Cloud Monitoring holds metrics, Cloud Logging holds logs with sinks that route them onward, and Cloud Trace, Profiler, and Error Reporting cover request traces, CPU/heap profiles, and exception grouping. The distinctive pieces are log-based metrics (turn a log pattern into a time series), log sinks with exclusions (control cost and export to BigQuery), and a native SLO/burn-rate API in Cloud Monitoring.

## Detail

**Metric scopes let one project see many.** A monitoring metric scope aggregates metrics from multiple projects, so a platform team gets one dashboard across the estate without duplicating configuration. Logging is the mirror image: sinks at the folder or organisation level, with `--include-children`, aggregate logs centrally.

**Sinks, exclusions, and the cost lever.** All logs flow into the `_Default` bucket, which is billed by volume. The pattern that controls cost: exclusion filters remove high-volume, low-value entries (health checks, load-balancer 200s) before ingestion, while a BigQuery or Cloud Storage sink retains what must be queryable long-term at a much lower price. Audit logs — admin activity is free and always on, data access must be enabled and is chargeable — should be routed to a locked-down project.

**Log-based metrics are the feature to name.** A counter or distribution metric derived from a log filter turns "count of `payment declined` entries per minute" or a latency extracted from a log field into a proper metric you can alert on and chart, without changing application code. It is the quickest path from a log you already have to an alert you need.

**Cloud Monitoring has native SLOs.** You define a service, an SLI (request-based or windows-based), and a goal, and the API exposes error-budget burn — meaning multi-window burn-rate alerting without hand-maintaining PromQL. For teams already standardised on Prometheus, Google Cloud Managed Service for Prometheus ingests Prometheus metrics at scale and is queryable with PromQL, which is often the better fit for GKE-centric platforms.

**Alerting policies** combine a condition (metric threshold, absence of data, log match, or SLO burn) with notification channels. Two details matter: alert on _absence_ of data for things that should always report (a silent exporter looks healthy), and configure auto-close carefully so incidents do not resolve themselves while still broken.

**Instrumentation.** OpenTelemetry is the recommended path for traces and custom metrics, exporting to Cloud Trace and Cloud Monitoring. Trace sampling defaults are low — raise it for low-traffic critical paths and keep all error traces, otherwise the trace you want during an incident was sampled away.

## Example

```bash
# Log-based metric: count payment declines per minute from existing logs
gcloud logging metrics create payment_declines \
  --description="Declined payment authorisations" \
  --log-filter='resource.type="cloud_run_revision"
    AND jsonPayload.event="payment_declined"
    AND severity>=WARNING'

# Cut ingest cost: exclude successful health checks from the default bucket
gcloud logging sinks update _Default \
  --add-exclusion=name=drop-healthz,filter='httpRequest.requestUrl:"/healthz"
    AND httpRequest.status=200'

# Retain everything queryable and cheap in BigQuery
gcloud logging sinks create logs-to-bq \
  bigquery.googleapis.com/projects/logging-prod/datasets/platform_logs \
  --log-filter='severity>=INFO' --include-children --organization=123456789
```

## Interview tips

- Log-based metrics and sink exclusions are the two GCP-specific answers that show real usage.
- Mention the native SLO API — and Managed Service for Prometheus if the platform is GKE-based.
- Expect: "how do you notice a broken exporter?" — alert on metric absence, not just thresholds.

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
