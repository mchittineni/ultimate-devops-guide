---
title: "How do you back up and restore a Kubernetes cluster?"
id: 451
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
  - backup-and-disaster-recovery
  - kubernetes
---

# How do you back up and restore a Kubernetes cluster?

**Short answer:** There are three separate things to back up, and conflating them is the mistake. **(1) Cluster state** - every API object - which is either an `etcd` snapshot (self-managed control plane) or an object-level export with a tool such as **Velero** (the only option on EKS/GKE/AKS, where you have no etcd access). **(2) Persistent data** - the PersistentVolumes behind your stateful workloads, captured as CSI `VolumeSnapshot`s or filesystem backups, and for databases preferably by the database's own consistent backup rather than a disk snapshot. **(3) The things that are not in the cluster at all** - the Git repositories, container images, secret-manager contents, DNS, and the IaC that builds the cluster. The framing that wins: in a GitOps world the cluster is largely reproducible from Git, so what you truly cannot regenerate is **persistent data and secrets**; and a backup you have never restored is not a backup.

## Detail

### etcd snapshot versus Velero

|                                     | etcd snapshot                                   | Velero                                                               |
| ----------------------------------- | ----------------------------------------------- | -------------------------------------------------------------------- |
| Granularity                         | Whole cluster, all-or-nothing                   | Namespace, label selector, resource type                             |
| Works on managed clusters           | **No** - no etcd access on EKS/GKE/AKS          | Yes                                                                  |
| Restores into a _different_ cluster | Awkward at best                                 | Yes - the migration and DR path                                      |
| Captures PV data                    | No (only the PV/PVC objects)                    | Yes, via CSI snapshots or the file-level uploader                    |
| Speed of full recovery              | Very fast for the same cluster                  | Slower, object by object                                             |
| Typical use                         | Control-plane disaster on self-managed clusters | Everyday namespace restores, cluster migration, DR to another region |

Run **both** where you can: the etcd snapshot is your control-plane insurance, Velero is your workload insurance and your only way to restore selectively or into a new cluster.

Two etcd nuances worth stating: the snapshot must be paired with the **PKI material** in `/etc/kubernetes/pki` (restore the data without the CA and nothing trusts anything), and a restore is **cluster-wide time travel** - objects created after the snapshot vanish, which is precisely why you cannot use it to undo one bad namespace.

### Velero, concretely

Velero runs in-cluster, writes object manifests to an object store (S3/Blob/GCS), and delegates volume data either to **CSI snapshots** (fast, storage-native, stays in the region unless you replicate) or to its **file-system backup** uploader (kopia/restic - slower, but portable across storage classes and clouds, which is what makes cross-provider migration possible).

Essentials:

- **Schedules** with sensible retention (`--ttl`), and separate schedules for different tiers - hourly for the payments namespace, daily for everything else.
- **Hooks** (`pre.hook.backup.velero.io/command`) to quiesce an application - flush and lock a database, or trigger `pg_dump` - so the snapshot is consistent rather than a crash-consistent disk image.
- **Restore practice**: `velero restore create --from-backup daily-20260810 --include-namespaces payments --namespace-mappings payments:payments-restore` restores beside production so you can verify without risk.
- **Exclusions**: do not back up `kube-system` blindly, and exclude noisy or regenerable resources (events, `endpointslices`) to keep restores clean.
- **Protect the backup store**: object-lock/immutability and a separate account or subscription, because ransomware that reaches your cluster credentials will look for the backups next. This is the control most teams miss.

### Persistent data deserves its own answer

A CSI snapshot of a running database volume is **crash-consistent**, not application-consistent - it is equivalent to pulling the power. For anything transactional, take the database's own backup (`pg_basebackup` + WAL archiving, `mysqldump`/XtraBackup + binlogs, or the managed service's automated backups plus point-in-time recovery) and keep snapshots as the fast path for the filesystem. State your RPO explicitly: continuous WAL shipping gives minutes; a nightly snapshot gives up to 24 hours of loss, and that is a business decision, not a technical default.

Also remember StatefulSet PVCs deliberately survive Pod and even StatefulSet deletion, so "the workload is gone" does not mean the data is - and conversely `reclaimPolicy: Delete` means deleting a PVC destroys the disk.

### What must be backed up outside the cluster

- **Git** - manifests, Helm values, Terraform. With GitOps this is most of your cluster state, so the repository host's own backup and a mirror matter.
- **Container images** - a restore that cannot pull `registry.example.com/api:1.9.0` is not a restore. Replicate the registry or keep immutable digests plus a rebuild path.
- **Secrets** - if they live in Vault or a cloud secret manager (and they should), that store needs its own backup and its own restore rehearsal.
- **Cluster definition** - the Terraform/eksctl/Cluster API that recreates the control plane, node groups, IAM, VPC, and add-ons. "Rebuild the cluster from code, restore data into it" is a faster and cleaner DR story than repairing a broken cluster.
- **DNS and certificates** - so traffic can actually be pointed at the new cluster.

### The restore runbook, and rehearsing it

Order matters: build or repair the cluster → restore CRDs and operators → restore namespaces and objects → restore volumes → re-point DNS → verify. Write it down, then **run it on a schedule** into a throwaway cluster and record the measured RTO. Test the restore of one namespace monthly and a full cluster rebuild at least annually; that exercise is what turns a plausible plan into a real one and is exactly what interviewers are probing when they ask "have you tested it?"

## Example

```bash
# --- 1. Control plane: etcd snapshot (self-managed only) ---
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /backup/etcd-$(date +%F-%H%M).db
tar czf /backup/pki-$(date +%F).tgz /etc/kubernetes/pki   # useless without this
etcdutl snapshot status /backup/etcd-2026-08-10-0200.db --write-out=table
aws s3 cp /backup/ s3://acme-cluster-backups/prod/ --recursive   # off-cluster, object-locked
```

```bash
# --- 2. Workloads and volumes: Velero ---
velero install --provider aws --plugins velero/velero-plugin-for-aws:v1.10.0 \
  --bucket acme-velero --backup-location-config region=eu-west-1 \
  --features=EnableCSI --use-node-agent

# tiered schedules with retention
velero schedule create hourly-payments --schedule "0 * * * *" \
  --include-namespaces payments --ttl 168h --snapshot-volumes
velero schedule create daily-all --schedule "0 2 * * *" \
  --exclude-namespaces kube-system,velero --ttl 720h

# verify, then practise the restore beside production
velero backup describe daily-all-20260810020000 --details
velero restore create verify-$(date +%s) --from-backup daily-all-20260810020000 \
  --include-namespaces payments --namespace-mappings payments:payments-verify
velero restore logs verify-1754784000
```

```yaml
# Application-consistent backup: quiesce with hooks instead of hoping
apiVersion: v1
kind: Pod
metadata:
  name: mysql-0
  annotations:
    pre.hook.backup.velero.io/command: '["/bin/sh","-c","mysql -e \"FLUSH TABLES WITH READ LOCK; FLUSH LOGS;\""]'
    pre.hook.backup.velero.io/timeout: 3m
    post.hook.backup.velero.io/command: '["/bin/sh","-c","mysql -e \"UNLOCK TABLES;\""]'
---
# CSI snapshot class used by Velero for volume data
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-gp3
  labels: { velero.io/csi-volumesnapshot-class: "true" }
driver: ebs.csi.aws.com
deletionPolicy: Retain
```

```text
Restore runbook - rehearsed quarterly, RTO measured not estimated

  0. Decide: repair this cluster, or rebuild from IaC and restore into it?
  1. terraform apply     -> VPC, control plane, node groups, IAM, add-ons  (~20 min)
  2. install CRDs + operators + Velero                                     (~5 min)
  3. velero restore (namespaces in dependency order: data -> platform -> apps)
  4. verify volume data: row counts, checksums, application health checks
  5. re-point DNS / global load balancer, watch error rate and latency
  6. record actual RTO/RPO in the DR log; file gaps as work items
```

## Interview tips

- Split the answer into three buckets immediately - cluster state, persistent data, and out-of-cluster dependencies. Candidates who only say "etcd snapshot" have not run this in production.
- Say plainly that **etcd snapshots are not available on managed clusters**, so on EKS/GKE/AKS the answer is Velero. That single fact separates people who have done it from people who have read about it.
- Explain why you would run both: etcd for fast whole-cluster recovery, Velero for selective restores and restoring into a _different_ cluster.
- Volunteer the consistency point: a CSI snapshot of a live database is crash-consistent, so use hooks to quiesce or take the database's own backup with WAL/binlog shipping. Then tie it to an explicit RPO number.
- Mention that the etcd snapshot is worthless without the PKI material, and that an etcd restore is cluster-wide time travel - so it cannot undo one bad namespace.
- Bring up backup immutability and a separate account. If an attacker holds cluster credentials, unprotected backups are the next target.
- Close on rehearsal: describe the ordered runbook, say how often you test it, and give a measured RTO. "We restore one namespace monthly and rebuild a cluster annually" is the answer that ends the question. See [what is backup and disaster recovery](../backup-and-disaster-recovery/what-is-backup-and-disaster-recovery.md), [verifying that your backups can actually be restored](../backup-and-disaster-recovery/how-do-you-verify-that-your-backups-can-actually-be-restored.md), [executing a DR failover](../backup-and-disaster-recovery/how-do-you-execute-a-disaster-recovery-failover-with-minimal-rto-and-rpo.md), and [what happens when a control-plane node or etcd fails](../kubernetes/what-happens-when-a-kubernetes-control-plane-node-or-etcd-fails.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
