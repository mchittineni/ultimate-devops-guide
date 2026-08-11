---
title: "How do you troubleshoot a Pod stuck in Pending or CrashLoopBackOff?"
id: 234
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# How do you troubleshoot a Pod stuck in Pending or CrashLoopBackOff?

**Short answer:** Troubleshoot a `Pending` pod by inspecting cluster scheduling (CPU/memory capacity, node selectors, taints/tolerations, PVC binding), and troubleshoot `CrashLoopBackOff` by checking application runtime logs (`kubectl logs --previous`), failing readiness/liveness probes, missing secrets, or exit codes like `137` (OOMKilled).

## Detail

`Pending` and `CrashLoopBackOff` are the two most common pod failure states seen in production interviews and incidents:

### 1. Troubleshooting `Pending` Pods

A pod is stuck in `Pending` when the Kubernetes scheduler cannot find a node that satisfies its requirements.

- **Resource Constraints:** Check if cluster nodes have available CPU or Memory matching the pod's `resources.requests`.
- **Taints and Tolerations:** Check if nodes are tainted (e.g. `node.kubernetes.io/unschedulable` or custom node taints) without matching tolerations in the Pod spec.
- **Node Selectors & Affinity:** Verify that node labels specified in `nodeSelector` or `nodeAffinity` match active nodes.
- **Unbound Persistent Volume Claim (PVC):** If using persistent storage, check if the PVC is in `Pending` state waiting for dynamic volume provisioning.
- **Namespace Quotas:** Check if a `ResourceQuota` on the namespace is preventing new pod creation.

### 2. Troubleshooting `CrashLoopBackOff` Pods

A pod in `CrashLoopBackOff` is continuously starting, failing, and restarting with exponential backoff delay.

- **Application Crash / Misconfiguration:** Inspect standard output and standard error logs. If the container restarted, run `kubectl logs <pod-name> -c <container-name> --previous` to see the exit logs from the killed instance.
- **OOMKilled (Exit Code 137):** Container process exceeded its `resources.limits.memory` and was terminated by the Linux OOM killer. Check `kubectl describe pod <pod-name>` under `Last State`.
- **Failing Liveness / Readiness Probes:** Misconfigured HTTP endpoints, port mismatches, or tight probe timeouts causing Kubernetes to kill healthy starting containers.
- **Missing Environment Variables or Secrets:** The application fails at startup due to missing configuration, database connection strings, or unmounted Secret objects.

## Example

Diagnostic commands workflow:

```bash
# Step 1: Check pod status and events
kubectl describe pod web-app-6d8f7b5c8-xyz -n production

# Step 2: Check logs of the crashed container (including previous run)
kubectl logs web-app-6d8f7b5c8-xyz -n production --previous --tail=100

# Step 3: Check node capacity and namespace quotas if Pending
kubectl describe node <node-name> | grep -A 10 "Allocated resources"
kubectl get resourcequota -n production

# Step 4: Inspect PVC status if waiting for storage
kubectl get pvc -n production
```

Checking for OOMKilled state in describe output:

```yaml
Last State:     Terminated
  Reason:       OOMKilled
  Exit Code:    137
  Started:      Fri, 07 Aug 2026 09:15:00 +0000
  Finished:     Fri, 07 Aug 2026 09:16:30 +0000
```

## Interview tips

- Always mention starting with `kubectl describe pod` to read the `Events` section — that immediately reveals if the scheduler failed or if a probe triggered a restart.
- Explain the distinction between `resources.requests` (used by scheduler for node placement) and `resources.limits` (enforced by cgroups, causing OOMKilled if memory limit is breached).
- Note that `kubectl logs --previous` is critical because standard `kubectl logs` might return empty if the container just restarted.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
