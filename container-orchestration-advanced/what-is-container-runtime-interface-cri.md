---
title: "What is Container Runtime Interface (CRI)?"
id: 85
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
---

# 85. What is Container Runtime Interface (CRI)?

**Short answer:** The Container Runtime Interface is the gRPC API through which the kubelet talks to a container runtime. It decoupled Kubernetes from Docker, allowing any compliant runtime — containerd, CRI-O — to be plugged in.

## Detail

**The problem it solved.** Originally the kubelet had Docker support compiled in. Supporting other runtimes meant patching Kubernetes itself. CRI defines a stable contract instead, with two services: **RuntimeService** (pod sandbox and container lifecycle, exec, logs) and **ImageService** (pull, list, remove images).

**The dockershim story.** Docker predates CRI and does not implement it, so Kubernetes shipped an adapter called dockershim. It was deprecated in 1.20 and removed in 1.24. This caused alarm, but the practical impact was minimal: Docker-built images are OCI images and run unchanged on containerd or CRI-O. Only tooling that talked to the Docker socket on nodes needed to change.

**The layers**

```text
kubelet ──CRI (gRPC)──▶ containerd / CRI-O ──OCI runtime spec──▶ runc / crun / gVisor / Kata
```

**Runtime options**

- **containerd** — the default on most managed Kubernetes services; also underpins Docker itself.
- **CRI-O** — purpose-built for Kubernetes, the default in OpenShift.
- **gVisor** — a user-space kernel providing stronger isolation for untrusted workloads.
- **Kata Containers** — lightweight VMs per pod for hardware-level isolation.

**RuntimeClass** lets you select different runtimes per workload, so untrusted tenant code can run under gVisor while trusted services use runc.

## Example

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata: { name: gvisor }
handler: runsc
---
apiVersion: v1
kind: Pod
metadata: { name: untrusted-job }
spec:
  runtimeClassName: gvisor # stronger isolation for this workload
  containers:
    - { name: job, image: ghcr.io/org/sandboxed-job:1.2 }
```

```bash
crictl ps            # the CRI-level equivalent of docker ps, on a node
```

## Interview tips

- Be able to explain calmly why "Kubernetes dropped Docker" did not break Docker images.
- The kubelet → CRI → OCI layering is the diagram to describe.
- RuntimeClass with gVisor or Kata is the answer to "how do you run untrusted workloads?"

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
