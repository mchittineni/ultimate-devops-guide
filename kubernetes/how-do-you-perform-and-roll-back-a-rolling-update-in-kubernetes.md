---
title: "How do you perform and roll back a rolling update in Kubernetes?"
id: 410
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - devops-tools-and-automation
  - incident-management
---

# How do you perform and roll back a rolling update in Kubernetes?

**Short answer:** A Deployment rolls out by creating a new ReplicaSet and shifting replicas across within the bounds of `maxSurge` and `maxUnavailable`, gated by the **readiness probe** - which is what makes the update safe or useless. Watch it with `kubectl rollout status`, and if it goes wrong, `kubectl rollout undo deployment/<name>` restores the previous ReplicaSet immediately. The two things candidates miss: set `minReadySeconds` and `progressDeadlineSeconds` so a broken release stalls instead of quietly replacing every Pod, and remember that **a rollback only reverts the Pod template** - it cannot undo a database migration, a consumed message, or a mutated data format.

## Detail

### What actually happens

`kubectl apply` changes the Deployment's Pod template, which changes its hash, which creates a new ReplicaSet. The Deployment controller then scales the new one up and the old one down, obeying:

- **`maxUnavailable`** - how many replicas may be missing during the update. `0` guarantees full capacity but requires room for extra Pods.
- **`maxSurge`** - how many extra Pods above the desired count may exist. `0` means no extra capacity is used but the update must remove before it adds.
- **`minReadySeconds`** - how long a Pod must be `Ready` before it counts as available. Without this, a Pod that becomes ready and crashes two seconds later still lets the rollout continue, and you can replace an entire healthy fleet with a broken one.
- **`progressDeadlineSeconds`** - after this long without progress the rollout is marked `Failed` (condition `ProgressDeadlineExceeded`). Crucially, **it does not roll back automatically** - it stops and waits for you, which is why a stalled rollout can sit half-migrated for hours.

The readiness probe is the actual gate: if it does not genuinely test readiness (dependencies reachable, cache warm, migrations applied), a rolling update is just a slower way to break production. See [how do liveness, readiness, and startup probes differ](./how-do-liveness-readiness-and-startup-probes-differ.md).

### Doing it safely

```bash
kubectl apply -f deployment.yaml
kubectl rollout status deployment/checkout --timeout=5m   # non-zero exit on failure
```

Wire that exit code into the pipeline so a failed rollout fails the deploy job rather than being reported as success. Keep `revisionHistoryLimit` at something useful (10 is the default; `0` deletes your ability to roll back). Use `kubectl rollout pause` to hold a partially-updated state deliberately - a poor-man's canary - and `resume` to continue. Handle graceful shutdown properly: `terminationGracePeriodSeconds` long enough for in-flight requests, `SIGTERM` handled by the application, and a `preStop` sleep of a few seconds so load balancers and kube-proxy stop sending traffic before the process exits. Without that, every rolling update drops a small number of requests, which shows up as a latency and error blip nobody can explain.

### Rolling back

```bash
kubectl rollout history deployment/checkout           # revisions and change-cause
kubectl rollout undo deployment/checkout              # back one revision
kubectl rollout undo deployment/checkout --to-revision=7
```

`undo` re-applies the previous ReplicaSet's Pod template, so it is fast (the old image is usually still cached on the nodes) and it is the correct first move during an incident - mitigate, then diagnose. Two important caveats:

- **In GitOps, `undo` is not the fix.** ArgoCD or Flux will reconcile your manual rollback straight back to the broken version. The rollback is `git revert` on the manifest repository - which is also what leaves an audit trail. See [what is GitOps](../devops-tools-and-automation/what-is-gitops.md).
- **Rollback reverts code, not consequences.** If the release ran a destructive migration, wrote a new field format, published events consumers already processed, or changed a cache key, the old code may not tolerate the new data. That is why migrations are expand/contract and backward compatible for a release. See [how do you change a production database schema without downtime](../database-management-in-devops/how-do-you-change-a-production-database-schema-without-downtime.md).

### When the rollout is stuck

Diagnose in this order: `kubectl rollout status` (what is it waiting for?), `kubectl get rs` (which ReplicaSet has how many ready?), `kubectl describe pod` on a new Pod (image pull, config, probe failures, scheduling). The recurring causes are an image tag that does not exist or a registry credential problem, a failing readiness probe, insufficient cluster capacity for `maxSurge` Pods, a `PodDisruptionBudget` blocking the removal of old Pods, and a missing ConfigMap or Secret. Note the asymmetry with `maxUnavailable: 0`: if the cluster cannot fit the surge Pods, the rollout does not fail loudly - it simply never progresses.

### StatefulSets and DaemonSets differ

A StatefulSet updates **in reverse ordinal order, one Pod at a time**, and if a Pod never becomes ready the rollout stops there - so a broken StatefulSet update needs the template fixed and often a manual delete of the wedged Pod; `partition` in its `updateStrategy` is the built-in canary mechanism. DaemonSets roll per node with their own `maxUnavailable`. Neither behaves like a Deployment, and interviewers ask precisely because people assume they do.

### Beyond rolling updates

A rolling update has no traffic control and no automated verdict - it swaps Pods and hopes the probes catch problems. When you need percentage-based traffic shifting, metric-driven promotion, or instant rollback, that is blue/green or canary with Argo Rollouts or Flagger. See [what are deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md), [what is blue/green deployment](../advanced-devops-cloud/what-is-blue-green-deployment.md), and [what is canary analysis](../advanced-devops-cloud/what-is-canary-analysis.md).

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
  annotations:
    kubernetes.io/change-cause: "release 1.9.0 - payment retry fix" # shows in history
spec:
  replicas: 10
  revisionHistoryLimit: 10 # keep revisions, or you cannot roll back
  progressDeadlineSeconds: 600 # marks the rollout Failed - does NOT auto-revert
  minReadySeconds: 30 # a Pod must stay healthy before it counts
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0 # never lose capacity...
      maxSurge: 2 # ...at the cost of 2 extra Pods' headroom
  template:
    spec:
      terminationGracePeriodSeconds: 45
      containers:
        - name: api
          image: registry.example.com/checkout@sha256:9f2c8b1d... # digest, not :latest
          readinessProbe: # the actual gate on the rollout
            httpGet: { path: /readyz, port: 8080 }
            periodSeconds: 5
          lifecycle:
            preStop:
              exec: { command: ["sh", "-c", "sleep 5"] } # let endpoints drain first
```

```bash
# Deploy, and let the pipeline fail if the rollout does
kubectl apply -f deployment.yaml
kubectl rollout status deployment/checkout --timeout=5m || {
  kubectl rollout undo deployment/checkout        # mitigate first, diagnose after
  kubectl rollout status deployment/checkout --timeout=5m
  exit 1
}

# Stuck? Find out what it is waiting for, in three commands.
kubectl rollout status deployment/checkout
# Waiting for deployment "checkout" rollout to finish: 3 of 10 updated replicas are available
kubectl get rs -l app=checkout          # old vs new ReplicaSet, desired/current/ready
kubectl describe pod -l app=checkout --field-selector=status.phase=Pending | grep -A6 Events

kubectl rollout history deployment/checkout
kubectl rollout undo deployment/checkout --to-revision=7
```

## Interview tips

- Describe the ReplicaSet mechanism, not just the command: a template change creates a new ReplicaSet and the controller shifts replicas within `maxSurge`/`maxUnavailable`.
- Say that the readiness probe is what makes a rolling update safe, and that a probe returning 200 unconditionally makes the whole strategy decorative.
- `minReadySeconds` and `progressDeadlineSeconds` are the two fields that separate a considered answer from a recited one - and note explicitly that the progress deadline does **not** roll back automatically.
- Give `kubectl rollout undo` as the incident-time first move, then immediately add the caveat about migrations and data formats. That combination of decisiveness and caution is what is being assessed.
- Mention the GitOps correction: manual `undo` gets reconciled away, so the real rollback is `git revert`.
- Volunteer the `preStop` sleep plus `SIGTERM` handling for zero-dropped-requests. It explains the small error blip most teams have learned to ignore.
- Know that StatefulSets update in reverse ordinal order one at a time and stall on an unready Pod, and that `partition` is their canary control.
- Close by naming the limits of rolling updates - no traffic shifting, no automated verdict - and when you would reach for canary or blue/green instead.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [[How do you back up and restore a Kubernetes cluster?]] (`#451`): [How do you back up and restore a Kubernetes cluster?](../container-orchestration-advanced/how-do-you-back-up-and-restore-a-kubernetes-cluster.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
