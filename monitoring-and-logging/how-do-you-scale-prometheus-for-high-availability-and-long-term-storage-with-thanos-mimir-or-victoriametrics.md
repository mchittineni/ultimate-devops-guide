---
title: "How do you scale Prometheus for high availability and long-term storage with Thanos, Mimir, or VictoriaMetrics?"
id: 768
category: "Monitoring and Logging"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - monitoring-and-logging
  - prometheus
  - thanos
  - mimir
  - victoriametrics
quiz:
  stem: "Two identical Prometheus replicas scrape the same targets for high availability. What stops dashboards built on Thanos or Mimir from showing every series twice?"
  options:
    - "Prometheus replicas elect a leader and only the leader stores samples"
    - "Each replica sets a distinct replica external label, and the query layer (Thanos Querier) or ingest layer (Mimir HA tracker) deduplicates on it"
    - "Alertmanager deletes duplicate series after each scrape"
    - "Object storage automatically merges identical blocks on upload"
  answer: 2
  explanation: "Prometheus has no clustering, so HA pairs produce duplicate data by design. A per-replica external label lets Thanos deduplicate at query time and Mimir's HA tracker accept samples from only one replica per cluster at ingest."
---

# How do you scale Prometheus for high availability and long-term storage with Thanos, Mimir, or VictoriaMetrics?

**Short answer:** A single Prometheus server is deliberately simple: local disk, no replication, no clustering, typically weeks of retention. You get **high availability** by running two identical replicas and deduplicating, and **long-term, global storage** by shipping data to a horizontally scalable backend. **Thanos** bolts onto existing Prometheus servers (a sidecar uploads 2-hour TSDB blocks to object storage, and a global querier deduplicates and fans out). **Grafana Mimir** (and its predecessor Cortex) is a multi-tenant cluster that Prometheus `remote_write`s into, storing blocks in object storage. **VictoriaMetrics** is a separate, very resource-efficient TSDB that also accepts remote write, stored on block disks rather than object storage. Pick on operating model: keep Prometheus as the store and add a global view (Thanos sidecar), or turn Prometheus into a stateless collector and run a central metrics service (Mimir, VictoriaMetrics, Thanos Receive, or a managed service).

## Detail

### Why a single Prometheus stops being enough

- **No HA.** If the server restarts, you lose scrapes and alert evaluation for that window.
- **Bounded retention.** Local TSDB on one disk; months of high-cardinality data does not fit, and a lost volume loses the history.
- **No global view.** One server per cluster or region means no single query for "error rate across all clusters".
- **Vertical limits.** Memory scales with active series; past a few million series, one box gets expensive and slow to restart (WAL replay).

**Federation** (a global Prometheus scraping `/federate` from others) only works for a small set of pre-aggregated series; it is not a long-term storage answer.

### The HA pattern every option shares

Run two identical Prometheus replicas with the same config, differing only in a replica external label (`replica: 0` / `replica: 1`). Alertmanager is clustered and deduplicates the alerts both replicas fire. The storage layer then removes the duplicate series:

- **Thanos Querier** deduplicates at **query time** on the replica label (`--query.replica-label`), filling gaps from one replica with data from the other.
- **Mimir's HA tracker** deduplicates at **ingest**: per `cluster` label it accepts samples from one elected replica (`__replica__` label) and drops the other until the leader stops sending.

### The options compared

|                       | Thanos (sidecar)                                                                | Grafana Mimir                                                      | VictoriaMetrics                                       |
| --------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------- |
| How data arrives      | Sidecar uploads Prometheus's own 2 h blocks; or Thanos Receive for remote write | `remote_write` to distributors                                     | `remote_write` (or its own `vmagent` scraper)         |
| Storage               | Object storage (S3, GCS, Azure Blob)                                            | Object storage, with ingesters holding recent data                 | Local/block disks; `vmbackup` to object storage       |
| Recent data served by | The Prometheus servers themselves                                               | Ingesters (replication factor 3)                                   | `vmstorage` nodes                                     |
| Multi-tenancy         | Limited (labels, Receive tenants)                                               | Native (`X-Scope-OrgID`), per-tenant limits                        | Cluster version: account IDs in the URL               |
| Downsampling          | Compactor: 5 m and 1 h resolutions                                              | Not by default (relies on cheap object storage and query sharding) | Enterprise feature                                    |
| Query language        | PromQL                                                                          | PromQL                                                             | MetricsQL (a PromQL superset)                         |
| Operational shape     | Incremental: keep existing Prometheus                                           | A distributed system with many components                          | Fewest moving parts; single-node mode goes a long way |

**Thanos components:** sidecar (uploads blocks, serves recent data via the Store API), Store Gateway (serves historical blocks from the bucket), Querier (global PromQL, dedup), Query Frontend (splitting and caching), Compactor (compaction, downsampling, retention; run exactly one per bucket), Ruler (rules over global data). The sidecar requires Prometheus's local compaction to be disabled (min and max block duration both `2h`) so it uploads raw blocks.

**Mimir components:** distributor (validates, applies limits, shards by series), ingester (in-memory recent data, writes blocks to object storage), querier, query-frontend and query-scheduler, store-gateway, and compactor. Newer Mimir releases can also run an ingest-storage architecture with a Kafka-compatible log between the write and read paths, which decouples them further.

### Trade-offs to say out loud

- **Remote write moves the failure domain.** Prometheus buffers in its WAL (roughly two hours), so a backend outage longer than that loses data; size and monitor `prometheus_remote_storage_*` metrics, especially pending samples and failed sends.
- **Sidecar keeps alerting local.** With the Thanos sidecar, each Prometheus still evaluates its own alerts, so a central outage does not stop paging. With a pure remote-write design, decide whether rules run in the agents or centrally (Mimir ruler) and what happens when the centre is down.
- **Agent mode** (`prometheus --agent`, Grafana Alloy, or an OTel Collector) is the natural edge for central backends: scrape and remote write only, no local querying, little memory.
- **Cost is cardinality, not retention.** Object storage makes long retention cheap; ingester memory and per-series index cost are what scale your bill. Per-tenant series limits are the guardrail.
- **Managed equivalents** (Amazon Managed Service for Prometheus, Google Cloud Managed Service for Prometheus, Grafana Cloud, Azure Monitor managed Prometheus) trade per-sample pricing for not operating any of this.

## Example

```yaml
# prometheus.yml on each HA replica (only __replica__ differs): remote write into Mimir
global:
  scrape_interval: 30s
  external_labels:
    cluster: prod-eu-1 # Mimir HA tracker groups replicas by this label...
    __replica__: prometheus-0 # ...and dedupes on this one (dropped before storage)
remote_write:
  - url: http://mimir-distributor.mimir.svc:8080/api/v1/push
    headers:
      X-Scope-OrgID: platform # tenant
    queue_config:
      max_samples_per_send: 2000
```

```bash
# Thanos alternative: keep Prometheus as the store, add a sidecar and a global querier
prometheus --storage.tsdb.min-block-duration=2h --storage.tsdb.max-block-duration=2h \
  --storage.tsdb.path=/prometheus --config.file=/etc/prometheus/prometheus.yml

thanos sidecar --tsdb.path=/prometheus --prometheus.url=http://localhost:9090 \
  --objstore.config-file=/etc/thanos/bucket.yml

thanos query --endpoint=prometheus-0-sidecar:10901 --endpoint=prometheus-1-sidecar:10901 \
  --endpoint=thanos-store:10901 --query.replica-label=replica
```

```promql
# Is remote write keeping up? Seconds between the newest ingested sample and the newest sample
# sent, per remote endpoint (the expression behind the PrometheusRemoteWriteBehind alert)
max_over_time(prometheus_remote_storage_highest_timestamp_in_seconds[5m])
  - ignoring(remote_name, url) group_right
max_over_time(prometheus_remote_storage_queue_highest_sent_timestamp_seconds[5m])
  > 120
```

## Interview tips

- Start with what Prometheus is not: no replication, no clustering, local disk. Then separate the two problems - HA (replica pairs plus dedup) and long-term/global storage (a backend).
- Explain dedup precisely: a replica external label, removed at query time by Thanos or at ingest by Mimir's HA tracker.
- Contrast the models: Thanos sidecar extends the Prometheus you have; Mimir and VictoriaMetrics make Prometheus a collector feeding a central service.
- Mention the remote-write buffer limit (WAL, about two hours) and that a long backend outage drops data - and how you would monitor it.
- Cost follow-up: retention is cheap in object storage, active series are expensive; per-tenant limits and dropping labels at ingest control it.
- Expect "what would you choose?": a few clusters and an existing estate - Thanos sidecar; many teams needing multi-tenancy and limits - Mimir or a managed service; small team wanting efficiency - VictoriaMetrics. Give a reason, not a favourite.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?]] (`#687`): [How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?](../infrastructure-monitoring/how-does-node-exporter-collect-linux-host-hardware-and-os-metrics-for-prometheus.md)
- [[How do you monitor a Kubernetes cluster end to end?]] (`#772`): [How do you monitor a Kubernetes cluster end to end?](../infrastructure-monitoring/how-do-you-monitor-a-kubernetes-cluster-end-to-end.md)
- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
