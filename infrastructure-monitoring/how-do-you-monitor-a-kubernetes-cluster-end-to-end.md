---
title: "How do you monitor a Kubernetes cluster end to end?"
id: 772
category: "Infrastructure Monitoring"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - infrastructure-monitoring
  - kubernetes
  - prometheus
  - kube-state-metrics
quiz:
  stem: "Which source tells you that a Deployment has fewer available replicas than desired, as opposed to how much CPU its containers use?"
  options:
    - "node_exporter"
    - "kube-state-metrics, which reports Kubernetes object state from the API server"
    - "cAdvisor in the kubelet"
    - "The blackbox exporter"
  answer: 2
  explanation: "kube-state-metrics turns API objects into metrics such as kube_deployment_status_replicas_available, while cAdvisor reports container resource usage and node_exporter reports host metrics. Cluster monitoring needs all three."
---

# How do you monitor a Kubernetes cluster end to end?

**Short answer:** Monitor it in layers, each with its own data source: the **control plane** (API server latency and errors, etcd health, scheduler backlog), the **nodes** (node_exporter host metrics, kubelet and node conditions), **workloads** (kube-state-metrics for object state such as restarts, pending pods, and replica counts; cAdvisor for container CPU, memory, and throttling), **cluster capacity** (requests against allocatable, not just usage), **cluster services** (CoreDNS, ingress or Gateway API controllers, CNI, certificates), and **events and logs**. The usual implementation is kube-prometheus-stack with the community kubernetes-mixin alerts, plus a log agent and an events exporter. Then page only on user-facing SLOs and a handful of genuinely urgent cluster conditions; most cluster signals are diagnostic, not paging.

## Detail

### The layers and where their data comes from

| Layer             | Source                                                                      | Key signals                                                                                              |
| ----------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Control plane     | API server, etcd, scheduler, controller-manager `/metrics`                  | API request error ratio and p99 latency by verb, etcd leader and WAL fsync latency, pending pods         |
| Nodes             | node_exporter, kubelet, kube-state-metrics                                  | CPU/memory/disk/PSI, `Ready` condition, `MemoryPressure`/`DiskPressure`, kubelet PLEG and runtime errors |
| Workloads (state) | kube-state-metrics                                                          | `CrashLoopBackOff`, restarts, OOMKilled reasons, unavailable replicas, failed Jobs, HPA at max           |
| Workloads (usage) | cAdvisor (in the kubelet)                                                   | `container_memory_working_set_bytes` vs limit, CPU throttling ratio                                      |
| Capacity          | kube-state-metrics                                                          | Sum of requests vs allocatable per resource and node pool; pods unschedulable                            |
| Cluster services  | CoreDNS, ingress/Gateway controller, CNI (e.g. Cilium/Hubble), cert-manager | DNS SERVFAIL rate and latency, edge 5xx, dropped flows, certificate expiry                               |
| Events and logs   | Events exporter, log agent (Alloy, Fluent Bit)                              | `FailedScheduling`, `BackOff`, `Evicted`, image-pull errors; container logs                              |

### What deserves attention

- **Control plane.** API server availability and latency is the cluster's own SLO; the kubernetes-mixin ships burn-rate alerts for it (`KubeAPIErrorBudgetBurn`). etcd is sensitive to disk latency - a p99 WAL fsync above roughly 10 ms is the classic early warning. On managed clusters (EKS, GKE, AKS) you see only part of this, so lean on the provider's control-plane metrics and treat the API server as a dependency with its own SLO.
- **Requests, not usage, decide scheduling.** A cluster at 35% CPU usage can still be unschedulable if requests sum to 95% of allocatable. Track both, per node pool, and alert on pods stuck `Pending` rather than on node CPU.
- **Memory is a limit; CPU is a throttle.** Containers near their memory limit get OOM-killed (watch working set versus limit and `OOMKilled` termination reasons); containers at their CPU limit get throttled, which shows up as latency, not errors.
- **Pod churn creates cardinality.** Every new pod is new series from cAdvisor and kube-state-metrics. Drop unused cAdvisor metrics and labels at scrape time and keep kube-state-metrics' allowlists tight.
- **Monitor the monitoring.** Prometheus itself runs in the cluster, so send its Watchdog alert to an external heartbeat and keep at least one external probe of the cluster's ingress.

### What should page

Page on user-visible SLO burn for the services running on the cluster, plus a short list of cluster conditions that need a human now: API server error-budget burn, etcd without a leader or persistently slow disks, a sustained wave of `NotReady` nodes, and workloads stuck crash-looping in production. Pending pods, throttling, capacity trends, and certificate expiry (with weeks of notice) are tickets.

## Example

```promql
# Control plane: API server error ratio and p99 latency (exclude long-running WATCH/CONNECT)
sum(rate(apiserver_request_total{code=~"5.."}[5m])) / sum(rate(apiserver_request_total[5m]))
histogram_quantile(0.99, sum by (le, verb) (
  rate(apiserver_request_duration_seconds_bucket{verb!~"WATCH|CONNECT"}[5m])))

# etcd: slow disk is the early warning (p99 WAL fsync above ~10 ms)
histogram_quantile(0.99, sum by (le, instance) (rate(etcd_disk_wal_fsync_duration_seconds_bucket[5m]))) > 0.01

# Nodes: not Ready
kube_node_status_condition{condition="Ready", status="true"} == 0

# Workloads: crash loops, OOM kills, and pods that cannot be scheduled
kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"} == 1
kube_pod_container_status_last_terminated_reason{reason="OOMKilled"} == 1
sum by (namespace) (kube_pod_status_phase{phase="Pending"}) > 0

# Capacity: CPU requests of running/pending pods vs allocatable (the scheduler's view)
sum(kube_pod_container_resource_requests{resource="cpu"}
    * on (namespace, pod) group_left () (kube_pod_status_phase{phase=~"Pending|Running"} == 1))
  / sum(kube_node_status_allocatable{resource="cpu"})

# Cluster DNS: share of CoreDNS responses that are SERVFAIL
sum(rate(coredns_dns_responses_total{rcode="SERVFAIL"}[5m])) / sum(rate(coredns_dns_responses_total[5m]))
```

```bash
# The usual starting point: Prometheus Operator, Prometheus, Alertmanager, Grafana,
# node_exporter, kube-state-metrics, and the kubernetes-mixin dashboards and alerts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kps prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Quick checks when something looks wrong
kubectl get --raw '/readyz?verbose' | tail -5         # API server health checks
kubectl top nodes && kubectl top pods -A --sort-by=memory | head
kubectl get events -A --field-selector type=Warning --sort-by=.lastTimestamp | tail -20
```

## Interview tips

- Structure the answer by layer and name the data source for each; mixing up kube-state-metrics (object state), cAdvisor (container usage), and node_exporter (host) is the mistake interviewers listen for.
- Say that scheduling follows requests, not usage, and that you track requests against allocatable per node pool.
- Distinguish memory (OOM kill) from CPU (throttling) behaviour at limits, with the metric for each.
- Treat the API server as an SLO with burn-rate alerts, and mention etcd disk latency as the early warning on self-managed clusters.
- Keep paging narrow: user SLOs plus a few urgent cluster conditions; everything else is a ticket or a dashboard.
- Mention the operational gotchas: pod churn and cAdvisor cardinality, limited control-plane visibility on managed clusters, and an external heartbeat because the monitoring lives in the cluster it watches.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
