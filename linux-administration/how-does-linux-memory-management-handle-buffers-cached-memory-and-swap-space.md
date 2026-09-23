---
title: "How does Linux memory management handle buffers, cached memory, and swap space?"
id: 572
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - linux
  - memory
  - cache
  - swap
  - performance
quiz:
  stem: "Which metric reported by `free -m` represents the actual amount of memory that can be allocated to a new application without forcing the system to swap?"
  options:
    - "`free`"
    - "`available`"
    - "`shared`"
    - "`total`"
  answer: 2
  explanation: "`available` estimates how much memory is available for starting new applications without swapping, combining unused memory with reclaimable page caches."
---

# How does Linux memory management handle buffers, cached memory, and swap space?

**Short answer:** Linux utilizes otherwise idle RAM for page cache and disk buffers to accelerate I/O, reclaiming this memory instantly when applications request it; Swap moves inactive memory pages to disk to free physical RAM for active processes and cache.

## Detail

Junior engineers often panic when `free -m` shows only 100MB 'free' memory, mistaking cached memory for real memory exhaustion.

### Anatomy of `free -m`

```text
               total        used        free      shared  buff/cache   available
Mem:           16000       12000         400         500        3600        3600
Swap:           4000         200        3800
```

- **Used**: Memory actively mapped by processes (anon RSS).
- **Buff/Cache**: Disk blocks and files cached in RAM. **This is healthy!** Unused RAM is wasted RAM. If an app requests 2GB, the kernel immediately evicts clean cache without latency.
- **Available**: The true metric to watch! Represents memory that can be allocated to applications without swapping (free + reclaimable cache).

### Swappiness (`vm.swappiness`)

Controls how aggressively the kernel swaps anonymous memory vs reclaiming page cache (value 0 to 100, default 60):

- Low value (10): Avoid swapping unless memory pressure is severe (common for databases like PostgreSQL/Redis).
- Kubernetes nodes traditionally required swap disabled (`swapoff -a`). Node swap support (KEP-2400) went GA in Kubernetes 1.34: on cgroup v2 nodes the kubelet can run with `LimitedSwap`, letting Burstable Pods swap in proportion to their memory request, but the default is still `NoSwap`, so most clusters behave as before unless you opt in.

### Pressure, Reclaim, and the OOM Killer

When free memory falls below the zone watermarks, `kswapd` reclaims in the background: clean page cache is dropped cheaply, dirty pages are written back first, and anonymous pages can only go to swap. If reclaim cannot keep up, allocations stall in _direct reclaim_ (visible as latency and in PSI `/proc/pressure/memory`), and as a last resort the OOM killer terminates the process with the highest `oom_score`. In containers the same happens per cgroup against `memory.max`. The trade-off with swap: a little swap lets the kernel evict truly idle anonymous pages and keep more useful cache, but heavy swapping of hot pages (thrashing) is far worse than a clean OOM kill - which is why latency-sensitive services often run with little or no swap and alert on PSI instead.

## Example

```bash
free -h                                        # read "available", not "free"
grep -E 'MemAvailable|^Cached|Dirty|SwapCached' /proc/meminfo
vmstat 1 5                                     # si/so > 0 continuously = active swapping
cat /proc/pressure/memory                      # PSI: % of time tasks stalled on memory
sysctl vm.swappiness                           # default 60 on most distributions
sudo sysctl -w vm.swappiness=10                # prefer dropping cache over swapping (persist in /etc/sysctl.d/)

# Who is actually using swap?
for f in /proc/[0-9]*/status; do awk '/^Name|^VmSwap/ {printf "%s ", $2} END {print ""}' "$f"; done \
  | sort -k2 -n | tail -5

# Container view: the cgroup, not the host
cat /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.events
```

## Interview tips

- Say "watch `available`, not `free`" in the first sentence: page cache is reclaimable, so low free memory on a busy host is normal and healthy.
- Distinguish **buffers** (block-device metadata) from **cache** (file contents), and **clean** pages (dropped instantly) from **dirty** pages (must be written back first) - reclaim cost depends on that difference.
- Explain swap as a tool, not a failure: modest swap lets idle anonymous pages leave RAM; sustained `si`/`so` or rising PSI means thrashing and a real shortage.
- Know the Kubernetes position: swap support is GA since 1.34 but off (`NoSwap`) by default; memory limits are enforced per cgroup, and exceeding `memory.max` means an OOM kill (exit code 137).
- Never suggest `echo 3 > /proc/sys/vm/drop_caches` as a fix - it throws away useful cache and only hides the question of what is using memory.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[When do you use Bash and when do you use Python?]] (`#301`): [When do you use Bash and when do you use Python?](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)
- [[What is Git Branching Strategy?]] (`#47`): [What is Git Branching Strategy?](../version-control/what-is-git-branching-strategy.md)
- [[How do you recover lost commits using the Git Reflog?]] (`#579`): [How do you recover lost commits using the Git Reflog?](../version-control/how-do-you-recover-lost-commits-using-the-git-reflog.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
