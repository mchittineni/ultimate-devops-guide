---
title: "How does Kubernetes Leader Election work for HA control planes and custom controllers?"
id: 525
category: "Kubernetes"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - kubernetes
  - ha
  - controller
  - leader-election
quiz:
  stem: "Which Kubernetes API primitive is standardly used by controllers and control plane components to coordinate active-passive leader election?"
  options:
    - "PersistentVolumeClaims with ReadWriteOnce access mode"
    - "Lease objects in the coordination.k8s.io API group using atomic compare-and-swap renewals"
    - "Direct UDP broadcast packets between worker nodes"
    - "A shared Redis cluster hosted outside Kubernetes"
  answer: 2
  explanation: "Modern Kubernetes uses `Lease` objects in `coordination.k8s.io`. Standby replicas watch the lease and acquire leadership when the current holder fails to renew its timestamp."
---

# How does Kubernetes Leader Election work for HA control planes and custom controllers?

**Short answer:** Kubernetes leader election is a lock held in a `Lease` object (`coordination.k8s.io/v1`). Every replica of a controller tries to write its own identity into the Lease's `holderIdentity`; the API server's optimistic concurrency (`resourceVersion`) guarantees only one write wins. The winner keeps renewing `renewTime` on a short interval, while standbys watch; if the leader stops renewing for longer than `leaseDurationSeconds`, a standby takes the lease over and starts reconciling. `kube-controller-manager`, `kube-scheduler`, and most operators (via client-go or controller-runtime) all use this. It is active-passive by design, and it trades a few seconds of failover time for never having two writers - though that guarantee is only as good as the leader's discipline in stopping work when it loses the lease.

## Detail

**Why active-passive at all.** Controllers such as `kube-controller-manager`, `kube-scheduler`, and most operators are written assuming a single writer. Two active replicas would both create Pods for the same ReplicaSet or both bind the same Pod, fighting each other. Running several replicas with only one leader gives availability without that conflict.

**The protocol (client-go `leaderelection` package).**

1. **Acquire.** A candidate reads the Lease. If it is empty or expired, it updates it with its own `holderIdentity`, `acquireTime`, and `renewTime`, sending the `resourceVersion` it read. If another candidate got there first, the API server rejects the update with `409 Conflict` - this compare-and-swap is what makes the election safe without any separate consensus system (etcd provides the consensus underneath).
2. **Renew.** The leader updates `renewTime` every `retryPeriod` (client-go default 2 s). If it cannot renew within `renewDeadline` (default 10 s), it must stop leading - client-go calls `OnStoppedLeading`, and the usual implementation is to exit the process.
3. **Take over.** Standbys poll every `retryPeriod`. A standby treats the lease as expired when it has not **observed** the record change for `leaseDurationSeconds` (default 15 s), measured on its own clock - so clock skew between nodes does not matter, only the rate at which time passes. It then attempts the same compare-and-swap to claim the lease.

Worst-case failover after a leader crash is roughly `leaseDuration` plus a `retryPeriod`; after a graceful shutdown with `ReleaseOnCancel`, the leader clears the lease and a standby takes over almost immediately.

**Where you see it.**

- **Control plane.** `kube-controller-manager` and `kube-scheduler` run with `--leader-elect=true` (the default) and hold Leases in `kube-system`. On a three-node control plane, exactly one of each is active. `kubectl get lease -n kube-system` shows who.
- **Nodes.** A separate use of the same object: each kubelet renews a Lease in `kube-node-lease` as its cheap heartbeat.
- **Custom controllers.** controller-runtime enables it with `LeaderElection: true` and a `LeaderElectionID`; webhooks and metrics endpoints keep serving on every replica, only the reconcilers wait for leadership.
- **Coordinated leader election** (`LeaseCandidate` objects, beta and off by default at the time of writing) lets the API server pick the leader among candidates - for example, preferring the oldest compatible version during a control-plane upgrade - rather than whoever wins the race.

**Trade-offs and limitations.**

- **Not a perfect fence.** A leader that is paused (long GC, CPU starvation, a frozen VM) can believe it still leads after its lease has expired and a new leader has started. client-go minimises this with `renewDeadline < leaseDuration`, but actions that must never overlap need their own fencing (for example, checking an owner token or relying on `resourceVersion` preconditions on every write).
- **Failover is not instant.** Shorter durations fail over faster but generate more API writes and more false failovers when the API server is slow; the defaults are a compromise.
- **Throughput does not scale.** Only one replica does work. Controllers that need horizontal scale shard the keyspace instead (for example, by namespace or hash), each shard with its own lease.

## Example

```yaml
# The lock itself - what `kubectl get lease my-operator-leader -o yaml` shows
apiVersion: coordination.k8s.io/v1
kind: Lease
metadata:
  name: my-operator-leader
  namespace: operators
spec:
  holderIdentity: my-operator-7d8b5c-x2k9p_3f1c2a9e
  leaseDurationSeconds: 15
  acquireTime: "2026-09-23T19:58:02.000000Z"
  renewTime: "2026-09-23T20:00:10.000000Z"
  leaseTransitions: 4
```

```go
// controller-runtime: leader election for a custom operator
mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
    LeaderElection:                true,
    LeaderElectionID:              "my-operator-leader",
    LeaderElectionNamespace:       "operators",
    LeaderElectionReleaseOnCancel: true, // fast hand-over on graceful shutdown
})
```

```bash
kubectl get lease -n kube-system                     # kube-controller-manager, kube-scheduler holders
kubectl get lease my-operator-leader -n operators -o jsonpath='{.spec.holderIdentity}{"\n"}'
```

## Interview tips

- Name the primitive (`Lease` in `coordination.k8s.io`) and the mechanism that makes it safe: optimistic concurrency on `resourceVersion`, backed by etcd.
- Give the three timings - `leaseDuration` 15 s, `renewDeadline` 10 s, `retryPeriod` 2 s - and what each controls.
- Point out that expiry is judged on the observer's own clock since it last saw a change, which is why clock skew does not break it.
- Volunteer the limitation: a paused leader can act after losing the lease, so critical side effects need fencing. That is the senior-level answer.
- Mention that leader election gives availability, not throughput - scaling a controller means sharding.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [[How do you back up and restore a Kubernetes cluster?]] (`#451`): [How do you back up and restore a Kubernetes cluster?](../container-orchestration-advanced/how-do-you-back-up-and-restore-a-kubernetes-cluster.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
