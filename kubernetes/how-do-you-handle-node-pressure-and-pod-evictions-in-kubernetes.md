---
title: "How do you handle node pressure and Pod evictions in Kubernetes?"
id: 409
category: "Kubernetes"
difficulty: "Advanced"
tags:
  - devops
  - kubernetes
  - interview-questions
  - scalability-and-high-availability
  - infrastructure-monitoring
---

# How do you handle node pressure and Pod evictions in Kubernetes?

**Short answer:** Understand which mechanism evicted the Pod, because the fixes differ. **The kubelet** evicts under node pressure (memory, disk, inodes, PIDs) and chooses victims by **QoS class** - `BestEffort` first, then `Burstable` exceeding its requests, `Guaranteed` last. **The scheduler** preempts lower-`PriorityClass` Pods to make room for higher ones. **The API server** performs graceful eviction for `drain`, honouring PodDisruptionBudgets. The durable fixes are: set realistic requests and limits so QoS is not accidental, reserve capacity for the system (`--system-reserved`, `--kube-reserved`), give critical workloads a `PriorityClass` and everything else a lower one, protect availability with PDBs, and let the cluster autoscaler add nodes before pressure rather than after.

## Detail

### Who evicts, and why

| Mechanism                  | Trigger                                                                      | Victim selection                                              | Respects PDB |
| -------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------- | ------------ |
| **Kubelet node-pressure**  | `memory.available`, `nodefs.available`, `imagefs.available`, `pid.available` | QoS class, then usage above requests, then Pod priority       | No           |
| **Scheduler preemption**   | A pending higher-priority Pod cannot be scheduled                            | Lowest `PriorityClass` first                                  | Best effort  |
| **API eviction (`drain`)** | Node maintenance, upgrade, scale-down                                        | Whatever you drained                                          | Yes          |
| **OOM killer (in-kernel)** | Container exceeds its memory limit                                           | The offending process; container restarts, Pod is not evicted | n/a          |
| **Taint-based eviction**   | `NotReady`, `unreachable`, custom `NoExecute` taint                          | Pods without a matching toleration                            | No           |

The distinction that trips people: **exceeding a memory limit is an OOM kill** (exit code 137, container restarts in place, `Pod` stays), whereas **node memory pressure is an eviction** (Pod status `Failed`, reason `Evicted`, and it is rescheduled elsewhere). Read `kubectl describe pod` - the reason and message say which.

### QoS is derived, not declared

- **`Guaranteed`** - every container has `requests == limits` for both CPU and memory. Evicted last.
- **`Burstable`** - requests set, lower than limits (or only one of them set). Evicted after `BestEffort`, worst-offender-above-requests first.
- **`BestEffort`** - no requests or limits. First to die, and the reason most "random" evictions hit exactly the workloads nobody configured.

So the primary control for eviction risk is honest requests. Set memory requests near the real working set and **set memory `limits` equal to requests for anything critical** (memory is incompressible - there is no throttling, only killing). For CPU, requests matter for scheduling and limits cause throttling; many teams deliberately omit CPU limits on latency-sensitive services to avoid throttling while keeping requests accurate.

### Preventing pressure rather than reacting to it

1. **Reserve capacity for the system.** `--kube-reserved` and `--system-reserved` plus `--eviction-hard` keep the kubelet, container runtime, and OS from competing with Pods. Without them, a node runs out of memory before Kubernetes notices. Managed node groups set defaults; verify them rather than assuming.
2. **Right-size requests with data.** Use the Vertical Pod Autoscaler in recommendation mode, or historical p95 usage from Prometheus, to remove both over-request (wasted money, fewer Pods per node) and under-request (eviction risk).
3. **Autoscale before it hurts.** The Cluster Autoscaler or Karpenter adds nodes when Pods are unschedulable - which is _after_ the fact. Give it headroom with a low-priority "balloon" Deployment that gets preempted to create instant space, and make sure the autoscaler's limits, quotas, and instance types can actually satisfy the pending Pods. See [how do you autoscale workloads and nodes in Kubernetes](./how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
4. **Control disk pressure explicitly.** `imagefs` fills with unused images and `nodefs` with logs and `emptyDir`. Cap `emptyDir` with `sizeLimit`, rotate container logs (`containerLogMaxSize`), let the kubelet garbage-collect images, and watch for a Pod writing unbounded data to a local volume - the usual cause of a whole node going `DiskPressure` and evicting everything on it.
5. **Prioritise deliberately.** A small number of `PriorityClass` values - system-critical, production, batch - so the scheduler preempts the batch job rather than the payment service. Without priorities, preemption picks arbitrarily among equals.
6. **Protect availability during voluntary disruption.** A `PodDisruptionBudget` (`minAvailable: 2` or `maxUnavailable: 1`) makes `kubectl drain` and node-group upgrades wait rather than taking your last replica. Note the asymmetry that interviewers probe: PDBs constrain **voluntary** disruption only - the kubelet under memory pressure ignores them entirely.
7. **Spread the blast radius.** `topologySpreadConstraints` across zones and nodes, and anti-affinity for replicas of the same service, so one node's pressure does not remove a whole service. See [how do you control which node a Pod runs on](./how-do-you-control-which-node-a-pod-runs-on.md).

### Responding to an eviction storm

Confirm the node condition (`MemoryPressure`, `DiskPressure`), find what consumed the resource (`kubectl top nodes/pods`, then on the node: image cache, logs, a runaway container), cordon the node so nothing new lands, drain it if it is unhealthy, and raise the requests or limits on whatever was under-provisioned. Then fix the systemic cause - almost always missing requests, missing reservations, or an autoscaler that cannot add capacity fast enough. Evictions are a symptom of a capacity-planning gap, and treating them one Pod at a time is how a cluster stays permanently unstable. See [how do you do capacity planning](../site-reliability-engineering/how-do-you-do-capacity-planning.md).

## Example

```bash
# Which nodes are under pressure, and why?
kubectl get nodes -o custom-columns=\
'NAME:.metadata.name,MEM:.status.conditions[?(@.type=="MemoryPressure")].status,DISK:.status.conditions[?(@.type=="DiskPressure")].status'
kubectl describe node ip-10-0-3-14 | sed -n '/Conditions/,/Allocated resources/p'

# Evicted, or OOM-killed? The reason distinguishes the mechanism.
kubectl get pods -A --field-selector=status.phase=Failed
kubectl describe pod checkout-7d9f -n prod | grep -E 'Reason|Message|Last State|Exit Code'
#   Status: Failed   Reason: Evicted
#   Message: The node was low on resource: memory. Container api was using 2.1Gi,
#            which exceeds its request of 512Mi.       <- Burstable, over request

# What is actually consuming the node?
kubectl top nodes && kubectl top pods -A --sort-by=memory | head
kubectl describe node ip-10-0-3-14 | grep -A12 'Allocated resources'

# Stabilise: stop new work landing, then move it off safely (PDBs honoured)
kubectl cordon ip-10-0-3-14
kubectl drain ip-10-0-3-14 --ignore-daemonsets --delete-emptydir-data
```

```yaml
# Guaranteed QoS for the critical path, a PDB to survive drains, spread across zones
apiVersion: apps/v1
kind: Deployment
metadata: { name: checkout, namespace: prod }
spec:
  replicas: 6
  template:
    spec:
      priorityClassName: production # batch workloads sit below this
      containers:
        - name: api
          resources:
            requests: { cpu: "500m", memory: 1Gi }
            limits: { memory: 1Gi } # == request -> Guaranteed, evicted last
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app: checkout } }
      volumes:
        - name: scratch
          emptyDir: { sizeLimit: 1Gi } # bound it, or one Pod causes DiskPressure
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: checkout, namespace: prod }
spec:
  minAvailable: 4 # drains and upgrades wait; kubelet pressure does NOT
  selector: { matchLabels: { app: checkout } }
```

## Interview tips

- Separate the mechanisms in your first sentence - kubelet pressure, scheduler preemption, API eviction, OOM kill. Most candidates blur them, and the fixes are different.
- Get the OOM-versus-eviction distinction exactly right: exceeding a memory limit kills the container in place (exit 137), node pressure evicts the Pod. Interviewers use this to separate readers from operators.
- Explain that QoS class is **derived** from requests and limits, and name the eviction order. Then say the practical consequence: unconfigured `BestEffort` Pods are always the first casualties.
- Say why memory limits should equal requests for critical workloads (memory cannot be throttled) while CPU limits are often deliberately omitted (throttling hurts latency).
- Mention `--kube-reserved`/`--system-reserved` and eviction thresholds. Very few candidates do, and it is the difference between a node that degrades gracefully and one that falls over.
- The PDB nuance is a favourite follow-up: PDBs protect against voluntary disruption only, so they do not save you from node pressure.
- Bring up disk pressure with a concrete cause - an unbounded `emptyDir` or unrotated logs taking a whole node down - and the `sizeLimit` fix.
- Close on the systemic view: repeated evictions mean requests are wrong or capacity is short, so the real fix is right-sizing plus autoscaling headroom, not restarting Pods.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [[How do you run an application across multiple Kubernetes clusters?]] (`#414`): [How do you run an application across multiple Kubernetes clusters?](../container-orchestration-advanced/how-do-you-run-an-application-across-multiple-kubernetes-clusters.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
