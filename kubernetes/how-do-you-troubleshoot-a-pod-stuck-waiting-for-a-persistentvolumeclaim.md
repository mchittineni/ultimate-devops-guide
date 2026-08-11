---
title: "How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?"
id: 407
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - container-orchestration-advanced
  - aws-engineering
---

# How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?

**Short answer:** Read the PVC's events first - `kubectl describe pvc` names the cause almost every time. Then work through the five things that stop a claim binding or attaching: **no StorageClass** (or no default, so the claim waits for a volume nobody will create), **provisioner failure** (quota, permissions, or the CSI driver not running), **a mismatch between claim and volume** (size, `accessModes`, `storageClassName`, selector), **zone affinity** - an EBS or zonal disk exists in one availability zone and the Pod was scheduled in another, which is the single most common production case - and **`ReadWriteOnce` already attached to a different node**, which blocks the new Pod until the old attachment is released.

## Detail

### Distinguish the two stuck states

- **PVC `Pending`** - no volume is bound yet. The problem is provisioning or matching.
- **PVC `Bound` but the Pod is `Pending` or `ContainerCreating`** - the volume exists but cannot be attached or mounted to this node. The problem is topology, an existing attachment, or the CSI node plugin.

`kubectl describe pod` and `kubectl describe pvc` tell you which, and the Pod's events carry the attach/mount errors (`FailedAttachVolume`, `FailedMount`, `Multi-Attach error`, `volume node affinity conflict`).

### PVC Pending: provisioning and matching

- **No StorageClass named and no default.** The claim sits for ever with `no persistent volumes available for this claim and no storage class is set`. Check `kubectl get storageclass` for the `(default)` marker; a cluster can have zero or - worse - two defaults.
- **`volumeBindingMode`.** `WaitForFirstConsumer` is _correct_ behaviour for zonal storage: the PVC intentionally stays `Pending` until a Pod is scheduled, so the volume is created in the right zone. A PVC pending with no Pod using it is not a fault. `Immediate` provisions at once and is what causes zone mismatches later.
- **Provisioner failure.** Read the CSI controller's logs. The recurring causes are cloud quota (volume count or GiB limit in the region), IAM permissions missing for the CSI controller's role (on EKS, the `ebs-csi-controller` service account needs its policy through IRSA or Pod Identity), an invalid parameter in the StorageClass (unsupported volume type, `iops` on a type that does not accept it), or the driver simply not installed - a cluster upgraded past the removal of in-tree providers needs the CSI driver deployed.
- **Static PV mismatch.** When you pre-create PVs, all of these must satisfy the claim: capacity ≥ requested, `accessModes` superset, matching `storageClassName` (including both being empty), the PV not already `Bound` or `Released`, and any `selector`/`volumeName` matching. A `Released` PV is not reusable until you clear its `claimRef`.
- **Namespace and quota.** A `ResourceQuota` on `requests.storage` or `persistentvolumeclaims` count blocks creation - the message appears in the PVC's events.

### PVC Bound but the Pod will not start

- **Zone / topology conflict.** `volume node affinity conflict` means the PV lives in `us-east-1a` and the scheduler wants a node elsewhere. Zonal block storage (EBS, Azure managed disks, GCE PD) cannot cross zones. This is why a Pod that was fine yesterday is unschedulable today after a node group changed - and why `WaitForFirstConsumer` plus topology-aware provisioning is the fix, not a workaround. Restoring from a snapshot into the target zone is the recovery path for an existing volume.
- **`Multi-Attach error`** - a `ReadWriteOnce` volume is still attached to another node. Usual causes: a rolling update with the old Pod not yet terminated (use `Recreate` for single-writer volumes, or a StatefulSet), or a node that went `NotReady` without releasing the attachment, which needs the `VolumeAttachment` cleared or the node object deleted before the controller will detach. If several Pods genuinely need shared write access, you need `ReadWriteMany` - EFS, Azure Files, or NFS - not a bigger EBS volume.
- **CSI node plugin missing or unhealthy on that node.** The DaemonSet must be running there; a tainted node without the toleration, or a node that came up before the driver, produces mount timeouts.
- **fsGroup and permission failures.** The volume mounts but the application cannot write. Set `securityContext.fsGroup` so the kubelet chowns the volume, and remember `fsGroupChangePolicy: OnRootMismatch` to avoid a slow recursive chown on large volumes.
- **Filesystem or expansion state.** A resize needs `allowVolumeExpansion: true` on the StorageClass, and some drivers require a Pod restart to complete the filesystem grow (`FileSystemResizePending`). Shrinking is never supported.

### The habits that prevent this class of problem

Set an explicit `storageClassName` in every claim rather than relying on the cluster default; use `WaitForFirstConsumer` for zonal storage; keep `reclaimPolicy: Retain` for anything holding real data so a deleted PVC does not delete the disk; take snapshots (`VolumeSnapshot`) before risky operations; and monitor volume fill level, because a full PVC is a different and much worse incident than a pending one. See [what are StatefulSets in Kubernetes](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md) and [how do you run and scale a stateful application on Kubernetes](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md).

## Example

```bash
# 1. The events name the cause - start here, always
kubectl describe pvc data-checkout-0 -n prod | tail -20
# Events:  ProvisioningFailed  ... failed to provision volume with StorageClass "gp3":
#          rpc error: code = Internal desc = could not create volume: VolumeLimitExceeded

# 2. Is there a StorageClass, and is one actually the default?
kubectl get storageclass          # look for "(default)" - zero or two are both bugs
kubectl get pvc -n prod -o wide   # STATUS, VOLUME, CAPACITY, ACCESS MODES, STORAGECLASS

# 3. Bound but not mounting? The Pod's events carry attach/mount errors
kubectl describe pod checkout-0 -n prod | grep -A6 Events
#   Warning  FailedScheduling  ... 1 node(s) had volume node affinity conflict
#   Warning  FailedAttachVolume ... Multi-Attach error for volume "pvc-8f1c..."

# 4. Who is holding a ReadWriteOnce volume?
kubectl get volumeattachment | grep pvc-8f1c
kubectl get pv pvc-8f1c... -o jsonpath='{.spec.nodeAffinity}{"\n"}'   # which zone?

# 5. Provisioner side
kubectl -n kube-system logs -l app=ebs-csi-controller -c csi-provisioner --tail=50
kubectl get csidrivers && kubectl -n kube-system get ds -l app=ebs-csi-node
```

```yaml
# Zonal storage done correctly: bind late, expandable, keep the data on delete
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: gp3 }
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer # provision in the zone the Pod lands in
allowVolumeExpansion: true
reclaimPolicy: Retain # a deleted PVC must not delete real data
parameters: { type: gp3, encrypted: "true" }
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: data-checkout, namespace: prod }
spec:
  storageClassName: gp3 # explicit: never rely on the cluster default
  accessModes: [ReadWriteOnce] # RWO = one node at a time; use RWX (EFS) to share
  resources: { requests: { storage: 100Gi } }
```

## Interview tips

- Say "I read the PVC's events first" before anything else. The API tells you the cause; candidates who start theorising about storage classes without looking lose the point.
- Separate `Pending` PVC from bound-but-unmountable in your answer. They have entirely different causes and the distinction shows you have debugged both.
- `WaitForFirstConsumer` is the detail that marks experience: explain that a pending PVC with no consumer is expected behaviour and that it exists to solve zone placement.
- Volume node affinity conflict is the highest-value war story - zonal disks cannot cross availability zones, so the Pod is unschedulable and the fix is a snapshot restore into the target zone.
- Know the `Multi-Attach` cause (RWO still attached, often a lost node) and that the real fix for genuine sharing is `ReadWriteMany` storage, not a larger disk.
- Mention `fsGroup` for the write-permission variant, and `allowVolumeExpansion` plus no-shrink for resize questions.
- Close on prevention: explicit storage class, `Retain` for real data, snapshots before risky changes, and an alert on volume fill level.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you run an application across multiple Kubernetes clusters?]] (`#414`): [How do you run an application across multiple Kubernetes clusters?](../container-orchestration-advanced/how-do-you-run-an-application-across-multiple-kubernetes-clusters.md)
- [[How do you back up and restore a Kubernetes cluster?]] (`#451`): [How do you back up and restore a Kubernetes cluster?](../container-orchestration-advanced/how-do-you-back-up-and-restore-a-kubernetes-cluster.md)
- [[How do you run a multi-tenant Kubernetes cluster?]] (`#453`): [How do you run a multi-tenant Kubernetes cluster?](../container-orchestration-advanced/how-do-you-run-a-multi-tenant-kubernetes-cluster.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
