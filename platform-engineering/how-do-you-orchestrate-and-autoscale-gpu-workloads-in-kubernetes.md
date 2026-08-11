---
title: "How do you orchestrate and autoscale GPU workloads in Kubernetes?"
id: 240
category: "Platform Engineering"
difficulty: "Advanced"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# How do you orchestrate and autoscale GPU workloads in Kubernetes?

**Short answer:** Orchestrate GPU workloads in Kubernetes using the NVIDIA GPU Operator (for driver injection and container runtime configuration), partition GPUs via Multi-Instance GPU (MIG) or Time-Slicing, and autoscale GPU nodes using Karpenter or KEDA based on GPU duty cycle and VRAM utilization metrics.

## Detail

Running AI and machine learning workloads on Kubernetes requires specialized platform engineering patterns to manage expensive hardware efficiently:

### 1. NVIDIA GPU Operator & Device Plugin

- **Automated Driver & Runtime Management:** The NVIDIA GPU Operator deploys daemonsets that automatically install NVIDIA drivers, Container Toolkit, CUDA libraries, and the Kubernetes Device Plugin (`nvidia.com/gpu`).
- **Resource Allocation:** Pods declare GPU requirements in their specification (`resources.limits.nvidia.com/gpu: "1"`).
- **Know the ceiling:** the device-plugin model can only express a whole-number count of an opaque resource. "Two of `nvidia.com/gpu`" cannot say _which_ GPU, how much VRAM, or what topology - so operators end up encoding hardware in node labels and affinity rules, exactly as the example below does.

### 1b. Dynamic Resource Allocation (DRA) - the current direction

- **DRA reached GA in Kubernetes 1.34** (September 2025) and is enabled by default. It replaces the integer-count model with a declarative request: a `DeviceClass` describes a family of hardware, a `ResourceClaim` asks for a device matching real attributes ("a GPU with at least 40 GB of memory"), and the scheduler resolves the allocation.
- **Why it matters:** sharing, topology awareness, and multi-device claims become first-class instead of node-label conventions. The DRA extended-resource bridge lets existing `nvidia.com/gpu` workloads migrate incrementally rather than in one cutover.
- **What to say in an interview:** device plugins are still what most production clusters run today, but describing them as the only option now dates the answer. Name DRA, say it went GA in 1.34, and explain the attribute-based request as the reason it exists.

### 2. GPU Partitioning: MIG vs Time-Slicing

Hardware GPUs are expensive; sharing them across lightweight workloads is essential:

- **Multi-Instance GPU (MIG):** Hard physical partition of a single A100/H100 GPU into up to 7 isolated GPU instances with dedicated compute, memory, and memory bandwidth guarantees. Ideal for multi-tenant production inference.
- **Time-Slicing:** Soft temporal sharing of a single GPU across multiple pods. Ideal for development, staging, or lightweight model development where physical isolation is not mandatory.

### 3. GPU Autoscaling (Node Provisioning & Pod Scaling)

- **Karpenter / Cluster Autoscaler:** Provisions GPU instance types (e.g. AWS `g5.xlarge`, `p4d.24xlarge`, GCP `g2-standard`) on demand based on pending pod resource requests, automatically terminating them when idle to reduce cloud spend.
- **KEDA (Kubernetes Event-driven Autoscaling):** Scales inference pods up or down based on metrics like HTTP request queue depth, request latency, or NVIDIA DCGM GPU memory utilization.

## Example

Deployment requesting a dedicated NVIDIA GPU with node affinity:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-inference-worker
  namespace: ai-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gpu-inference
  template:
    metadata:
      labels:
        app: gpu-inference
    spec:
      tolerations:
        - key: "nvidia.com/gpu"
          operator: "Exists"
          effect: "NoSchedule"
      nodeSelector:
        accelerator: nvidia-tesla-a10g
      containers:
        - name: cuda-worker
          image: nvcr.io/nvidia/pytorch:26.05-py3
          command: ["python3", "serve_model.py"]
          resources:
            limits:
              nvidia.com/gpu: 1
              memory: 32Gi
              cpu: "8"
            requests:
              nvidia.com/gpu: 1
              memory: 16Gi
              cpu: "4"
```

Configuring NVIDIA Time-Slicing via ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: time-slicing-config
  namespace: gpu-operator
data:
  any: |-
    version: v1
    sharing:
      timeSlicing:
        resources:
          - name: nvidia.com/gpu
            replicas: 4
```

## Interview tips

- Differentiate clearly between **MIG** (hardware-level isolation for A100/H100) and **Time-Slicing** (software-level sharing across all GPU architectures).
- Explain why standard HPA (CPU/Memory scaling) fails for GPU workloads: GPUs require scaling based on VRAM consumption, queue length, or DCGM metrics (`DCGM_FI_DEV_GPU_UTIL`).
- Emphasize node provisioning with **Karpenter**: Karpenter handles heterogeneous GPU instance constraints much faster than legacy Cluster Autoscaler.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure Terraform code for multiple environments and providers?]] (`#422`): [How do you structure Terraform code for multiple environments and providers?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [[What is Infrastructure as Code?]] (`#26`): [What is Infrastructure as Code?](../infrastructure-as-code/what-is-infrastructure-as-code.md)
- [[What is Ansible?]] (`#28`): [What is Ansible?](../infrastructure-as-code/what-is-ansible.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
