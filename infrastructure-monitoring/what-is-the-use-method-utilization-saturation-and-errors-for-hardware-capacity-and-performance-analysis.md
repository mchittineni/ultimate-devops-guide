---
title: "What is the USE Method (Utilization, Saturation, and Errors) for hardware capacity and performance analysis?"
id: 686
category: "Infrastructure Monitoring"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - monitoring
  - use-method
  - performance
  - brendan-gregg
quiz:
  stem: "Under Brendan Gregg's USE Method, what does 'Saturation' specifically measure?"
  options:
    - "The physical temperature of the server rack"
    - "The degree to which extra work is queued waiting for a resource because it cannot be serviced immediately"
    - "The total amount of disk space occupied by logs"
    - "The number of users logged into the system"
  answer: 2
  explanation: "Saturation measures extra work that has queued up behind an overloaded resource (e.g. CPU run queue or disk I/O wait queue), which directly causes latency spikes."
---

# What is the USE Method (Utilization, Saturation, and Errors) for hardware capacity and performance analysis?

**Short answer:** Created by Brendan Gregg, the USE Method directs engineers to check Utilization (% time resource was busy), Saturation (queued work waiting for resource), and Errors for every physical and virtual system resource (CPU, memory, disk, network).

## Detail

When an infrastructure performance issue strikes, engineers waste time randomly poking around. The USE Method provides a systematic, exhaustive checklist:

### For Every Resource (CPU, Memory, Storage I/O, Network Interfaces)

1. **Utilization**: What percentage of time was the resource actively busy?
   - CPU: % user + % system.
   - Disk: % util from `iostat -xz`.
2. **Saturation**: How much work is queued waiting because the resource is 100% busy?
   - CPU: Run queue length (`vmstat`, load average).
   - Memory: Page scanning and swapping (`vmstat` `si`/`so`), OOM kills, memory pressure in `/proc/pressure/memory`.
   - Disk: Average queue length (`aqu-sz` in `iostat -x`); rising `r_await`/`w_await` latency is the consequence.
3. **Errors**: Are hardware or software error counters incrementing?
   - Network: Dropped packets, CRC errors in `ip -s link`.
   - Disk: SMART errors, media faults in `dmesg`.

### Why Saturation Matters

A disk at 99% utilization might still be delivering acceptable latency if queues are empty. But once **saturation** occurs (work sits queued waiting for previous I/O to finish), response latency climbs sharply and non-linearly - queueing theory says waiting time grows without bound as utilisation approaches 100%.

**Limitations.** USE is a resource-centric method: it finds the bottlenecked resource quickly but says nothing about user impact, so it pairs with RED (Rate, Errors, Duration) for services. Utilisation also needs care on modern hardware - a multi-queue NVMe device or a hyperthreaded CPU can show "100% busy" with capacity to spare - and software resources (thread pools, connection pools, file descriptors, locks) belong on the checklist as much as hardware.

## Example

```bash
# A 60-second USE pass on a Linux host
uptime                          # load averages: CPU saturation hint (includes D-state tasks)
vmstat 1 5                      # r = run queue (CPU saturation), si/so = swapping, wa
mpstat -P ALL 1 3               # per-CPU utilisation: one hot core hides in the average
free -m                         # memory utilisation
iostat -xz 1 3                  # disk utilisation (%util), saturation (aqu-sz), latency
sar -n DEV,EDEV 1 3             # network utilisation and interface errors
cat /proc/pressure/{cpu,memory,io}   # PSI: direct saturation measurements
dmesg -T | grep -iE 'error|fail|oom' | tail   # errors
```

## Interview tips

- USE checklist: Utilization (% busy), Saturation (queued work), Errors.
- Applying USE to all resources: CPU, Memory, Disk, Network.
- Saturation being the key indicator of performance degradation.
- Formulated by Brendan Gregg.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[How does Docker BuildKit work and what caching and build features does it unlock?]] (`#515`): [How does Docker BuildKit work and what caching and build features does it unlock?](../docker/how-does-docker-buildkit-work-and-what-caching-and-build-features-does-it-unlock.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
