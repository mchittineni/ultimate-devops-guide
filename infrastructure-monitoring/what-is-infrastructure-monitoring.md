---
title: "What is Infrastructure Monitoring?"
id: 131
category: "Infrastructure Monitoring"
difficulty: "Beginner"
tags:
  - devops
  - infrastructure-monitoring
  - interview-questions
---

# What is Infrastructure Monitoring?

**Short answer:** Infrastructure monitoring is the continuous collection of health and performance signals from the compute, storage, network, and platform layers - hosts, containers, clusters, databases, and cloud services - to detect problems and inform capacity decisions.

## Detail

**What is monitored at each layer**

- **Hosts / nodes** - CPU (including steal time), memory and swap, disk usage, inode usage, I/O wait, load average, network throughput and errors.
- **Containers and orchestration** - pod restarts, OOM kills, CPU throttling, pending pods, node conditions, and control-plane health.
- **Storage** - volume capacity, IOPS and throughput against provisioned limits, latency, and replication status.
- **Network** - packet loss, latency, connection counts, NAT gateway usage, DNS resolution success.
- **Cloud services** - managed database connections and replication lag, queue depth and age, load balancer target health, and service quotas approaching their limits.

**The USE method** structures this well: for every resource, measure **Utilisation** (how busy), **Saturation** (how much queued work) and **Errors**. Saturation is the underrated one - a CPU at 100% utilisation with no run queue is fine; one with a long run queue is not.

**Practical guidance**

- Alert on conditions that require action: disk projected to fill within four hours beats a static "80% full" threshold.
- Watch for the signals people forget: inode exhaustion, file descriptor limits, certificate expiry, and cloud quota limits.
- Use CPU _throttling_ rather than CPU usage for containers with limits - throttling is what actually hurts latency.
- Retain enough history for capacity planning and seasonal comparison.

Infrastructure monitoring is necessary but not sufficient: it tells you a node is unhealthy, not whether users are affected. Pair it with application and SLO monitoring.

## Example

```promql
# Predictive: a filesystem that will be full within 4 hours at the current trend
predict_linear(node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}[6h], 4 * 3600) < 0

# Saturation, not utilisation: containers throttled in more than 25% of CFS periods
sum by (namespace, pod) (rate(container_cpu_cfs_throttled_periods_total[5m]))
  / sum by (namespace, pod) (rate(container_cpu_cfs_periods_total[5m])) > 0.25

# The forgotten ones: inodes and file descriptors
node_filesystem_files_free{fstype!~"tmpfs|overlay"} / node_filesystem_files < 0.1
process_open_fds / process_max_fds > 0.8
```

## Interview tips

- Naming the USE method gives structure to an otherwise list-shaped answer.
- Predictive alerting ("will fill in four hours") over static thresholds is a mature practice.
- Container CPU throttling as the metric that matters is a strong Kubernetes-specific detail.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
