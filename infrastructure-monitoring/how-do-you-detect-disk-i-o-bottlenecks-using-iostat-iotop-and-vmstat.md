---
title: "How do you detect Disk I/O bottlenecks using iostat, iotop, and vmstat?"
id: 690
category: "Infrastructure Monitoring"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - linux
  - disk-io
  - performance
  - iostat
  - vmstat
quiz:
  stem: "When inspecting `iostat -xz 1`, which metric provides the most accurate indicator of real disk I/O response latency (including queue time)?"
  options:
    - "`r/s`"
    - "`await`"
    - "`svctm`"
    - "`wMB/s`"
  answer: 2
  explanation: "`await` measures the average time in milliseconds that read and write requests spent both waiting in the OS device queue and being serviced by the physical drive."
---

# How do you detect Disk I/O bottlenecks using iostat, iotop, and vmstat?

**Short answer:** Disk I/O bottlenecks are identified using `iostat -xz 1` to check `%util` (device busy percentage) and `await` (average I/O latency in ms), `vmstat 1` to observe `wa` (CPU wait time) and blocked processes (`b`), and `iotop` to pinpoint the specific process hogging disk throughput.

## Detail

When disk storage cannot keep up with write/read demand, CPU cores sit idle waiting for disk blocks, causing severe system degradation:

### Diagnostic Workflow

1. **`vmstat 1`**:
   - Check **`wa` (iowait)**: High `%wa` (> 20%) means CPUs are idle while I/O is outstanding. It is a hint, not a measurement - on many-core machines it can stay low while one disk is saturated.
   - Check **`b` column**: Number of processes blocked in uninterruptible disk sleep (`D` state).
2. **`iostat -xz 1`**:

   ```text
   Device    r/s    w/s   rMB/s   wMB/s  r_await  w_await  aqu-sz  %util
   nvme0n1  10.0  500.0    0.1    50.0     0.40    45.20   22.60  98.50
   ```

   - **`%util`**: Percentage of time the disk was servicing requests. On a single spinning disk, `%util > 90%` means it is near saturation (see the caveat below for SSD/NVMe).
   - **`r_await` / `w_await`**: The average time (in milliseconds) for read/write requests to complete (queue time + service time); older sysstat versions show a combined `await`. For NVMe/SSD, single-digit milliseconds or less is normal; a `w_await` of 45ms indicates heavy saturation.
   - **`aqu-sz`**: Average queue length - the saturation signal.
   - **Caveats**: `%util` only means "the device had at least one request in flight"; NVMe and SSD arrays serve many requests in parallel, so 100% `%util` does not mean the device is maxed out - trust latency and queue size more. `svctm` was deprecated as inaccurate and removed from recent sysstat releases. On cloud volumes, also check provisioned IOPS/throughput limits (e.g. EBS burst balance), because throttling there looks like latency with low `%util`.

3. **`iotop -oP`**:
   - Displays running processes sorted by real-time disk read/write bandwidth, pinpointing the exact process causing the bottleneck (needs root; `pidstat -d 1` from sysstat is an alternative).
4. **Pressure Stall Information (`/proc/pressure/io`)**, on kernels 4.20+: the share of time tasks were stalled on I/O, which is a more direct saturation signal than iowait and is exported by node_exporter (`node_pressure_io_waiting_seconds_total`).

## Example

```bash
vmstat 1 5                      # wa and b columns: is anything blocked on I/O?
iostat -xz 1 5                  # per-device r_await/w_await, aqu-sz, %util (sysstat package)
sudo iotop -oPa                 # only processes doing I/O, accumulated totals
cat /proc/pressure/io           # some/full stall percentages over 10s/60s/300s
```

```promql
# The same questions in Prometheus with node_exporter
rate(node_disk_io_time_weighted_seconds_total[5m])                       # ~ average queue size
rate(node_disk_write_time_seconds_total[5m]) / rate(node_disk_writes_completed_total[5m])  # write latency (s)
rate(node_pressure_io_waiting_seconds_total[5m])                         # I/O pressure stall
```

## Interview tips

- `vmstat` showing high `%wa` (CPU wait) and blocked processes (`b`).
- `iostat -xz` measuring `%util` (saturation) and `await` (I/O latency in ms).
- `await` thresholds: single-digit ms for SSD/NVMe vs tens of ms indicating queue buildup.
- `iotop` to identify the rogue process consuming I/O bandwidth.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[What are Linux cgroups v2 and how do they improve container resource isolation over cgroups v1?]] (`#514`): [What are Linux cgroups v2 and how do they improve container resource isolation over cgroups v1?](../docker/what-are-linux-cgroups-v2-and-how-do-they-improve-container-resource-isolation-over-cgroups-v1.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
