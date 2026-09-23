---
title: "How do Pod Disruption Budgets (PDB) protect application availability during cluster maintenance?"
id: 530
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - kubernetes
  - pdb
  - availability
  - maintenance
quiz:
  stem: "What action does Kubernetes take when `kubectl drain` attempts to evict a Pod that would violate a PodDisruptionBudget?"
  options:
    - "The Kubelet immediately forces a hard reboot of the worker node"
    - "The Eviction API rejects the eviction request, causing the drain to block and retry until replacement pods become Ready"
    - "The PDB is automatically deleted and the pod is terminated"
    - "The cluster autoscaler shuts down all application pods across the cluster"
  answer: 2
  explanation: "Voluntary disruptions rely on the Eviction API. If an eviction violates a PDB, the API returns HTTP 429, forcing the drain process to wait until healthy replicas exist elsewhere."
---

# How do Pod Disruption Budgets (PDB) protect application availability during cluster maintenance?

**Short answer:** A PodDisruptionBudget sets the minimum number of Pods that must stay available (`minAvailable`) or the maximum that may be down (`maxUnavailable`) for a label selector during **voluntary** disruptions - node drains, cluster upgrades, and autoscaler scale-downs. It works because those tools evict Pods through the Eviction API, which refuses any eviction that would breach the budget. It does nothing against involuntary failures, and a budget that allows zero disruptions blocks maintenance entirely.

## Detail

Kubernetes distinguishes two kinds of disruption:

- **Involuntary disruptions**: hardware faults, kernel panics, a VM deleted by the cloud provider, node-pressure eviction. A PDB cannot prevent these, although they do count against the budget.
- **Voluntary disruptions**: `kubectl drain`, managed node-pool upgrades, Cluster Autoscaler or Karpenter consolidation. These go through the Eviction API and so respect PDBs.

**How the Eviction API enforces the budget.** `kubectl drain node-1` cordons the node and then calls the `pods/eviction` subresource for each Pod rather than deleting it. The API server checks every PDB that selects the Pod: if evicting it would take healthy Pods below `minAvailable` (or push unavailable Pods above `maxUnavailable`), the request is **rejected with HTTP 429 Too Many Requests** and the Pod keeps running. Drain retries every few seconds. Meanwhile, each Pod that _was_ evicted is recreated by its controller on another node; once the replacement is Ready, the budget has room again and the next eviction succeeds. The PDB therefore paces the drain, one safe step at a time.

**`minAvailable` or `maxUnavailable`.** Both accept an integer or a percentage. `maxUnavailable` is usually the better choice for Deployments because it scales with the replica count; `minAvailable` suits quorum systems (for example, 2 of 3 etcd or ZooKeeper members). Only one may be set per PDB.

**Unhealthy Pods.** By default a Pod that is running but not Ready still needs budget to be evicted, so a Deployment with a crash-looping replica can deadlock a drain. Setting `unhealthyPodEvictionPolicy: AlwaysAllow` (stable since Kubernetes 1.31) lets not-Ready Pods be evicted regardless of the budget.

**Trade-offs and limitations.**

- `minAvailable: 100%`, `maxUnavailable: 0`, or `minAvailable` equal to the replica count means **no** eviction is ever allowed. Node upgrades then stall: depending on the platform, a managed upgrade either fails (EKS managed node groups, unless forced) or ignores the budget after a timeout (GKE), so the budget ends up protecting nothing.
- A PDB on a single-replica workload is the same problem in miniature: either accept the downtime or run at least two replicas.
- Deleting a Pod directly (`kubectl delete pod`) or deleting a Deployment bypasses the Eviction API and ignores PDBs. So does `kubectl drain --disable-eviction`.

## Example

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-pdb
spec:
  maxUnavailable: 1 # at most one payment Pod down at a time for voluntary disruptions
  unhealthyPodEvictionPolicy: AlwaysAllow # do not let a crash-looping Pod block drains
  selector:
    matchLabels:
      app: payment
```

```bash
kubectl get pdb payment-pdb               # ALLOWED DISRUPTIONS column: 0 means drains will block
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data --timeout=10m
# "Cannot evict pod as it would violate the pod's disruption budget." - drain keeps retrying
```

## Interview tips

- Separate voluntary disruptions (drains, upgrades, consolidation) from involuntary ones (hardware failure). A PDB only governs the first kind.
- Name the mechanism: the Eviction API returns 429 when an eviction would breach the budget, and drain retries until a replacement is Ready.
- Prefer `maxUnavailable` for Deployments, `minAvailable` for quorum-based systems, and know that only one can be set.
- Volunteer the failure mode: a budget that allows zero disruptions blocks every node upgrade. Interviewers often ask "what if `ALLOWED DISRUPTIONS` is 0?".
- Mention `unhealthyPodEvictionPolicy: AlwaysAllow` for the crash-looping-replica deadlock.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
