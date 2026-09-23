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

A pod is stuck in `Pending` when the Kubernetes scheduler cannot find a node that satisfies its requirements (or, after scheduling, while images pull and volumes attach). The scheduler states its reason in the Pod's events, one clause per filter that rejected nodes - for example `0/6 nodes are available: 3 Insufficient cpu, 2 node(s) had untolerated taint {dedicated: gpu}, 1 node(s) didn't match Pod's node affinity/selector.` Read that message before guessing; if a cluster autoscaler is installed, its `NotTriggerScaleUp` event explains why it did not add a node either.

- **Resource Constraints:** Check if cluster nodes have available CPU or Memory matching the pod's `resources.requests`.
- **Taints and Tolerations:** Check if nodes are tainted (e.g. `node.kubernetes.io/unschedulable` or custom node taints) without matching tolerations in the Pod spec.
- **Node Selectors & Affinity:** Verify that node labels specified in `nodeSelector` or `nodeAffinity` match active nodes.
- **Unbound Persistent Volume Claim (PVC):** If using persistent storage, check if the PVC is in `Pending` state waiting for dynamic volume provisioning.
- **Namespace Quotas:** Check if a `ResourceQuota` on the namespace is preventing new pod creation.

### 2. Troubleshooting `CrashLoopBackOff` Pods

A pod in `CrashLoopBackOff` is continuously starting, failing, and restarting with exponential backoff delay (10 s, doubling up to a five-minute cap, reset after the container runs cleanly for ten minutes). `CrashLoopBackOff` is not the error itself - it is the kubelet waiting between restarts - so the cause is always in the previous container's exit code and logs.

- **Application Crash / Misconfiguration:** Inspect standard output and standard error logs. If the container restarted, run `kubectl logs <pod-name> -c <container-name> --previous` to see the exit logs from the killed instance.
- **OOMKilled (Exit Code 137):** Container process exceeded its `resources.limits.memory` and was terminated by the Linux OOM killer. Check `kubectl describe pod <pod-name>` under `Last State`.
- **Failing Liveness or Startup Probes:** Misconfigured HTTP endpoints, port mismatches, or tight probe timeouts cause the kubelet to kill containers that were merely slow to start. A failing **readiness** probe does not restart anything - it only removes the Pod from Service endpoints - so it produces a `Running` but `0/1 Ready` Pod, not a crash loop.
- **Exit codes:** `1` or another small number is the application's own failure; `137` is SIGKILL (OOM kill or a liveness-probe kill - `Reason` in `Last State` says which); `139` is a segfault; `126`/`127` mean the entrypoint is not executable or not found, usually a wrong `command` or an image built for another CPU architecture (`exec format error`).
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

```text
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
- Know the trade-off in the fix: raising memory limits or loosening probes stops the loop, but if the real cause is a leak or a hung dependency you have only slowed it down. Confirm the cause from the exit code and logs before changing the manifest.
- If the container exits too fast to inspect, `kubectl debug <pod> -it --copy-to=debug --container=<name> -- sh` starts a copy with a shell as the command, so you can poke at the filesystem and environment.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
