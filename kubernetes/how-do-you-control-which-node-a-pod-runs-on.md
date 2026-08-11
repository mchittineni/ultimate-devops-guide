---
title: "How do you control which node a Pod runs on?"
id: 256
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# How do you control which node a Pod runs on?

**Short answer:** `nodeSelector` and node affinity are Pod-side rules saying where a Pod _wants_ to go; taints and tolerations are node-side rules saying who a node will _accept_. Pod affinity and anti-affinity place Pods relative to other Pods, and topology spread constraints distribute replicas evenly across failure domains. You usually need a pair: a taint to keep everything else off special hardware, plus affinity to attract the right workloads onto it.

## Detail

**The distinction interviewers actually test.** `nodeSelector`/node affinity express _attraction_ - "schedule me on a node with an NVMe SSD". Taints express _repulsion_ - "nothing runs here unless it explicitly tolerates this". A toleration does **not** attract a Pod to a tainted node; it only removes the barrier. This is why GPU node pools carry both a taint (so ordinary web Pods do not land on expensive hardware) and a label (so GPU Pods can select it).

**Node affinity, in two strengths:**

- `requiredDuringSchedulingIgnoredDuringExecution` - a hard constraint. No matching node means the Pod stays `Pending`.
- `preferredDuringSchedulingIgnoredDuringExecution` - a weighted preference. The scheduler tries, then places the Pod anywhere if it cannot.

`IgnoredDuringExecution` in both names means the rule is evaluated at scheduling time only; relabelling a node later does not evict running Pods.

**Taint effects:**

| Effect             | Meaning                                                           |
| ------------------ | ----------------------------------------------------------------- |
| `NoSchedule`       | New Pods without a matching toleration are not scheduled here     |
| `PreferNoSchedule` | Soft version - the scheduler avoids the node if it can            |
| `NoExecute`        | As above, **and** running Pods without the toleration are evicted |

Kubernetes taints nodes automatically for conditions like `node.kubernetes.io/not-ready` and `unreachable`; `tolerationSeconds` on those is what controls how long a Pod survives on a node that has gone silent.

**Pod affinity and anti-affinity** place Pods relative to other Pods over a `topologyKey` - typically `kubernetes.io/hostname` (per node) or `topology.kubernetes.io/zone`. Anti-affinity is the classic HA rule: "no two replicas of this Deployment on the same node." Be aware it is computationally expensive on large clusters, and a _required_ anti-affinity with more replicas than nodes leaves Pods permanently `Pending`.

**Topology spread constraints are the modern answer** for even distribution. `maxSkew` bounds the imbalance between domains, and `whenUnsatisfiable: ScheduleAnyway` degrades gracefully instead of wedging - which is exactly the failure mode required anti-affinity has. Reach for `topologySpreadConstraints` first and keep anti-affinity for strict "never co-locate" rules.

**`nodeName` bypasses the scheduler entirely.** It is a debugging tool, not a placement strategy - no resource checks, no rescheduling if the node dies.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference
spec:
  replicas: 6
  template:
    spec:
      # 1. Node-side gate: this pool is tainted, so we must tolerate it.
      tolerations:
        - key: workload
          operator: Equal
          value: gpu
          effect: NoSchedule

      # 2. Pod-side attraction: only land on the GPU pool, prefer newer cards.
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: accelerator
                    operator: In
                    values: [nvidia-a100, nvidia-h100]
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              preference:
                matchExpressions:
                  - key: accelerator
                    operator: In
                    values: [nvidia-h100]

      # 3. Spread replicas across zones, but never block scheduling on it.
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels: { app: inference }

      containers:
        - name: server
          image: ghcr.io/acme/inference:2.1.0
```

```bash
kubectl taint nodes gpu-node-1 workload=gpu:NoSchedule    # add
kubectl taint nodes gpu-node-1 workload=gpu:NoSchedule-   # remove (trailing dash)
kubectl label nodes gpu-node-1 accelerator=nvidia-h100

# Why is this Pod Pending? The scheduler says so explicitly.
kubectl describe pod inference-xxx | grep -A10 Events
```

## Interview tips

- The one-liner to have ready: **taints repel, affinity attracts** - and a toleration is permission, not preference.
- Expect the direct comparison "nodeSelector / node affinity vs taints and tolerations". Answer with the direction of the rule, then say you normally use both together.
- Know that `NoExecute` evicts already-running Pods and the other two effects do not.
- Prefer `topologySpreadConstraints` over required pod anti-affinity for HA spread, and be ready to say why: anti-affinity leaves Pods `Pending` when replicas exceed domains.
- `kubectl describe pod` on a `Pending` Pod prints the scheduler's exact reason - say that when asked how you would debug placement.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
