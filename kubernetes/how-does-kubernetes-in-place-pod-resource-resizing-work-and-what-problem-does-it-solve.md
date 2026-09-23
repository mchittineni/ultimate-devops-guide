---
title: "How does Kubernetes In-Place Pod Resource Resizing work and what problem does it solve?"
id: 522
category: "Kubernetes"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - kubernetes
  - resources
  - in-place-resize
  - vpa
quiz:
  stem: "What is the key operational advantage of Kubernetes In-Place Pod Resource Resizing?"
  options:
    - "It allows pods to consume more CPU than the physical node actually possesses"
    - "It mutates CPU and memory limits directly in the container cgroups without restarting the container process"
    - "It bypasses the need for Kubernetes worker nodes entirely"
    - "It automatically rewrites application code to be multithreaded"
  answer: 2
  explanation: "In-place resizing allows the Kubelet to adjust underlying cgroup boundaries on the fly, avoiding pod eviction, container restarts, and cache invalidation."
---

# How does Kubernetes In-Place Pod Resource Resizing work and what problem does it solve?

**Short answer:** In-place Pod resize makes a running container's CPU and memory requests and limits mutable, so they can be changed without evicting and recreating the Pod - and, for CPU and memory increases, usually without restarting the container. You send the change to the Pod's `resize` subresource, the kubelet checks it fits on the node, and then rewrites the container's cgroup limits live. It was alpha in Kubernetes 1.27, beta (on by default) in 1.33, and GA in 1.35. It removes the restart penalty from vertical scaling, but it cannot move a Pod to a bigger node, cannot change QoS class, and a memory shrink below current usage is still dangerous.

## Detail

**The problem it solves.** Before this feature, `spec.containers[*].resources` was immutable. Changing it - by hand or by the Vertical Pod Autoscaler - meant deleting the Pod and creating a new one, which costs:

- Cache invalidation and slow warm-up for JVM services, databases, and anything with a large in-memory working set.
- Dropped long-lived connections (WebSockets, gRPC streams) and restarted batch work.
- A trip through the scheduler, which may leave the replacement `Pending` if the cluster is full.

That made VPA's apply modes too disruptive for many teams, who ran it in recommendation-only mode instead.

**How a resize flows.**

1. **The request.** A client (a person, VPA, or an operator) patches the Pod's `resize` subresource. `spec.containers[*].resources` now holds the _desired_ values.
2. **Admission on the node.** The kubelet checks the new requests against the node's allocatable capacity. If it fits, it records the allocation (`status.containerStatuses[*].allocatedResources`). If not, it sets the Pod condition `PodResizePending` with reason `Deferred` (might fit later, for example once another Pod exits - the kubelet retries) or `Infeasible` (can never fit on this node, such as asking for more CPU than the node has).
3. **Actuation.** The kubelet asks the container runtime to update the container's cgroup (`cpu.max`/`cpu.weight`, `memory.max` on cgroup v2) while the process keeps running. `PodResizeInProgress` is set until the change is applied; `status.containerStatuses[*].resources` then shows the values actually in force.
4. **Restart policy.** Each container can declare a `resizePolicy` per resource: `NotRequired` (the default - apply live) or `RestartContainer` (restart this container to apply). Use `RestartContainer` for memory when the runtime sizes itself at startup, such as a JVM with a fixed `-Xmx`, because raising the cgroup limit alone does not grow the heap.

**Limitations and trade-offs.**

- Only CPU and memory can be resized, and the Pod's **QoS class cannot change** - a `Guaranteed` Pod must stay requests == limits.
- The Pod stays on its node. A resize that does not fit is `Deferred` or `Infeasible`, not rescheduled; only recreating the Pod moves it. (Kubernetes 1.37 adds alpha support for the scheduler preempting lower-priority Pods to make room for a pending resize.)
- **Decreasing a memory limit below current usage** can trigger an immediate OOM kill; the kubelet makes a best effort to avoid this but cannot reclaim memory the application is holding.
- Not supported on Windows nodes, with the static CPU manager or memory manager policies, or for regular (non-sidecar) init containers.
- The application must cope with the change: a process that reads its CPU count once at startup (thread-pool sizes, `GOMAXPROCS`) will not use extra CPU until it re-reads it.

**Where it fits with VPA.** VPA's `InPlaceOrRecreate` update mode uses this API, resizing in place when it can and evicting only when it cannot. That is what makes automatic vertical scaling acceptable for stateful and latency-sensitive workloads.

## Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api
spec:
  containers:
    - name: api
      image: registry.example.com/api:2.3.0
      resources:
        requests: { cpu: "500m", memory: "512Mi" }
        limits: { cpu: "1", memory: "1Gi" }
      resizePolicy:
        - resourceName: cpu
          restartPolicy: NotRequired # apply live
        - resourceName: memory
          restartPolicy: RestartContainer # heap is sized at start-up
```

```bash
# Raise CPU in place (kubectl 1.32+ supports --subresource resize)
kubectl patch pod api --subresource resize --type merge -p \
  '{"spec":{"containers":[{"name":"api","resources":{"requests":{"cpu":"1"},"limits":{"cpu":"2"}}}]}}'

# Did it apply, or is it pending?
kubectl get pod api -o jsonpath='{.status.containerStatuses[0].resources}{"\n"}'
kubectl get pod api -o jsonpath='{.status.conditions[?(@.type=="PodResizePending")]}{"\n"}'
kubectl get pod api -o jsonpath='{.status.containerStatuses[0].restartCount}{"\n"}'  # unchanged for CPU
```

## Interview tips

- Start with the problem: resources used to be immutable, so every vertical change was a Pod recreation with cold caches and dropped connections.
- Describe the mechanism: `resize` subresource, kubelet admission against node capacity, then a live cgroup update by the runtime.
- Know the states: `PodResizePending` with `Deferred` or `Infeasible`, then `PodResizeInProgress`. Old material shows a `status.resize` field; it was replaced by these conditions during beta.
- Name `resizePolicy` (`NotRequired` versus `RestartContainer`) and give the JVM heap as the reason to restart on memory changes.
- Volunteer the limits: no QoS class change, no move to another node, memory shrink can OOM, and apps that size thread pools at start-up will not see the new CPU.
- Link it to VPA's `InPlaceOrRecreate` mode - that pairing is why the feature matters in practice.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does the Kubernetes Controller Pattern implement declarative reconciliation loops?]] (`#622`): [How does the Kubernetes Controller Pattern implement declarative reconciliation loops?](../container-orchestration-advanced/how-does-the-kubernetes-controller-pattern-implement-declarative-reconciliation-loops.md)
- [[What is the difference between client-go Informers, Listers, and Reflector components?]] (`#625`): [What is the difference between client-go Informers, Listers, and Reflector components?](../container-orchestration-advanced/what-is-the-difference-between-client-go-informers-listers-and-reflector-components.md)
- [[What are Kubernetes Dynamic Resource Allocation (DRA) and Device Plugins for GPU/FPGA workloads?]] (`#626`): [What are Kubernetes Dynamic Resource Allocation (DRA) and Device Plugins for GPU/FPGA workloads?](../container-orchestration-advanced/what-are-kubernetes-dynamic-resource-allocation-dra-and-device-plugins-for-gpu-fpga-workloads.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
