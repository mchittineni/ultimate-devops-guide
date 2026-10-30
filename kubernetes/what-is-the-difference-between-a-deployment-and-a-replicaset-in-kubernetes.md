---
title: "What is the difference between a Deployment and a ReplicaSet in Kubernetes?"
id: 752
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - kubernetes
  - interview-questions
quiz:
  stem: "You change the container image in a Deployment's Pod template. What does the Deployment controller do?"
  options:
    - "It edits the existing ReplicaSet's template, which restarts all Pods at once"
    - "It creates a new ReplicaSet for the new template and scales it up while scaling the old one down"
    - "It deletes the Deployment and recreates it"
    - "It patches the running containers in place without creating Pods"
  answer: 2
  explanation: "Each distinct Pod template gets its own ReplicaSet (named with the pod-template-hash). A rollout shifts replicas from the old ReplicaSet to the new one within maxSurge and maxUnavailable, and keeps old ReplicaSets for rollback."
---

# What is the difference between a Deployment and a ReplicaSet in Kubernetes?

**Short answer:** A **ReplicaSet** has one job: keep N Pods matching a label selector running, creating or deleting Pods from its template to close the gap. A **Deployment** manages ReplicaSets on top of that: every change to the Pod template creates a **new ReplicaSet**, and the Deployment shifts replicas from the old one to the new one at a controlled pace, keeping old ReplicaSets around so it can roll back. So you create Deployments and let them own ReplicaSets; you almost never create a ReplicaSet directly, because a bare ReplicaSet ignores template changes for existing Pods and has no rollout or rollback.

## Detail

### The ownership chain

```text
Deployment  checkout                 (desired replicas, strategy, revision history)
  ├── ReplicaSet  checkout-7d9f8c    (template v2, replicas: 3)  -> Pods checkout-7d9f8c-xxxxx
  └── ReplicaSet  checkout-5b6c4a    (template v1, replicas: 0)  <- kept for rollback
```

Each ReplicaSet name carries a **`pod-template-hash`** label computed from its template; the Deployment adds that label to the ReplicaSet's selector and its Pods so two revisions never claim each other's Pods. Every object points to its parent through `ownerReferences`, so deleting the Deployment garbage-collects its ReplicaSets and Pods.

### What each controller does

| Concern                          | ReplicaSet                                             | Deployment                                                             |
| -------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------- |
| Keeps N Pods running             | Yes - its whole purpose                                | Delegates to its current ReplicaSet                                    |
| Reacts to a template change      | Only for **new** Pods; existing Pods keep the old spec | Creates a new ReplicaSet and rolls Pods over                           |
| Rollout strategy                 | None                                                   | `RollingUpdate` (`maxSurge`, `maxUnavailable`) or `Recreate`           |
| Rollback                         | None                                                   | `kubectl rollout undo`, bounded by `revisionHistoryLimit` (default 10) |
| Pause, resume, progress deadline | No                                                     | `rollout pause/resume`, `progressDeadlineSeconds`, `minReadySeconds`   |
| Scaling target for an HPA        | Possible                                               | The normal target                                                      |

Scaling alone (`kubectl scale deployment checkout --replicas=5`) does **not** create a new ReplicaSet - only a Pod-template change does. That is why changing replicas never appears in `kubectl rollout history`.

### Where the older objects fit

- **ReplicationController** is the pre-ReplicaSet API with equality-only selectors. It still exists but is legacy; ReplicaSets support set-based selectors (`In`, `NotIn`, `Exists`).
- **StatefulSets** and **DaemonSets** do not use ReplicaSets at all; they manage Pods directly (using `ControllerRevision` objects for their history) because they need stable identity or one Pod per node.

### Trade-offs and traps

- **Selector immutability.** A Deployment's `spec.selector` cannot be changed after creation; changing labels means a new Deployment.
- **Label overlap.** If a bare Pod or another controller's Pods match a ReplicaSet's selector, the ReplicaSet will count - and may delete - them. Unique labels per workload avoid it.
- **Editing the ReplicaSet by hand** is futile: the Deployment reconciles it straight back. Change the Deployment.
- **Old ReplicaSets cost nothing running** (they are scaled to zero) but each is an object in etcd; `revisionHistoryLimit: 0` saves that at the price of losing rollback.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: checkout }
spec:
  replicas: 3
  revisionHistoryLimit: 5 # old ReplicaSets kept for rollback
  selector: { matchLabels: { app: checkout } } # immutable after creation
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  template:
    metadata: { labels: { app: checkout } }
    spec:
      containers:
        - name: api
          image: registry.example.com/checkout:1.9.0
```

```bash
kubectl set image deployment/checkout api=registry.example.com/checkout:1.9.1
kubectl get rs -l app=checkout
# NAME                  DESIRED   CURRENT   READY
# checkout-7d9f8c4b6d   3         3         3      <- new template
# checkout-5b6c4a9f2e   0         0         0      <- previous, kept for rollback
kubectl rollout history deployment/checkout
kubectl rollout undo deployment/checkout           # scales the old ReplicaSet back up
kubectl get rs checkout-7d9f8c4b6d -o jsonpath='{.metadata.ownerReferences[0].kind}{"\n"}'   # Deployment
```

## Interview tips

- One line each: a ReplicaSet keeps N identical Pods alive; a Deployment manages ReplicaSets to roll out and roll back template changes.
- Explain that a template change creates a new ReplicaSet (named by `pod-template-hash`), while a scale change does not - that is the detail interviewers probe.
- Say why you do not use bare ReplicaSets: existing Pods keep the old template, and there is no rollout strategy or rollback.
- Mention that rollback works by scaling an old ReplicaSet back up, so `revisionHistoryLimit: 0` removes it.
- Note that StatefulSets and DaemonSets manage Pods directly, not through ReplicaSets. See [how do you perform and roll back a rolling update](./how-do-you-perform-and-roll-back-a-rolling-update-in-kubernetes.md) and [what are StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
