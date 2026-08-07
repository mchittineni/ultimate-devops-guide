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

## Interview tips

- Naming the USE method gives structure to an otherwise list-shaped answer.
- Predictive alerting ("will fill in four hours") over static thresholds is a mature practice.
- Container CPU throttling as the metric that matters is a strong Kubernetes-specific detail.

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
