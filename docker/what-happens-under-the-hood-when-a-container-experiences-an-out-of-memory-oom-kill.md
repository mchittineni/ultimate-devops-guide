---
title: "What happens under the hood when a container experiences an Out Of Memory (OOM) kill?"
id: 516
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - docker
  - memory
  - oom
  - linux-kernel
quiz:
  stem: "Why does a container process killed by the OOM killer typically exit with exit code 137?"
  options:
    - "137 is the standard HTTP error code for memory overload"
    - "Unix processes killed by a signal exit with 128 + signal number; SIGKILL is signal 9 (128 + 9 = 137)"
    - "The Docker daemon reserves exit code 137 for configuration syntax errors"
    - "The kernel sends SIGTERM (signal 15) which maps to code 137"
  answer: 2
  explanation: "Standard Linux shells and container runtimes report process termination due to a signal as 128 + signal_number. SIGKILL is signal 9, resulting in exit code 137."
---

# What happens under the hood when a container experiences an Out Of Memory (OOM) kill?

**Short answer:** A container's memory limit is its cgroup's `memory.max`. When the processes in that cgroup try to allocate past it, the kernel first tries to reclaim memory charged to the cgroup (dropping clean page cache, writing back dirty pages, swapping if allowed). If reclaim cannot get under the limit, the kernel's **memory-cgroup OOM killer** picks a victim inside that cgroup only - the process with the highest `oom_score`, or the whole group if `memory.oom.group` is set - and sends it `SIGKILL`, which cannot be caught. The main process dying ends the container with exit code **137** (128 + 9); Docker records `OOMKilled: true` and Kubernetes records `reason: OOMKilled`. The host and other containers are unaffected - that is the point of the limit - but the application gets no chance to shut down cleanly.

## Detail

**The sequence.**

1. **Charging.** Every page a process in the container touches - anonymous memory (heap, stacks) and page cache for files it reads or writes - is charged to its cgroup. Kernel memory such as socket buffers is charged too.
2. **Hitting the limit.** An allocation or page fault would push usage over `memory.max`. (If `memory.high` is set lower, the kernel throttles and reclaims aggressively above it first; Docker's `--memory-reservation` sets `memory.low`, a protection rather than a limit.)
3. **Reclaim.** The kernel reclaims within the cgroup: drop clean cache, write back and drop dirty cache, swap anonymous pages if `memory.swap.max` allows. Page cache alone therefore rarely causes an OOM kill.
4. **OOM kill.** If reclaim fails, the cgroup OOM killer scores processes in the cgroup (mainly by resident memory, adjusted by `oom_score_adj`) and kills the highest. With `memory.oom.group=1` it kills every process in the cgroup together - the kubelet sets this on cgroup v2 nodes so a container is never left half-alive, and offers a `singleProcessOOMKill` setting to opt out.
5. **Bookkeeping.** The cgroup's `memory.events` increments `oom` and `oom_kill`; the kernel logs `Memory cgroup out of memory: Killed process ...`; the runtime notices the main process exit and marks the container.

**Container OOM versus node OOM.** A container OOM is scoped to one cgroup and triggered by its own limit. A **node** running out of memory is different: the kubelet usually evicts Pods first when `memory.available` crosses its eviction threshold (status `Evicted`, not `OOMKilled`), and if memory runs out faster than that, the kernel's global OOM killer picks victims across the node using `oom_score_adj` values the kubelet sets by QoS class (BestEffort first, Guaranteed last).

**Diagnosing it.**

- Exit code 137 means SIGKILL, not necessarily OOM - check the recorded reason (`OOMKilled`) and `memory.events`, because a liveness-probe kill or `docker kill` also exits 137.
- Look at the working set (`container_memory_working_set_bytes`), not total usage, since total includes reclaimable cache.
- Runtimes that size themselves from the host (old JVMs, Node's default heap) OOM quickly in small containers; set `-XX:MaxRAMPercentage`, `--max-old-space-size`, or `GOMEMLIMIT`.

**Trade-offs.** A hard limit protects neighbours but turns a memory spike into an abrupt crash with no graceful shutdown. Leaving memory unlimited avoids that but lets one container push the whole node into eviction or a global OOM. The usual answer is a limit sized from measured peak usage plus headroom, runtime heap settings below that limit, and alerts on memory approaching the limit before the kill happens.

## Example

```bash
# Reproduce: a 128 MiB limit and a process that allocates 256 MiB
docker run --name oomdemo --memory=128m --memory-swap=128m \
  python:3.13-slim python -c "b = bytearray(256 * 1024 * 1024)"
echo $?                                                   # 137
docker inspect -f '{{.State.OOMKilled}} {{.State.ExitCode}}' oomdemo   # true 137

# Kernel's view
sudo dmesg -T | grep -i "memory cgroup out of memory"

# While a container runs: how close is it to the limit, and has it been OOM-killed?
cg=/sys/fs/cgroup$(cut -d: -f3 /proc/$(docker inspect -f '{{.State.Pid}}' <container>)/cgroup)
cat $cg/memory.current $cg/memory.max
cat $cg/memory.events            # oom / oom_kill counters

# Kubernetes equivalent
kubectl get pod api-7d9f -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}{"\n"}'   # OOMKilled
```

## Interview tips

- Walk the sequence: charge to the cgroup, hit `memory.max`, reclaim, then the cgroup OOM killer sends SIGKILL to the highest-scoring process.
- Explain 137 as 128 + 9, and add that 137 alone does not prove OOM - check `OOMKilled` or `memory.events`.
- Separate a container OOM kill from node-pressure eviction and the global OOM killer.
- Mention `memory.oom.group` and why Kubernetes kills the whole container rather than one process.
- Give the practical fixes: size limits from the working set, and configure runtime heaps (JVM, Node, Go) to stay below the limit.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- [[How do you troubleshoot a Kubernetes Service that has no endpoints?]] (`#403`): [How do you troubleshoot a Kubernetes Service that has no endpoints?](../kubernetes/how-do-you-troubleshoot-a-kubernetes-service-that-has-no-endpoints.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
