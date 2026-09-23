---
title: "How do you backup and restore Kubernetes state including etcd, PVCs, and cluster manifests?"
id: 600
category: "Backup and Disaster Recovery"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - backup-and-disaster-recovery
  - kubernetes
  - backup
  - etcd
  - velero
  - disaster-recovery
quiz:
  stem: "Which tool is the industry standard for backing up both Kubernetes cluster resource manifests and persistent storage volume snapshots in managed cloud environments (like EKS and GKE)?"
  options:
    - "Velero"
    - "Fluentd"
    - "Prometheus Alertmanager"
    - "CoreDNS"
  answer: 1
  explanation: "Velero is the CNCF standard tool for backing up, restoring, and migrating Kubernetes manifests and persistent storage volumes via cloud CSI snapshot integration."
---

# How do you backup and restore Kubernetes state including etcd, PVCs, and cluster manifests?

**Short answer:** Kubernetes DR requires backing up control-plane state via etcd snapshots (`etcdctl snapshot save`) and application workloads using tools like Velero, which synchronizes declarative manifests and orchestrates VolumeSnapshots (CSI) for PersistentVolumeClaims.

## Detail

Kubernetes clusters have state in two distinct layers:

1. **Control Plane State**: Stored in `etcd` (every manifest, ConfigMap, Secret, and CustomResourceDefinition).
2. **Application Persistent Data**: Stored in storage volumes (PersistentVolumeClaims backed by EBS, Ceph, Azure Disk).

### 1. Backing up etcd (Self-Managed Control Planes)

```bash
# etcdctl defaults to the v3 API since etcd 3.4, so ETCDCTL_API=3 is no longer needed
etcdctl snapshot save /var/backups/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Restore uses etcdutl (etcdctl snapshot restore was deprecated in 3.5 and removed in 3.6)
etcdutl snapshot restore /var/backups/etcd-snapshot.db --data-dir /var/lib/etcd-restored
```

The snapshot contains Secrets, so encrypt it and store it outside the cluster. Restoring etcd rewinds the whole cluster to that moment, which is why it is a last resort; namespace-level problems are better handled by restoring workloads.

### 2. Workload & Storage Backup with Velero

In managed Kubernetes (EKS, GKE, AKS), cloud providers manage etcd; teams use **Velero** for cluster DR:

- **Manifest Backup**: Exports all API resources in selected namespaces to compressed tarballs in S3/GCS.
- **Volume Backup**: Hooks into the CSI (Container Storage Interface) driver to trigger underlying cloud storage volume snapshots, or copies volume data file-by-file with its built-in Kopia uploader (file-system backup) when snapshots are unavailable or must leave the cloud provider.
- **Migration & DR**: Enables restoring an entire production namespace into a brand new cluster in another region with a single command:

  ```bash
  velero restore create --from-backup prod-backup-20260923
  ```

**Limitations.** CSI snapshots usually live in the same region and account as the volume, so they are not DR on their own - copy them out (Velero's snapshot data movement, or provider cross-region copy). Also, the cluster's desired state should already be in Git (GitOps), so manifest backups are the safety net and Git is the source of truth.

## Example

A scheduled Velero backup of one namespace, including CSI volume snapshots moved to object storage:

```bash
velero schedule create prod-daily \
  --schedule "0 2 * * *" \
  --include-namespaces prod \
  --snapshot-move-data \
  --ttl 720h

velero backup get                      # confirm backups are Completed, not PartiallyFailed
velero restore create --from-backup prod-daily-20260923020000 \
  --namespace-mappings prod:prod-restore-test   # restore test into a scratch namespace
```

## Interview tips

- Two layers of state: etcd (manifests/cluster state) and PVCs (application storage).
- `etcdctl snapshot save` for control-plane backups.
- Velero for managed Kubernetes clusters.
- CSI VolumeSnapshots for capturing persistent volumes.
- Point out that managed control planes (EKS, GKE, AKS) do not expose etcd, so Velero plus GitOps is the realistic answer there.
- Restore into a scratch namespace or cluster regularly - a `PartiallyFailed` backup nobody looked at is the common failure.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
