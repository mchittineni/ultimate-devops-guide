---
title: "How does Kubernetes Storage Architecture coordinate CSI Plugins, Provisioners, and Attachers?"
id: 627
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - kubernetes
  - storage
  - csi
  - pvc
  - ebs
quiz:
  stem: "Which CSI component is responsible for calling cloud provider APIs to format a raw volume and bind-mount it into a Pod's local container directory?"
  options:
    - "The central `csi-provisioner` controller"
    - "The node-level CSI plugin executing `NodeStageVolume` and `NodePublishVolume`"
    - "The CoreDNS daemon"
    - "The kube-scheduler"
  answer: 2
  explanation: "While control-plane sidecars handle API provisioning and attachment, the node-level CSI daemon (running on the target worker) executes `NodeStageVolume` (formatting) and `NodePublishVolume` (mounting into the pod)."
---

# How does Kubernetes Storage Architecture coordinate CSI Plugins, Provisioners, and Attachers?

**Short answer:** A CSI driver is split into a **controller plugin** (a Deployment that talks to the storage backend's API) and a **node plugin** (a DaemonSet that mounts volumes on each node), both implementing the CSI gRPC interface. Kubernetes never calls the backend directly; instead, Kubernetes-maintained **sidecar containers** translate API objects into CSI calls: `external-provisioner` turns a PVC into `CreateVolume` and a PV, `external-attacher` turns a `VolumeAttachment` into `ControllerPublishVolume` (attach the disk to the node's VM), and on the node the kubelet calls `NodeStageVolume` (format and mount once per node) and `NodePublishVolume` (bind-mount into the Pod). `node-driver-registrar` only registers the node plugin's socket with the kubelet. This design lets storage vendors ship on their own release cycle, at the cost of several moving parts to debug.

## Detail

**Why CSI exists.** Volume plugins used to live in-tree in `k8s.io/kubernetes`, so every storage vendor's code shipped, and broke, with Kubernetes releases. CSI moved drivers out-of-tree; the in-tree cloud plugins (EBS, Azure Disk, GCE PD, and others) have since been migrated to CSI and removed.

**The components.**

| Component                                    | Runs as                                | Watches / is called by                     | CSI call(s)                                                |
| -------------------------------------------- | -------------------------------------- | ------------------------------------------ | ---------------------------------------------------------- |
| `external-provisioner`                       | Sidecar in the controller Deployment   | PVCs with its StorageClass                 | `CreateVolume`, `DeleteVolume`                             |
| `external-attacher`                          | Sidecar in the controller Deployment   | `VolumeAttachment` objects                 | `ControllerPublishVolume` / `ControllerUnpublishVolume`    |
| `external-resizer`                           | Sidecar in the controller Deployment   | PVC size increases                         | `ControllerExpandVolume`                                   |
| `external-snapshotter` + snapshot controller | Sidecar plus a cluster-wide controller | `VolumeSnapshot` / `VolumeSnapshotContent` | `CreateSnapshot`, `DeleteSnapshot`                         |
| Attach/detach controller                     | Inside kube-controller-manager         | Pods scheduled to nodes                    | Creates `VolumeAttachment` objects                         |
| kubelet                                      | Every node                             | Pods on its node                           | `NodeStageVolume`, `NodePublishVolume`, `NodeExpandVolume` |
| `node-driver-registrar`                      | Sidecar in the node DaemonSet          | kubelet plugin registration                | Registers the driver socket; no volume work                |

**The lifecycle of one volume.**

1. A PVC references a StorageClass whose `provisioner` is the driver name (for example `ebs.csi.aws.com`). With `volumeBindingMode: WaitForFirstConsumer`, the provisioner waits until the scheduler picks a node, so it can create the disk in that node's zone.
2. `external-provisioner` calls `CreateVolume`; the driver creates the disk and returns a volume handle; the sidecar creates a PV and Kubernetes binds it to the PVC.
3. The Pod is scheduled. The attach/detach controller creates a `VolumeAttachment` for (PV, node); `external-attacher` calls `ControllerPublishVolume`, and the driver attaches the disk to the VM. Drivers that do not need an attach step (many NFS or local drivers) declare `attachRequired: false` in their `CSIDriver` object and skip this.
4. The kubelet calls the node plugin's `NodeStageVolume` - format if empty (ext4/XFS) and mount at a per-node staging path - then `NodePublishVolume` to bind-mount it into `/var/lib/kubelet/pods/<uid>/volumes/...`, from where the runtime mounts it into the container.
5. Deletion reverses the chain: unpublish, unstage, detach, and (with `reclaimPolicy: Delete`) `DeleteVolume`.

**Trade-offs and failure points.** Every hop is a separate controller with its own logs, so a stuck volume needs you to find the right one: `ProvisioningFailed` on the PVC points at the provisioner (often cloud quota or IAM); a `VolumeAttachment` with an attach error points at the attacher; `FailedMount` on the Pod points at the node plugin. The node plugin must run on every node that may host the volume - a taint without a toleration on the DaemonSet produces mount timeouts. And the controller plugin's cloud credentials (IRSA, EKS Pod Identity, Workload Identity) are a common source of permission errors.

## Example

```yaml
# The CSIDriver object advertises capabilities to Kubernetes
apiVersion: storage.k8s.io/v1
kind: CSIDriver
metadata: { name: ebs.csi.aws.com }
spec:
  attachRequired: true # a VolumeAttachment / ControllerPublishVolume step is needed
  podInfoOnMount: false
  fsGroupPolicy: File
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: gp3 }
provisioner: ebs.csi.aws.com # routes PVCs to this driver's external-provisioner
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
parameters: { type: gp3, encrypted: "true" }
```

```bash
kubectl get csidrivers
kubectl get volumeattachments | grep pvc-8f1c           # attach step state per node
kubectl -n kube-system logs deploy/ebs-csi-controller -c csi-provisioner --tail=50
kubectl -n kube-system logs deploy/ebs-csi-controller -c csi-attacher --tail=50
kubectl -n kube-system logs ds/ebs-csi-node -c ebs-plugin --tail=50   # stage/publish errors
```

## Interview tips

- Separate controller plugin (backend API) from node plugin (mounts), and name the sidecars that bridge Kubernetes objects to CSI calls.
- Walk the lifecycle: PVC → `CreateVolume` → PV → `VolumeAttachment` → `ControllerPublishVolume` → `NodeStageVolume` → `NodePublishVolume`.
- Correct the common mistake: `node-driver-registrar` only registers the plugin; the node plugin itself formats and mounts.
- Mention `WaitForFirstConsumer` as the reason the provisioner can create zonal disks in the right zone.
- For debugging, map the symptom to the component: provisioning failures, attach failures, and mount failures each live in a different log.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
