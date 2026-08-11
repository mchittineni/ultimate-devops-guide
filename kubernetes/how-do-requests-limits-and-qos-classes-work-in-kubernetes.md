---
title: "How do requests, limits, and QoS classes work in Kubernetes?"
id: 444
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - cloud-cost-optimization
  - scalability-and-high-availability
---

# How do requests, limits, and QoS classes work in Kubernetes?

**Short answer:** A **request** is what the scheduler reserves - it decides which node a Pod fits on and is what the node's "allocated" figure counts. A **limit** is what the kubelet enforces at runtime through cgroups. The two resources behave completely differently at the limit: **CPU is compressible**, so exceeding the CPU limit means the container is _throttled_, while **memory is not**, so exceeding the memory limit means the container is _OOM-killed_ and restarted. From the request/limit combination Kubernetes derives a **QoS class** - `Guaranteed` (limits equal requests for every resource), `Burstable` (requests set, lower than limits), `BestEffort` (nothing set) - and that class decides eviction order when a node runs out of resources. The practical rules: always set memory request = memory limit, set a CPU request but be very careful with CPU limits, and never ship a container with nothing set.

## Detail

### Scheduling versus enforcement

The scheduler only ever looks at **requests**. A node with 8 vCPU and 32 GiB advertises slightly less as _allocatable_ (kubelet, container runtime, and eviction thresholds are reserved), and the scheduler admits Pods while the **sum of requests** fits. Limits are invisible to it - which is why you can dramatically oversubscribe a node by setting small requests and large limits, and why the node then thrashes.

The exam version of this: _a node has 8 vCPU / 32 GiB; a Pod requests 2 vCPU / 10 GiB and limits 4 vCPU / 16 GiB; the HPA goes to 4 replicas - how many actually run?_ Count requests against allocatable: 4 × 10 GiB = 40 GiB > ~30 GiB usable, so memory is the binding constraint. Three Pods schedule (30 GiB) and the fourth stays `Pending` with `Insufficient memory`. The limits never enter the arithmetic.

### What happens at the limit

|                     | CPU                                                                                                      | Memory                                                                                                            |
| ------------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Mechanism           | CFS quota per 100 ms period                                                                              | cgroup memory limit                                                                                               |
| At the limit        | **Throttled** - the container is descheduled until the next period. Latency spikes, no restart, no event | **OOM-killed** - `reason: OOMKilled`, exit code 137, restart per `restartPolicy`, `CrashLoopBackOff` if it recurs |
| Symptom to look for | `container_cpu_cfs_throttled_seconds_total` climbing while CPU usage sits below the limit                | `kubectl describe pod` showing `Last State: Terminated, Reason: OOMKilled`                                        |
| Advice              | Set requests; set limits only where you must, and not too tight                                          | Always set limit = request                                                                                        |

CPU limits deserve their own warning. A limit of `500m` means 50 ms of CPU per 100 ms period **across all threads**, so a multi-threaded runtime (JVM, Go with a high `GOMAXPROCS`, Node with a worker pool) can burn its whole quota in 10 ms and then stall for 90 ms. That shows up as p99 latency far worse than the average, on a container whose average CPU looks fine. For latency-sensitive services, prefer a correct CPU **request** plus no limit (or a generous one), and let the request-based fair share do the work.

Memory is the opposite: because it cannot be reclaimed, an unbounded container can consume the node and take healthy neighbours with it. Always bound memory.

### QoS classes and eviction order

| Class        | How you get it                                                     | Consequence                                                                  |
| ------------ | ------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `Guaranteed` | Every container has limits == requests for **both** CPU and memory | Evicted last; eligible for exclusive CPUs with the static CPU manager policy |
| `Burstable`  | At least one request set, and not all limits == requests           | Evicted after BestEffort, ordered by how far usage exceeds requests          |
| `BestEffort` | No requests or limits at all                                       | **Evicted first**, and the kernel's preferred OOM victim                     |

Under node memory pressure the kubelet evicts BestEffort first, then Burstable Pods exceeding their requests, then Guaranteed. Setting requests is therefore not merely a scheduling hint - it buys survival. This is also the answer to "why did my Pod get evicted when the node had memory free?": the node crossed an eviction _threshold_, not its total.

### Namespace-level controls (limiting without touching the Deployment)

A classic interview scenario is _how do you limit resource usage without editing the manifest?_ - the answer is namespace objects:

- **`LimitRange`** - injects `default` limits and `defaultRequest` into containers that omit them, and can enforce `min`/`max` and a `maxLimitRequestRatio`. This is what stops BestEffort Pods existing at all.
- **`ResourceQuota`** - caps the namespace total for `requests.cpu`, `limits.memory`, Pod count, PVC count, and per-storage-class storage. Note the trap: once a quota specifies a compute resource, **every** new Pod must set that resource or admission rejects it - which is why LimitRange and ResourceQuota are deployed together.
- **Priority classes and preemption** - give critical workloads a higher `priorityClassName` so they can preempt lower-priority Pods rather than sit `Pending`.

### Sizing them honestly

Guessing is how you end up with both waste and throttling. Measure: `kubectl top`, `container_memory_working_set_bytes` and CPU rate over a week, then set memory request/limit near the p99 working set plus headroom, and the CPU request near the p90 usage. **Vertical Pod Autoscaler in `recommendationOnly` mode** is the low-risk way to get data-driven numbers; running VPA in `Auto` alongside an HPA on the same resource is a known conflict. Over-requesting is the number one cause of a cluster that is 30% utilised and still needs more nodes - it is a cost problem, not just a tidiness problem.

Two runtime-specific notes worth having: a JVM before container-awareness, or without `-XX:MaxRAMPercentage`, sizes its heap from the **host's** memory and gets OOM-killed instantly; and Go's `GOMEMLIMIT`/`GOMAXPROCS` should be aligned to the cgroup, not the node.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  template:
    spec:
      containers:
        - name: api
          image: registry.example.com/api:1.9.0
          resources:
            requests: { cpu: "500m", memory: "512Mi" }
            limits: { memory: "512Mi" } # memory bounded == request; no CPU limit
          env:
            - { name: GOMEMLIMIT, value: "460MiB" } # runtime respects the cgroup
      # a latency-sensitive Pod that must survive node pressure -> Guaranteed
---
apiVersion: v1
kind: LimitRange
metadata: { name: defaults, namespace: team-a }
spec:
  limits:
    - type: Container
      default: { cpu: "500m", memory: "512Mi" } # applied when the manifest omits them
      defaultRequest: { cpu: "100m", memory: "128Mi" }
      max: { cpu: "4", memory: "8Gi" }
      maxLimitRequestRatio: { memory: "1" } # forces memory limit == request
---
apiVersion: v1
kind: ResourceQuota
metadata: { name: team-a-quota, namespace: team-a }
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.memory: 60Gi
    persistentvolumeclaims: "10"
    gp3-retain.storageclass.storage.k8s.io/requests.storage: 500Gi
```

```bash
# Which class did I actually get, and was anything OOM-killed?
kubectl get pod api-7f4c2b -o jsonpath='{.status.qosClass}{"\n"}'
kubectl describe pod api-7f4c2b | grep -A3 "Last State"       # OOMKilled / exit 137
kubectl get events -n prod --field-selector reason=Evicted

# Is this latency problem actually CPU throttling?
kubectl top pod -n prod --containers | sort -k3 -h | tail
# PromQL: throttling ratio per container - anything sustained above ~0.05 is a problem
#   rate(container_cpu_cfs_throttled_periods_total[5m])
# / rate(container_cpu_cfs_periods_total[5m])

# Requests versus reality across the cluster - the cost conversation
kubectl describe node | grep -A6 "Allocated resources"
```

## Interview tips

- Lead with the split: requests are for the **scheduler**, limits are for the **kubelet**. Everything else follows from it.
- Give the asymmetry in one sentence - "CPU is compressible so you get throttled; memory is not so you get OOM-killed" - and name exit code 137 and `OOMKilled`. That is the phrase interviewers wait for.
- Recommend memory limit == request always, and be prepared to argue against tight CPU limits using the CFS-quota explanation. Being able to say _why_ a `500m` limit hurts a multi-threaded service is a senior signal.
- Recite the three QoS classes and, more importantly, what they buy: eviction order. Then answer "why was my Pod evicted with free memory on the node?" with eviction thresholds.
- For "limit resources without changing the Deployment", answer `LimitRange` plus `ResourceQuota`, and mention the trap that a quota on a compute resource makes that resource mandatory for every Pod.
- Do the node arithmetic out loud if they give you numbers - sum the **requests** against allocatable, not the limits, and remember system reserved.
- Close on cost: over-requesting is why clusters sit at low utilisation while the bill grows, and VPA in recommendation mode is how you fix it with data. See [autoscaling workloads and nodes in Kubernetes](./how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md), [node pressure and Pod evictions](./how-do-you-handle-node-pressure-and-pod-evictions-in-kubernetes.md), [Pod stuck in Pending or CrashLoopBackOff](./how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md), and [cutting a cloud bill without hurting reliability](../cloud-cost-optimization/how-do-you-cut-a-cloud-bill-without-hurting-reliability.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [[How do you run an application across multiple Kubernetes clusters?]] (`#414`): [How do you run an application across multiple Kubernetes clusters?](../container-orchestration-advanced/how-do-you-run-an-application-across-multiple-kubernetes-clusters.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
