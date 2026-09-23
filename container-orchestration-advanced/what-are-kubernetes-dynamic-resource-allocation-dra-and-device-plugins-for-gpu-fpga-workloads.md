---
title: "What are Kubernetes Dynamic Resource Allocation (DRA) and Device Plugins for GPU/FPGA workloads?"
id: 626
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - kubernetes
  - gpu
  - dra
  - device-plugins
  - ai-ml
quiz:
  stem: "What key limitation of traditional Kubernetes Device Plugins does Dynamic Resource Allocation (DRA) address for AI/ML workloads?"
  options:
    - "Device Plugins were unable to run on Linux servers"
    - "Device Plugins only supported coarse integer allocations of whole devices, whereas DRA enables fine-grained claims, fractional partitioning, and dynamic parameter configuration"
    - "Device Plugins required disabling all container security contexts"
    - "Device Plugins do not support NVIDIA GPUs"
  answer: 2
  explanation: "Device Plugins only permitted requesting whole integer devices (`nvidia.com/gpu: 1`). DRA provides a flexible claim architecture supporting fractional slices, custom configs, and topology awareness."
---

# What are Kubernetes Dynamic Resource Allocation (DRA) and Device Plugins for GPU/FPGA workloads?

**Short answer:** **Device plugins** are the original mechanism: a vendor DaemonSet registers a device type with the kubelet, which advertises it as an opaque integer extended resource (`nvidia.com/gpu: 8`), and a Pod asks for whole devices in `resources.limits`. **Dynamic Resource Allocation (DRA)**, GA since Kubernetes 1.34 as `resource.k8s.io/v1`, replaces the integer with a claim model like storage's PVCs: drivers publish devices and their attributes in `ResourceSlice` objects, admins define `DeviceClass`es, and workloads create `ResourceClaim`s whose CEL selectors describe what they need ("a GPU with at least 40 GiB of memory"). The scheduler then picks concrete devices. DRA brings attribute-based selection, sharing one device between Pods or containers, and per-claim configuration; the trade-off is that it needs DRA-capable drivers and is more complex than a single integer.

## Detail

**Device plugins, and their limits.**

- A vendor plugin (for example the NVIDIA device plugin) runs on each node, registers with the kubelet over a gRPC socket, and reports healthy devices. The node's `status.allocatable` shows `nvidia.com/gpu: 8`.
- A Pod requests `nvidia.com/gpu: 1`; the scheduler only counts integers, and the kubelet asks the plugin which device IDs to inject.
- Limitations: the scheduler knows nothing about device **attributes** (model, memory, interconnect), so you steer with node labels and affinity instead. Allocation is whole devices only; sharing (time-slicing, MIG partitions) is configured out-of-band on the node and exposed as more integer resources. A device cannot be shared between Pods under Kubernetes' control, and there is no per-request configuration.

**How DRA works.**

| Object                  | Who creates it       | Purpose                                                                                    |
| ----------------------- | -------------------- | ------------------------------------------------------------------------------------------ |
| `ResourceSlice`         | The DRA driver       | Publishes the devices on a node (or network-attached) with typed attributes and capacities |
| `DeviceClass`           | Cluster admin        | Names a category of device and base selectors/configuration, e.g. `gpu.example.com`        |
| `ResourceClaim`         | User or controller   | Requests one or more devices from a class, filtered by CEL expressions                     |
| `ResourceClaimTemplate` | User (in a workload) | Stamps out one claim per Pod, like `volumeClaimTemplates`                                  |

The scheduler evaluates claims against the published slices with **structured parameters** - it understands the attributes, so it can pick a node that actually has a matching device - and records the allocation in the claim's status. The kubelet then calls the driver on that node to prepare the device and inject it (via CDI) into the containers that reference the claim. Because the claim is an object, several containers or Pods can reference the same one to share a device.

Earlier alpha versions of DRA used a `ResourceClass` with opaque, driver-evaluated `parametersRef`; that "classic" design was removed in favour of structured parameters, so older blog posts and `v1alpha2` examples no longer apply.

**Beyond the core.** Newer releases add features on top of the GA core - for example, alternatives in a single request (`firstAvailable`, "an H100, or else two A100s"), partitionable devices, admin access for monitoring tools, and device health and taint handling - several of which are still beta or alpha, so check your cluster version before relying on them.

**Trade-offs.**

- You need a DRA driver for your hardware (NVIDIA, Intel, and others publish them); a device plugin and a DRA driver for the same devices on the same node do not coexist cleanly.
- Claims add objects and scheduling work; for "one whole GPU per Pod" on homogeneous nodes, a device plugin is simpler and still supported.
- Cluster autoscaler and Karpenter support for DRA is newer than the scheduler's, so check that node scale-up understands claims.

## Example

```yaml
# Classic device plugin: an integer, no attributes
apiVersion: v1
kind: Pod
metadata: { name: train-legacy }
spec:
  containers:
    - name: trainer
      image: registry.example.com/trainer:3.0.0
      resources:
        limits: { nvidia.com/gpu: 1 }
```

```yaml
# DRA (resource.k8s.io/v1): ask for a GPU by its attributes
apiVersion: resource.k8s.io/v1
kind: ResourceClaimTemplate
metadata: { name: large-gpu }
spec:
  spec:
    devices:
      requests:
        - name: gpu
          exactly:
            deviceClassName: gpu.example.com
            selectors:
              - cel:
                  expression: device.capacity["gpu.example.com"].memory.compareTo(quantity("40Gi")) >= 0
---
apiVersion: v1
kind: Pod
metadata: { name: train }
spec:
  resourceClaims:
    - name: gpu
      resourceClaimTemplateName: large-gpu # one claim generated for this Pod
  containers:
    - name: trainer
      image: registry.example.com/trainer:3.0.0
      resources:
        claims: [{ name: gpu }] # this container gets the allocated device
```

```bash
kubectl get deviceclasses
kubectl get resourceslices -o wide            # what each node's driver has published
kubectl get resourceclaims                    # allocated? which device, which node?
kubectl describe resourceclaim train-gpu-xxxxx
```

## Interview tips

- Explain device plugins in one line - integer extended resources registered through the kubelet - and name their limits: no attributes, whole devices, no managed sharing.
- Describe DRA's objects - `ResourceSlice`, `DeviceClass`, `ResourceClaim`, `ResourceClaimTemplate` - and the PVC analogy.
- Say that DRA is GA (`resource.k8s.io/v1` since 1.34) and uses structured parameters with CEL, so the scheduler understands device attributes. Flag `ResourceClass`/`parametersRef` examples as outdated.
- Mention sharing a claim across containers or Pods, and per-claim configuration, as the capabilities device plugins cannot offer.
- Be balanced: device plugins remain simpler for homogeneous whole-GPU workloads, and DRA needs vendor drivers and autoscaler support.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
