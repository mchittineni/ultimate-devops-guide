---
title: "How does persistent storage work in Kubernetes?"
id: 443
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - container-orchestration-advanced
---

# How does persistent storage work in Kubernetes?

**Short answer:** Storage is deliberately split into a **claim** and a **volume**. A **PersistentVolumeClaim** is the application's request - "I need 20 GiB, ReadWriteOnce, from this class" - and lives with the workload. A **PersistentVolume** is the actual piece of storage. A **StorageClass** names a provisioner (a CSI driver) plus its parameters, so when a PVC references a class the driver **dynamically provisions** a matching PV and binds it; static provisioning, where an administrator pre-creates PVs, is the older manual path. The container mounts the PVC, not the PV. The two facts that drive every real design decision: **access modes are enforced by the underlying storage** (a cloud block device is genuinely single-node, so `ReadWriteMany` needs a file service such as EFS, Azure Files, or NFS), and **`volumeBindingMode: WaitForFirstConsumer`** is what stops a volume being created in the wrong availability zone from the Pod that needs it.

## Detail

### The objects and how they fit together

```text
Pod ──mounts──> PVC ──bound to──> PV ──backed by──> real disk (via CSI driver)
                 │                  ▲
                 └──references──> StorageClass ──provisions──┘
```

- **PVC** - namespaced, part of the application. Requests size, access mode, optionally a class and a selector.
- **PV** - cluster-scoped, represents real capacity. Carries the CSI driver handle, capacity, access modes, reclaim policy, and node affinity (for zonal disks).
- **StorageClass** - the "kind of storage available here". Holds the provisioner, parameters (disk type, IOPS, filesystem, encryption key), `reclaimPolicy`, `allowVolumeExpansion`, and `volumeBindingMode`. One class is usually marked default.
- **CSI driver** - the out-of-tree plugin that actually creates, attaches, and mounts the device. In-tree cloud providers are gone; everything is CSI now.

Binding is one-to-one and exclusive: a bound PV serves exactly one PVC.

### Static versus dynamic provisioning

**Dynamic** (the norm): PVC → StorageClass → driver creates the disk → PV appears → bound. No human involved, and the disk's lifecycle follows the claim.

**Static**: an administrator creates PVs by hand describing existing storage (a pre-existing NFS export, a LUN, a disk with data already on it), and PVCs bind to whichever PV satisfies their request. Use it when the storage exists outside Kubernetes' control or you need to attach a specific volume - for example restoring a snapshot, or importing a database volume during a migration. Set `storageClassName: ""` on the PVC to opt out of the default class, or the class will provision a fresh empty disk instead of binding your prepared PV.

### Access modes - and the misconception

| Mode                      | Meaning                           | Reality                                                                                                                                    |
| ------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `ReadWriteOnce` (RWO)     | Read-write by one **node**        | Cloud block storage (EBS, Azure Disk, PD). Multiple Pods can share it **if they are on the same node** - which people misread as "one Pod" |
| `ReadOnlyMany` (ROX)      | Read-only by many nodes           | Common for shared reference data, snapshots                                                                                                |
| `ReadWriteMany` (RWX)     | Read-write by many nodes          | Needs a shared filesystem: EFS, Azure Files, Filestore, NFS, CephFS. **Not** available from plain block storage                            |
| `ReadWriteOncePod` (RWOP) | Read-write by exactly one **Pod** | The mode people usually mean when they say RWO; useful to guarantee a single writer                                                        |

Access modes are validated against what the driver supports, not merely honoured because you asked. "Can EBS be attached to multiple nodes?" - not in the normal case: it is a single-attach block device (io1/io2 multi-attach exists but requires a cluster-aware filesystem, so it is not a general answer). This is the reason a Deployment scaled from 1 to 3 replicas with one RWO PVC leaves two Pods `Pending` with a multi-attach or volume node-affinity error - all replicas share the one claim.

### The scheduling trap: `volumeBindingMode`

With `Immediate`, the driver provisions the disk as soon as the PVC is created - possibly in zone `a` - and then the scheduler is constrained to put the Pod in zone `a`. If that zone has no capacity, the Pod never schedules. With **`WaitForFirstConsumer`**, binding is deferred until a Pod is scheduled, so the disk is created in the zone the scheduler chose. Use it for any zonal block storage; it is the default on most managed clusters now and the answer to a whole family of `Pending` PVC and node-affinity failures.

### Lifecycle: reclaim policy, expansion, snapshots

- **`reclaimPolicy`**: `Delete` destroys the underlying disk when the PVC is deleted - fine for caches, dangerous for databases. `Retain` keeps the PV and the data as `Released`, so an operator must clean it up or re-bind it deliberately. Dynamic provisioning defaults to `Delete`; set `Retain` on any class that backs real data.
- **Expansion**: with `allowVolumeExpansion: true`, editing the PVC's `resources.requests.storage` grows the volume online (many drivers no longer require a Pod restart to resize the filesystem). You cannot shrink a PVC.
- **Snapshots**: `VolumeSnapshotClass` + `VolumeSnapshot` capture point-in-time state, and a new PVC can be created with `dataSource` pointing at a snapshot - the standard clone/restore path. Snapshots are per-volume and usually not application-consistent on their own, so quiesce or use the database's own backup for anything transactional.

### StatefulSets and `volumeClaimTemplates`

A Deployment shares one PVC across replicas; a **StatefulSet** with `volumeClaimTemplates` gives every replica **its own** PVC (`data-mysql-0`, `data-mysql-1`) with stable identity, which is what a replicated database needs. Those PVCs deliberately **survive** scale-down and Pod deletion so the data comes back with the same ordinal - which also means scaling down does not free the disks, and you must delete them yourself.

### Quotas and per-team limits

A `ResourceQuota` can cap `requests.storage`, `persistentvolumeclaims` count, and per-class usage (`gold.storageclass.storage.k8s.io/requests.storage`) in a namespace - the answer to "five teams share a cluster, how do you stop one consuming all the storage?"

## Example

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: gp3-retain }
provisioner: ebs.csi.aws.com
parameters: { type: gp3, iops: "4000", throughput: "250", encrypted: "true" }
reclaimPolicy: Retain # data outlives a deleted PVC
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer # provision in the zone the Pod lands in
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: postgres }
spec:
  serviceName: postgres
  replicas: 3
  selector: { matchLabels: { app: postgres } }
  template:
    metadata: { labels: { app: postgres } }
    spec:
      containers:
        - name: postgres
          image: postgres:16
          volumeMounts: [{ name: data, mountPath: /var/lib/postgresql/data }]
  volumeClaimTemplates: # one PVC per replica, stable across restarts
    - metadata: { name: data }
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: gp3-retain
        resources: { requests: { storage: 100Gi } }
```

```yaml
# RWX for a workload that genuinely needs many writers (uploads, shared cache)
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: shared-uploads }
spec:
  accessModes: ["ReadWriteMany"] # EFS / Azure Files / Filestore, not block storage
  storageClassName: efs-sc
  resources: { requests: { storage: 50Gi } }
---
# Restore: a new PVC cloned from a snapshot
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: data-postgres-0-restore }
spec:
  dataSource: { name: pg-nightly-2026-08-09, kind: VolumeSnapshot, apiGroup: snapshot.storage.k8s.io }
  accessModes: ["ReadWriteOnce"]
  storageClassName: gp3-retain
  resources: { requests: { storage: 100Gi } }
```

```bash
# Diagnose a PVC that will not bind
kubectl get pvc,pv
kubectl describe pvc data-postgres-0 | tail -20      # events name the real cause
kubectl get storageclass                             # is there a default? right binding mode?
kubectl get events --field-selector reason=ProvisioningFailed -A

# Grow a volume online
kubectl patch pvc data-postgres-0 -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'

# Re-use a Retained PV: clear the stale claimRef so it can bind again
kubectl patch pv pvc-9f2c8b1d -p '{"spec":{"claimRef":null}}'
```

## Interview tips

- Start with the separation of concerns - PVC is the request owned by the app, PV is the capacity, StorageClass is the recipe, CSI does the work - and say the Pod mounts the **claim**. That structure alone answers "what is the difference between a PV and a PVC?"
- Correct the RWO misconception explicitly: it is one **node**, not one Pod, and `ReadWriteOncePod` is the mode that means one Pod. Interviewers notice.
- Have the "Deployment with a PVC scaled to 3 replicas" answer ready: they all share one claim, so replicas on other nodes stay `Pending` on multi-attach - and the fix is a StatefulSet with `volumeClaimTemplates` or an RWX filesystem.
- Name `WaitForFirstConsumer` and explain the zone-mismatch failure it prevents. This is the single most useful piece of storage trivia in a real cluster.
- Talk about `reclaimPolicy: Retain` for anything holding data, and warn that StatefulSet PVCs survive scale-down - so "we scaled to zero" does not stop the storage bill.
- Mention volume expansion (grow only, never shrink) and snapshot-to-PVC restore as the clone path.
- Close with quotas per namespace and class for multi-tenant clusters. See [how do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim](./how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md), [what are StatefulSets in Kubernetes](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md), [running and scaling a stateful application on Kubernetes](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md), and [how do you back up and restore a Kubernetes cluster](../container-orchestration-advanced/how-do-you-back-up-and-restore-a-kubernetes-cluster.md).

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
