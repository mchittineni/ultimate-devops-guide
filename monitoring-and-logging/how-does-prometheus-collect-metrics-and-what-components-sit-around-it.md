---
title: "How does Prometheus collect metrics, and what components sit around it?"
id: 500
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - monitoring-and-logging
  - interview-questions
  - kubernetes
  - infrastructure-monitoring
---

# How does Prometheus collect metrics, and what components sit around it?

**Short answer:** Prometheus **pulls**. It discovers targets (from Kubernetes, cloud APIs, Consul, or static config), then scrapes an HTTP `/metrics` endpoint on each one at a fixed interval and stores the samples in its local time-series database. Around the server sit five kinds of component: **exporters** that translate something that does not speak Prometheus into `/metrics` (`node_exporter` for hosts, `kube-state-metrics` for Kubernetes object state, `blackbox_exporter` for probing endpoints, plus database and application-specific ones); **client libraries** inside your applications exposing metrics natively; **service discovery** so targets are found rather than listed; **Alertmanager**, a separate process that receives fired alerts and handles grouping, inhibition, silencing, and routing to Slack/PagerDuty/email; and **Pushgateway** for the one case pull cannot cover - short-lived batch jobs that exit before anyone can scrape them. Grafana sits on top as the query and dashboard layer. The distinction interviewers probe: **Prometheus evaluates alert rules itself and sends alerts to Alertmanager, which does the routing** - people frequently attribute both jobs to one component.

## Detail

### The pull model, and its consequences

```text
service discovery (Kubernetes API / EC2 / Consul / files)
        │  produces a target list + labels
        ▼
Prometheus  ──scrape every 15-30s──> http://target:9100/metrics   (plain text exposition)
        │        relabelling: drop, keep, rename, add labels
        ├─ TSDB (local disk, ~2h blocks, default 15d retention)
        ├─ recording rules  -> precomputed series
        ├─ alerting rules   -> fired alerts ──> Alertmanager ──> Slack / PagerDuty / email
        └─ remote_write     -> Thanos / Mimir / Cortex / a vendor, for long-term + global view
```

Pull has real advantages: the monitoring system knows the intended target list, so a target that stops responding is an explicit `up == 0` rather than silence; there is no fan-in problem; and any target can be scraped by hand with `curl` for debugging. Its limits are equally real: targets must be reachable **from** Prometheus (so a firewall or NAT in between is a problem), and anything that exits between scrapes is invisible - which is what Pushgateway exists for. Push-based systems (StatsD, OpenTelemetry with OTLP) solve the reverse trade-off.

### The components, and what each is actually for

| Component                     | Runs where                       | What it does                                                                                      | When you need it               |
| ----------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------ |
| **Prometheus server**         | Central, per cluster or per team | Scrape, store, evaluate rules                                                                     | Always                         |
| **node_exporter**             | A DaemonSet or on every host     | Host metrics: CPU, memory, disk, filesystem, network, load                                        | Always, for infrastructure     |
| **kube-state-metrics**        | One Deployment per cluster       | Kubernetes **object state** from the API: Deployment replicas, Pod phase, PVC status, Job success | Always, on Kubernetes          |
| **cAdvisor** (in the kubelet) | Every node                       | **Container resource usage**: CPU, memory working set, throttling                                 | Built in - no separate install |
| **Alertmanager**              | 2-3 replicas, clustered          | Dedupe, group, inhibit, silence, route notifications                                              | As soon as you alert           |
| **Pushgateway**               | One instance                     | Holds metrics pushed by short-lived jobs until scraped                                            | **Only** for batch jobs        |
| **blackbox_exporter**         | Central                          | Probes URLs, TCP ports, DNS, ICMP, and **TLS expiry** from outside                                | For user-facing endpoints      |
| **Client library**            | Inside your app                  | Native `/metrics` with your business and RED metrics                                              | For anything you own           |
| **Grafana**                   | Central                          | Dashboards and ad-hoc querying                                                                    | Always                         |
| **Thanos / Mimir / Cortex**   | Alongside                        | Long-term storage, global query across Prometheis, downsampling, HA dedupe                        | Beyond one cluster or 15 days  |
| **Prometheus Operator**       | Per cluster                      | CRDs (`ServiceMonitor`, `PodMonitor`, `PrometheusRule`) so teams declare scraping                 | Kubernetes at any scale        |

**The most-confused pair**: `kube-state-metrics` reports **desired versus actual state of API objects** (`kube_deployment_status_replicas_available`), while **cAdvisor** reports **actual resource consumption of containers** (`container_memory_working_set_bytes`). "Is my Deployment fully rolled out?" is kube-state-metrics; "is this container about to be OOM-killed?" is cAdvisor. You need both.

### Service discovery and relabelling

Listing targets by hand does not survive autoscaling, so Prometheus queries the platform. In Kubernetes it discovers nodes, pods, services, endpoints, and ingresses, each carrying metadata as labels; **relabel rules** then decide what to scrape and how to label it. This is where most real Prometheus configuration effort goes, and the two rules that matter most are `keep`/`drop` on an annotation or label (so teams opt in rather than everything being scraped) and `metric_relabel_configs` to **drop high-cardinality metrics at ingest** before they cost you memory.

With the Prometheus Operator this becomes declarative: a team ships a `ServiceMonitor` alongside their service and scraping starts, with no change to a central config file. That is the answer to "how is Prometheus set up in your project?" that sounds like a platform rather than a pet.

### Why Prometheus memory grows enormously

Asked as a scenario, and the answer is almost always **cardinality**. Prometheus holds an in-memory index of every active series, and a series is a unique combination of metric name and label values. So a label with unbounded values - a user ID, a request ID, a full URL path with IDs in it, a pod name in a metric that outlives pods, a customer email - multiplies series without limit. A single metric with a `path` label capturing `/orders/12345` creates one series per order.

Diagnose it, do not guess: `prometheus_tsdb_head_series` is the total, `topk(10, count by (__name__)({__name__=~".+"}))` finds the worst metrics, and the `/status/tsdb` page lists the biggest label values. Fix by **dropping the offending label at ingest** with `metric_relabel_configs`, fixing the instrumentation to bucket the value (`/orders/:id`), reducing retention, raising scrape intervals for low-value targets, and - once you are beyond one server - moving long-term storage to Thanos or Mimir with downsampling rather than growing the box. Federation and sharding by team or cluster are the other structural answers. See [controlling metric cardinality and monitoring cost at scale](../infrastructure-monitoring/how-do-you-control-metric-cardinality-and-monitoring-cost-at-scale.md).

### Metric types, and the one people get wrong

**Counter** (monotonically increasing - always use `rate()` on it, never the raw value), **Gauge** (goes up and down - queue depth, memory in use), **Histogram** (pre-defined buckets, aggregatable across instances, which is why `histogram_quantile()` over a histogram is correct and averaging a summary's quantiles is not), and **Summary** (client-side quantiles, cheap but **not aggregatable**). For latency SLOs you want histograms, and increasingly native histograms, precisely because you must aggregate across replicas.

### Alertmanager: the part that decides whether on-call is bearable

Prometheus evaluates rules and fires; **Alertmanager** decides what a human sees. Its four jobs:

- **Grouping** - one notification for "100 pods down in namespace X" instead of 100 pages, keyed by `group_by`.
- **Inhibition** - suppress the symptom when the cause is already firing (a cluster-down alert inhibits every service alert in it).
- **Silences** - time-boxed mutes during maintenance, with a matcher and an owner.
- **Routing** - a tree matching on labels, so `severity: page` goes to PagerDuty and `severity: ticket` goes to Slack, with per-team receivers.

Run it as a **cluster of 2-3 replicas** (they gossip so duplicate alerts from HA Prometheus pairs produce one notification), and always include a **dead-man's-switch**: an always-firing alert whose _absence_ of notification tells you the monitoring pipeline itself has failed. Monitoring that cannot detect its own outage is the most common gap in a real setup.

### Installing it, and what "set up" should mean

The realistic answer for Kubernetes is the **kube-prometheus-stack** Helm chart: Prometheus Operator, Prometheus, Alertmanager, node_exporter, kube-state-metrics, Grafana, and a set of default rules and dashboards, all configured together. Then you add `ServiceMonitor`s per service, `PrometheusRule`s per team, persistent storage with a retention policy, and `remote_write` if you need more than local retention. Saying "I would not hand-roll it; I would use kube-prometheus-stack and then own the rules and dashboards as code" is a better answer than describing a manual install.

## Example

```yaml
# Prometheus Operator: a team declares scraping alongside their service
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: payments
  namespace: prod
  labels: { release: kube-prometheus-stack } # so the operator picks it up
spec:
  selector: { matchLabels: { app: payments } }
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
      metricRelabelings: # drop the cardinality bomb AT INGEST
        - action: labeldrop
          regex: "(user_id|request_id|session_id)"
        - action: drop
          sourceLabels: [__name__]
          regex: "go_gc_duration_seconds.*" # noise nobody queries
```

```yaml
# Alert rules live with the code, not in a UI
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata: { name: payments, namespace: prod }
spec:
  groups:
    - name: payments.slo
      rules:
        - record: job:request_error_rate:ratio5m # recording rule: precompute the expensive bit
          expr: |
            sum(rate(http_requests_total{job="payments",code=~"5.."}[5m]))
            / sum(rate(http_requests_total{job="payments"}[5m]))
        - alert: PaymentsErrorBudgetBurn
          expr: job:request_error_rate:ratio5m > 0.02
          for: 10m
          labels: { severity: page, team: payments }
          annotations:
            summary: "payments 5xx rate {{ $value | humanizePercentage }}"
            runbook_url: https://runbooks.example.com/payments-5xx
        - alert: Watchdog # dead-man's switch: silence here means monitoring is broken
          expr: vector(1)
          labels: { severity: none }
```

```yaml
# Alertmanager: grouping, inhibition, and routing - the difference between alerts and noise
route:
  group_by: [alertname, cluster, namespace] # 100 pods down -> ONE notification
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: slack-default
  routes:
    - matchers: [severity="page"]
      receiver: pagerduty
      continue: false
    - matchers: [severity="ticket"]
      receiver: slack-team
inhibit_rules:
  - source_matchers: [alertname="ClusterDown"] # suppress symptoms when the cause fires
    target_matchers: [severity="page"]
    equal: [cluster]
receivers:
  - name: pagerduty
    pagerduty_configs: [{ service_key: "<key>" }]
  - name: slack-team
    slack_configs: [{ api_url: "<webhook>", channel: "#alerts" }]
```

```bash
# Debug the pipeline in the order it flows
curl -s http://localhost:9100/metrics | head -20            # 1. is the target exposing metrics?
curl -s 'http://prometheus:9090/api/v1/targets' | jq '.data.activeTargets[]
  | select(.health!="up") | {job:.labels.job, url:.scrapeUrl, err:.lastError}'   # 2. scraping?
curl -sG 'http://prometheus:9090/api/v1/query' --data-urlencode 'query=up{job="payments"}'

# 3. why is memory growing? -> cardinality, almost always
curl -sG 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=prometheus_tsdb_head_series'
curl -sG 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=topk(10, count by (__name__)({__name__=~".+"}))'
open http://prometheus:9090/tsdb-status     # biggest label values and series counts

# 4. did the alert fire, and did Alertmanager deliver it?
curl -s http://prometheus:9090/api/v1/rules | jq '.data.groups[].rules[]
  | select(.state=="firing") | {name, state}'
curl -s http://alertmanager:9093/api/v2/alerts | jq '.[] | {name:.labels.alertname, status}'
curl -s http://alertmanager:9093/api/v2/silences | jq '.[] | {matchers, endsAt, createdBy}'
```

## Interview tips

- Say **pull** first and then give both sides: the target list is known so a dead target is an explicit `up == 0`, but targets must be reachable from Prometheus and short-lived jobs need Pushgateway.
- Name the components with a one-line purpose each. The pair to get right is **kube-state-metrics** (Kubernetes object state, from the API) versus **cAdvisor** (container resource usage, from the kubelet) - interviewers use it to check you have actually operated this.
- Be precise that **Prometheus evaluates the rules and fires; Alertmanager groups, inhibits, silences, and routes**. Attributing both to one component is the common error.
- Say Pushgateway is **only** for batch jobs, and that using it as a general push endpoint breaks the staleness model.
- For "Prometheus memory is growing enormously", answer **cardinality** immediately, name the diagnostic queries, and give the fixes in order: drop labels at ingest, fix instrumentation to bucket IDs, reduce retention, then move long-term storage to Thanos/Mimir rather than growing the box.
- Know the four metric types and why **histograms aggregate and summaries do not** - which is why latency SLOs need histograms.
- Describe Alertmanager's grouping and inhibition with a concrete example (one notification for 100 pods, cluster-down inhibiting service alerts), and include a **dead-man's-switch** so you can detect a monitoring outage.
- For "how do you set it up?", say kube-prometheus-stack plus `ServiceMonitor`s and `PrometheusRule`s as code, rather than describing a manual install. That answers the question and shows you think in platforms. See [what is Prometheus](./what-is-prometheus.md), [writing effective PromQL queries and Alertmanager rules](./how-do-you-write-effective-promql-queries-and-alertmanager-rules.md), [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md), and [controlling metric cardinality and monitoring cost at scale](../infrastructure-monitoring/how-do-you-control-metric-cardinality-and-monitoring-cost-at-scale.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What is Infrastructure Monitoring?]] (`#131`): [What is Infrastructure Monitoring?](../infrastructure-monitoring/what-is-infrastructure-monitoring.md)
- [[What are Monitoring Tools?]] (`#132`): [What are Monitoring Tools?](../infrastructure-monitoring/what-are-monitoring-tools.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
