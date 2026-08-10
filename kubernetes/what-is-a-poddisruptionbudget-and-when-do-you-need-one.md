---
title: "What is a PodDisruptionBudget and when do you need one?"
id: 446
category: "Kubernetes"
difficulty: "Advanced"
tags:
  - devops
  - kubernetes
  - interview-questions
  - scalability-and-high-availability
---

# What is a PodDisruptionBudget and when do you need one?

**Short answer:** A PodDisruptionBudget is a contract that limits how many Pods of a workload may be taken down **by voluntary disruptions** at the same time. You declare either `minAvailable` or `maxUnavailable` against a label selector, and the **eviction API** honours it: `kubectl drain`, cluster autoscaler scale-down, node-pool upgrades, and descheduler-style tooling all evict through that API and will block rather than breach the budget. The crucial qualifier is **voluntary**: a PDB does nothing about a node dying, a kernel panic, an OOM kill, or someone running `kubectl delete pod`. You need one for anything where losing several replicas at once is an outage or a data-loss risk - quorum systems (etcd, ZooKeeper, Kafka, Consul), databases, ingress controllers, and any service with a small replica count that gets drained during cluster maintenance.

## Detail

### Voluntary versus involuntary - the distinction that defines the object

| Voluntary (PDB applies)                       | Involuntary (PDB does nothing)                                               |
| --------------------------------------------- | ---------------------------------------------------------------------------- |
| `kubectl drain` / node cordon + drain         | Node hardware or kernel failure                                              |
| Cluster autoscaler removing an underused node | Spot/preemptible instance reclaim (short notice; some providers drain first) |
| Managed node-group or node-pool upgrade       | Kubelet or container runtime crash                                           |
| Rolling a node image / OS patching            | OOM kill, eviction under node pressure                                       |
| Descheduler rebalancing                       | `kubectl delete pod` (bypasses the eviction API)                             |

Saying that sentence - "a PDB constrains the eviction API, so it protects you from maintenance, not from failures" - is most of the answer.

### `minAvailable` versus `maxUnavailable`

- `minAvailable: 2` - at least two Pods matching the selector must remain **Ready** at all times. Absolute numbers are the safe choice for quorum systems, because you can reason about them directly.
- `maxUnavailable: 1` - at most one may be down. Equivalent phrasing, expressed from the other side.
- Percentages are allowed (`minAvailable: 75%`) and are rounded **up** for `minAvailable`; they scale with the workload, which is convenient for large Deployments but easy to get wrong for small ones.
- You may only set one of the two per PDB.

### The deadlock that catches everyone

If `minAvailable` equals the replica count - `replicas: 1` with `minAvailable: 1`, or `replicas: 3` with `minAvailable: 3` - **no Pod can ever be evicted**, and `kubectl drain` hangs forever. Node upgrades stall, the cluster autoscaler gives up on scaling down, and the platform team ends up deleting Pods by hand (which bypasses the budget and defeats the purpose). Rules of thumb:

- A single-replica workload cannot be protected by a PDB. Either accept the disruption or scale to 2+ - and if it genuinely cannot run two copies, that is a design problem the PDB cannot solve.
- For a three-node quorum, `minAvailable: 2` is correct: one may leave, quorum survives.
- Watch `status.disruptionsAllowed` (`kubectl get pdb`); if it sits at 0, maintenance is blocked and you should know before you start a cluster upgrade, not during it.

Also note that unhealthy Pods count against you: if a replica is already `CrashLoopBackOff`, the budget may allow zero further disruptions. `unhealthyPodEvictionPolicy: AlwaysAllow` (1.27+) lets already-unready Pods be evicted so a drain can make progress instead of deadlocking on broken Pods.

### PDBs are not a substitute for spreading

A PDB slows disruption down; it does not stop all your replicas being on one node in the first place. If three replicas share a node and that node dies, the PDB was irrelevant. Pair it with:

- `topologySpreadConstraints` across `kubernetes.io/hostname` and `topology.kubernetes.io/zone` (`whenUnsatisfiable: ScheduleAnyway` for soft, `DoNotSchedule` for hard).
- Pod anti-affinity for the strict cases.
- `terminationGracePeriodSeconds` plus a `preStop` hook, so the eviction the PDB permitted is itself graceful and connections drain.

Together these three - spread, PDB, graceful shutdown - are what "safe during a node upgrade" actually means.

### Where it shows up operationally

`kubectl drain` reports `Cannot evict pod as it would violate the pod's disruption budget` and retries. That message is a feature: it is the cluster telling you the maintenance would breach availability. The right responses are to wait, scale the workload up temporarily, or fix an unhealthy replica - not `--force` or `--disable-eviction`, which delete Pods directly and skip the budget entirely.

## Example

```yaml
# Quorum system: three replicas, exactly one may be disrupted at a time
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: kafka-pdb, namespace: data }
spec:
  minAvailable: 2 # NOT 3 - that would block every drain forever
  unhealthyPodEvictionPolicy: AlwaysAllow # let a broken replica be evicted
  selector:
    matchLabels: { app: kafka }
---
# Stateless service: percentage-based, scales with the Deployment
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api-pdb, namespace: prod }
spec:
  maxUnavailable: 25%
  selector:
    matchLabels: { app: api }
```

```yaml
# The PDB only works if the replicas were spread in the first place
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, namespace: prod }
spec:
  replicas: 6
  template:
    metadata: { labels: { app: api } }
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector: { matchLabels: { app: api } }
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app: api } }
      terminationGracePeriodSeconds: 45
      containers:
        - name: api
          image: registry.example.com/api:1.9.0
          lifecycle:
            preStop: { exec: { command: ["sh", "-c", "sleep 10"] } } # let the LB deregister
```

```bash
# Before any cluster or node-pool upgrade: is maintenance even possible?
kubectl get pdb -A
# NAME        MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
# kafka-pdb   2               N/A               1                     40d
# api-pdb     N/A             25%               0                     12d   <- blocked

kubectl get pdb api-pdb -n prod -o jsonpath='{.status.disruptionsAllowed}{"\n"}'
kubectl describe pdb api-pdb -n prod        # which Pods are counted unhealthy

# Drain honours it; --force does not (and is why people think PDBs "do not work")
kubectl drain ip-10-0-3-14 --ignore-daemonsets --delete-emptydir-data
```

## Interview tips

- Define it by mechanism: it constrains the **eviction API**, so it governs voluntary disruptions - drains, autoscaler scale-down, node upgrades - and has no effect on node failure, OOM kills, or `kubectl delete pod`. Leading with that distinction is the strongest possible opening.
- Bring up the deadlock unprompted: `replicas: 1` with `minAvailable: 1`, or `minAvailable` equal to the replica count, makes drains hang forever. Interviewers who run clusters have all been bitten by this.
- Give the quorum example - three replicas, `minAvailable: 2` - because it shows you are thinking about what the workload needs rather than copying a template.
- Say that a PDB is one leg of a tripod with `topologySpreadConstraints` and graceful shutdown, and that a budget over three replicas on one node buys nothing.
- Mention `status.disruptionsAllowed` as the pre-upgrade check, and `unhealthyPodEvictionPolicy: AlwaysAllow` as the fix for drains blocked by already-broken Pods. Both are recent and specific.
- If they ask what to do when a drain is blocked: wait, temporarily scale up, or repair the unhealthy replica - never `--force`, which bypasses the budget you deliberately set. See [upgrading a production Kubernetes cluster with zero downtime](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md), [node pressure and Pod evictions](./how-do-you-handle-node-pressure-and-pod-evictions-in-kubernetes.md), and [rolling updates and rollback](./how-do-you-perform-and-roll-back-a-rolling-update-in-kubernetes.md).

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
