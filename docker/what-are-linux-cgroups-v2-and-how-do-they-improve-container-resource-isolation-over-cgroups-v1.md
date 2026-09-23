---
title: "What are Linux cgroups v2 and how do they improve container resource isolation over cgroups v1?"
id: 514
category: "Docker"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - docker
  - linux
  - cgroups
  - kernel
quiz:
  stem: "Which problem with container I/O throttling did Linux cgroups v2 resolve that existed in cgroups v1?"
  options:
    - "cgroups v1 could only throttle network packets, not disk writes"
    - "In v1, buffered page cache writes were not attributed to the container, allowing write starvation of the host"
    - "cgroups v1 prohibited the use of NVMe solid-state storage"
    - "cgroups v2 requires containers to run with root privileges to throttle disk reads"
  answer: 2
  explanation: "In cgroups v1, asynchronous buffered writes through the page cache lost their cgroup association, preventing effective I/O limits. v2 unified memory and I/O tracking."
---

# What are Linux cgroups v2 and how do they improve container resource isolation over cgroups v1?

**Short answer:** Control groups (cgroups) are the kernel feature that limits and accounts for a group of processes' CPU, memory, I/O, and PIDs - they are how container resource limits are enforced. cgroups v2 replaces v1's separate hierarchy per controller with **one unified hierarchy** in which every process sits in exactly one cgroup for all controllers. That makes cross-resource behaviour correct - most importantly, buffered writes are charged to the cgroup that dirtied the page cache, so I/O limits actually work - and adds better interfaces: `memory.high` soft throttling before OOM, Pressure Stall Information (PSI), safe delegation to unprivileged users for rootless containers, and cgroup-aware OOM handling. v2 is now the baseline: from Kubernetes 1.35 the kubelet refuses to start on cgroup v1 nodes by default.

## Detail

**What was wrong with v1.** Each controller (`cpu`, `memory`, `blkio`, `pids`, ...) had its own tree under `/sys/fs/cgroup/<controller>/`, and a process could be in different groups in each. Controllers could not cooperate: page-cache writeback was issued by kernel threads, not the container, so `blkio` limits did not apply to buffered writes and one container could saturate the disk. Memory limits were a hard cliff with no reliable soft limit, and delegating a subtree to an unprivileged user was unsafe.

**What v2 changes.**

| Area             | cgroups v1                                         | cgroups v2                                                                                           |
| ---------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Hierarchy        | One tree per controller                            | Single tree at `/sys/fs/cgroup`, controllers enabled per subtree via `cgroup.subtree_control`        |
| Buffered I/O     | Not attributed to the writer; limits bypassed      | Writeback charged to the owning cgroup, so `io.max` and `io.weight` apply                            |
| Memory           | `memory.limit_in_bytes` (hard) and weak soft limit | `memory.max` (hard OOM), `memory.high` (throttle and reclaim first), `memory.min`/`low` (protection) |
| CPU              | `cpu.cfs_quota_us`, `cpu.shares`                   | `cpu.max` ("quota period"), `cpu.weight`                                                             |
| Pressure metrics | None                                               | PSI per cgroup: `cpu.pressure`, `memory.pressure`, `io.pressure`                                     |
| OOM              | Kills a single process                             | `memory.oom.group` can kill the whole group together                                                 |
| Delegation       | Unsafe for unprivileged users                      | Designed for delegation, which rootless Docker and Podman rely on                                    |

**Where it matters for containers.**

- Docker, containerd, and CRI-O use v2 with the systemd cgroup driver on modern distributions; the kubelet and runtime must use the same driver.
- Kubernetes uses v2 features such as `memory.high` for the Memory QoS feature and PSI metrics, and newer runtimes read PSI to report node pressure.
- Runtimes inside containers must be cgroup v2-aware to size themselves correctly - JDK 11.0.16+ and 17+, Go's `GOMAXPROCS` defaults since Go 1.25, and recent Node versions read v2 limits; older runtimes may see host resources.
- The move is essentially complete: current RHEL, Ubuntu, Debian, and Fedora default to v2, systemd is removing v1 support, and Kubernetes 1.35 made v1 nodes fail to start unless you explicitly opt back in (with v1 support scheduled for removal).

**Trade-offs.** Migrating old nodes can break agents that hard-code v1 paths (older monitoring, security, or Java versions). `memory.high` throttling can make a workload slow rather than killed, which is better for availability but can hide a sizing problem - watch PSI and throttling metrics rather than only OOM counts.

## Example

```bash
# Which version is this host running?
stat -fc %T /sys/fs/cgroup        # cgroup2fs = v2, tmpfs = v1 or hybrid
docker info --format '{{.CgroupVersion}} {{.CgroupDriver}}'   # e.g. "2 systemd"

# Limits for a running container, as the kernel sees them
docker run -d --name demo --memory=512m --memory-reservation=384m --cpus=1 nginx:1.29
cg=/sys/fs/cgroup$(cut -d: -f3 /proc/$(docker inspect -f '{{.State.Pid}}' demo)/cgroup)
cat $cg/memory.max $cg/memory.low $cg/cpu.max   # 536870912 / 402653184 / 100000 100000
cat $cg/memory.pressure                          # PSI: some/full stall percentages
cat $cg/cpu.stat | grep throttled                # CPU quota throttling counters
```

## Interview tips

- Start with the structural change: one unified hierarchy instead of a tree per controller.
- Give the concrete fix that matters: buffered writeback is attributed to the right cgroup, so I/O limits work.
- Name the new interfaces - `memory.high`, `memory.min`/`low`, PSI, `memory.oom.group` - and what each is for.
- Connect it to rootless containers through safe delegation.
- Show you are current: v2 is the default everywhere, and Kubernetes 1.35 refuses cgroup v1 nodes by default, so v1 is now a migration problem, not a choice.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[What is a Pod in Kubernetes?]] (`#13`): [What is a Pod in Kubernetes?](../kubernetes/what-is-a-pod-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
