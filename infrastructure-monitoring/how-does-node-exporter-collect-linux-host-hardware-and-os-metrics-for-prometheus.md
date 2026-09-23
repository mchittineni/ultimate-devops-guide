---
title: "How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?"
id: 687
category: "Infrastructure Monitoring"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - monitoring
  - prometheus
  - node-exporter
  - linux
quiz:
  stem: "From which Linux kernel source does Prometheus Node Exporter collect raw CPU and memory metrics?"
  options:
    - "By opening an SSH session to the kernel console"
    - "By reading virtual kernel pseudo-filesystems like `/proc/stat` and `/proc/meminfo`"
    - "By running SQL queries against an embedded SQLite database"
    - "By intercepting BIOS hardware bus interrupts"
  answer: 2
  explanation: "Node Exporter reads the `/proc` and `/sys` virtual filesystems, where the Linux kernel dynamically exposes real-time hardware, process, and memory statistics."
---

# How does Node Exporter collect Linux host hardware and OS metrics for Prometheus?

**Short answer:** Node Exporter is a lightweight daemon that reads Linux kernel diagnostic pseudo-filesystems (`/proc` and `/sys`) and exposes system hardware and OS metrics in plain-text Prometheus format on HTTP port 9100.

## Detail

Node Exporter requires no kernel modules and runs as an unprivileged daemon or Kubernetes DaemonSet (typically with `hostPID`/`hostNetwork` and the host root filesystem mounted read-only, so it sees the host rather than its own container):

### How Node Exporter Gathers Data

Linux exposes deep kernel telemetry as virtual text files:

- **CPU**: Reads `/proc/stat` to calculate jiffies spent in user, system, idle, and iowait states (`node_cpu_seconds_total`).
- **Memory**: Reads `/proc/meminfo` (`node_memory_MemAvailable_bytes`).
- **Disks**: Reads `/proc/diskstats` (`node_disk_read_bytes_total`).
- **Network**: Reads `/proc/net/dev` (`node_network_receive_bytes_total`).
- **Pressure**: Reads `/proc/pressure/*` (`node_pressure_cpu_waiting_seconds_total`) on kernels with PSI.
- **Custom metrics**: The **textfile collector** reads `*.prom` files from a directory, so cron jobs and scripts can publish host-level metrics (e.g. last backup time) without running their own exporter.

Collectors can be enabled or disabled individually (`--collector.systemd`, `--no-collector.wifi`); the trade-off is cardinality - collectors like `systemd` or per-interface network stats on a host with hundreds of virtual interfaces can produce thousands of series per node.

### Essential PromQL Calculations

```promql
# Calculate real CPU utilization percentage across all cores:
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Calculate percentage of disk space used (ignore pseudo filesystems):
100 - ((node_filesystem_avail_bytes{fstype!~"tmpfs|overlay|squashfs"} * 100)
       / node_filesystem_size_bytes{fstype!~"tmpfs|overlay|squashfs"})
```

## Example

```bash
# Run it against the host from a container (pin a release tag in production)
docker run -d --name node-exporter --net=host --pid=host \
  -v "/:/host:ro,rslave" \
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host \
  --collector.textfile.directory=/host/var/lib/node_exporter/textfile

curl -s localhost:9100/metrics | grep -E '^node_(load1|memory_MemAvailable_bytes) '

# Textfile collector: a backup script publishes its own metric atomically
echo "backup_last_success_timestamp_seconds $(date +%s)" > /var/lib/node_exporter/textfile/backup.prom.$$ \
  && mv /var/lib/node_exporter/textfile/backup.prom.$$ /var/lib/node_exporter/textfile/backup.prom
```

On Kubernetes, the `prometheus-node-exporter` Helm chart (included in kube-prometheus-stack) deploys the same thing as a DaemonSet.

## Interview tips

- Scraping Linux `/proc` and `/sys` virtual filesystems.
- Exposing metrics in Prometheus exposition format on port 9100.
- Running as a Kubernetes DaemonSet across all nodes.
- Calculating CPU rate from counter `node_cpu_seconds_total`.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Linux cgroups v2 and how do they improve container resource isolation over cgroups v1?]] (`#514`): [What are Linux cgroups v2 and how do they improve container resource isolation over cgroups v1?](../docker/what-are-linux-cgroups-v2-and-how-do-they-improve-container-resource-isolation-over-cgroups-v1.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
