---
title: "How do you monitor Azure with Azure Monitor and KQL?"
id: 205
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
---

# How do you monitor Azure with Azure Monitor and KQL?

**Short answer:** Azure Monitor has two data planes — a metrics store for cheap, high-resolution numeric time series, and Log Analytics for structured logs and traces queried with KQL. You route platform logs there with diagnostic settings (ideally enforced by policy), instrument applications with Application Insights via OpenTelemetry, and alert on either metrics or scheduled KQL queries.

## Detail

**Metrics versus logs, and why the split matters.** Platform metrics are collected automatically, retained free for 93 days, and are the right target for fast, cheap alerts (CPU, request count, queue depth). Logs must be explicitly routed, are billed per GB ingested and retained, and are where you answer "what actually happened". Alerting on a metric where a metric exists is materially cheaper than a log query alert.

**Diagnostic settings are the plumbing everyone forgets.** No resource sends logs anywhere by default. Each resource needs a diagnostic setting pointing at a Log Analytics workspace (query), a storage account (cheap retention), or Event Hubs (streaming to a SIEM). Enforce it with a `DeployIfNotExists` policy at the management group so new resources are covered without asking teams.

**Workspace design.** Fewer workspaces is generally better — cross-workspace queries are possible but clumsier, and Sentinel works best with consolidated data. Use table-level retention and the Basic/Auxiliary log tiers for high-volume, low-value tables (verbose firewall or CDN logs) and Analytics tier for what you query interactively. Commitment tiers cut the per-GB price once volume is predictable.

**KQL is the skill being tested.** The idiom is a pipeline: filter early (`where` on time first, since time is the partition key), then project only needed columns, then summarise. `summarize ... by bin(TimeGenerated, 5m)` is the workhorse for trends; `join kind=leftouter` correlates across tables; `_ResourceId` links back to resources. Filtering late over a large table is the difference between a two-second query and a timeout.

**Application Insights via OpenTelemetry.** The Azure Monitor OpenTelemetry distro is the current recommended instrumentation path, giving traces, metrics, and logs with vendor-neutral SDKs. Sampling is essential at volume — ingestion sampling to control cost, plus keeping all failed requests so error investigation is not sampled away.

**Alerts.** Metric alerts (with dynamic thresholds when the baseline is seasonal), log search alerts for anything requiring correlation, activity-log alerts for control-plane changes such as a firewall rule modification, and action groups routing to a paging tool. Alert-processing rules suppress noise during maintenance windows, which is how you avoid the "everyone ignores Azure alerts" outcome.

## Example

```kusto
// Failed dependency calls by target, 5-minute buckets — filter first, then summarise
AppDependencies
| where TimeGenerated > ago(6h)
| where Success == false
| summarize failures = count(), p95_ms = percentile(DurationMs, 95)
    by Target, bin(TimeGenerated, 5m)
| order by failures desc
```

```kusto
// Control-plane audit: who changed network security rules in the last 7 days?
AzureActivity
| where TimeGenerated > ago(7d)
| where OperationNameValue has "MICROSOFT.NETWORK/NETWORKSECURITYGROUPS"
| where ActivityStatusValue == "Success"
| project TimeGenerated, Caller, OperationNameValue, _ResourceId
| order by TimeGenerated desc
```

## Interview tips

- Explain the metrics/logs split and cost consequence — it is the practical judgement being probed.
- "Filter on TimeGenerated first" is the KQL performance answer; be ready to write a small query on a whiteboard.
- Expect: "how do you guarantee every resource sends logs?" — a `DeployIfNotExists` Azure Policy, not a checklist.

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
