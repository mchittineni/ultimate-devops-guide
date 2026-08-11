---
title: "How do you choose between EBS, EFS, and S3?"
id: 479
category: "AWS Engineering"
difficulty: "Beginner"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - cloud-cost-optimization
---

# How do you choose between EBS, EFS, and S3?

**Short answer:** They are three different kinds of storage, not three products at different price points. **EBS is block storage**: a virtual disk attached to **one instance in one availability zone**, which you format with a filesystem - use it for boot volumes, databases, and anything needing low-latency random I/O. **EFS is a managed NFS filesystem**: mountable by **many instances across many AZs simultaneously**, elastic in size, with per-GB pricing several times EBS - use it when multiple writers genuinely need a shared POSIX filesystem. **S3 is object storage** accessed over an HTTP API, not a filesystem: unlimited, extremely durable (11 nines), cheapest per GB, with lifecycle tiering - use it for artefacts, backups, logs, media, data lakes, and static assets. The decision rule: **one writer with a filesystem → EBS; many writers needing a filesystem → EFS; anything an API can address → S3**, and prefer S3 whenever the access pattern allows, because it is the cheapest and needs no capacity management.

## Detail

### The comparison

|                      | EBS                                                     | EFS                                           | S3                                                    |
| -------------------- | ------------------------------------------------------- | --------------------------------------------- | ----------------------------------------------------- |
| Type                 | Block device                                            | NFS filesystem (POSIX)                        | Object store (HTTP API)                               |
| Attach scope         | **One AZ**, normally one instance                       | Multi-AZ, thousands of clients                | Regional, any client with credentials                 |
| Concurrent writers   | 1 instance (io1/io2 Multi-Attach is a narrow exception) | Many                                          | Many (per-object, last-write-wins)                    |
| Capacity             | Provisioned, must be grown deliberately                 | **Elastic** - grows and shrinks automatically | Effectively unlimited                                 |
| Latency              | Sub-millisecond                                         | Single-digit to low double-digit ms           | Tens of ms per request                                |
| Throughput model     | Per-volume IOPS/throughput (gp3 lets you set both)      | Elastic or provisioned                        | Scales with request concurrency                       |
| Durability           | Replicated within the AZ                                | Multi-AZ (One Zone class available)           | 11 nines, multi-AZ by default                         |
| Cost per GB          | Moderate                                                | **Highest** (~2-3× EBS for Standard)          | **Lowest**, and tiers down further                    |
| Filesystem semantics | Yes (you create it)                                     | Yes, shared, with locking                     | **No** - no directories, no partial writes, no rename |
| Snapshot / backup    | EBS snapshots (incremental, to S3)                      | AWS Backup                                    | Versioning + replication                              |

### The decision, as questions

1. **Does it need a POSIX filesystem?** If no - if the application can `PUT`/`GET` objects - use **S3**. Cheapest, no capacity to manage, lifecycle tiering, and durability you cannot match yourself.
2. **Do multiple machines need to write the same files at the same time?** Yes → **EFS**. No → **EBS**.
3. **Is latency critical and access random?** → **EBS** (gp3 for general purpose with independently provisioned IOPS and throughput, io2 Block Express for the extreme end).
4. **Is it archival?** → S3 with lifecycle to Glacier tiers, or EFS Infrequent Access if it must stay in a filesystem.

The frequently-asked EFS-versus-EBS question - _"which supports multiple nodes, which is cheaper, and which is faster?"_ - answers cleanly: **EFS** is the multi-node one; **EBS** is cheaper per GB and faster (lower latency, higher single-client IOPS); **EFS** wins only on sharing and elasticity. And **can EBS be attached to multiple nodes?** Normally no - it is a single-attach block device in one AZ, because two hosts writing to the same block device without a cluster-aware filesystem would corrupt it. io1/io2 Multi-Attach exists but requires a clustered filesystem and is not a general answer.

### Availability-zone binding, the constraint people forget

An EBS volume lives in **one AZ** and can only attach to an instance in that AZ. That has three consequences worth naming: a snapshot is the mechanism for moving a volume between AZs or regions (snapshot → create volume in the target AZ, or copy the snapshot cross-region); an instance replaced in another AZ cannot reattach the old volume; and in Kubernetes an EBS-backed PVC pins the Pod to one AZ, which is exactly why `volumeBindingMode: WaitForFirstConsumer` matters and why an EBS-backed workload cannot be `ReadWriteMany`.

The related "how do you back up an EBS volume and attach it to another server?" is a four-step answer: create a snapshot (incremental, stored in S3, safe to take on a running volume though quiescing gives a cleaner point), optionally copy it to the target region, create a volume **from the snapshot in the target AZ**, then attach and mount it (`lsblk`, `blkid`, `mount`, and `/etc/fstab` by UUID rather than device name, because device names are not stable).

### EBS volume types, briefly

**gp3** is the sensible default - baseline 3,000 IOPS and 125 MB/s included, both independently scalable, and cheaper than gp2 for the same performance. **io2 Block Express** for databases needing very high IOPS with a durability SLA. **st1/sc1** (HDD) for large sequential workloads like log processing, where throughput matters and random I/O does not. The gp2-to-gp3 migration is one of the easiest cost wins in AWS, and it is a good concrete answer when asked for cost optimisations you have implemented.

### EFS specifics

- **Performance modes**: General Purpose (default, lowest latency) versus Max I/O (higher throughput, higher latency, legacy). **Throughput modes**: Elastic (recommended - scales automatically, pay for what you use), Bursting (credit-based, and running out of burst credits is the classic EFS performance mystery), or Provisioned.
- **Storage classes**: Standard, One Zone (cheaper, single-AZ - accepts an AZ failure), and Infrequent Access with lifecycle management to move cold files automatically. Enable IA lifecycle; it is a large saving on typical file shares.
- **Access points** give a per-application root directory with an enforced POSIX UID/GID - the clean way to share one filesystem between workloads without them treading on each other.
- **Security**: encryption in transit (`-o tls` with the EFS mount helper) and at rest, plus a security group on the mount targets allowing 2049 from clients. A missing NFS rule is the usual cause of a mount that hangs.
- **Cost discipline**: EFS is priced per GB stored with no provisioning, so a runaway log directory is expensive quietly. Do not use EFS as a general dumping ground because it is convenient.

In Kubernetes, EFS is how you get `ReadWriteMany` - the answer to "how do you implement shared storage across multiple Pods on multiple nodes in EKS?" is the EFS CSI driver, not EBS. And "can you use EBS for shared storage if there is one node but multiple Pods?" - yes, actually: `ReadWriteOnce` means one **node**, so Pods co-located on that node can share the volume. Saying that precisely is a strong signal.

### S3 is not a filesystem

Worth stating explicitly, because treating it as one causes real problems: there are no real directories (only key prefixes), no partial writes or appends (you replace the whole object), rename is a copy-then-delete, listing a huge prefix is paginated and slow, and consistency is strong for reads after writes but there is no locking. Tools that mount S3 as a filesystem (`s3fs`, Mountpoint for Amazon S3) exist and are genuinely useful for read-heavy analytics, but they cannot make S3 behave like a POSIX filesystem for a database - do not put a database on it.

### The other options, so the answer is complete

- **Instance store** (NVMe attached to the host): fastest, and **ephemeral** - the data is gone when the instance stops. Correct for caches, scratch space, and shuffle data; wrong for anything you need to keep.
- **FSx**: managed Windows File Server (SMB, Active Directory), Lustre (HPC, and it can present S3 data), NetApp ONTAP, OpenZFS. The right answer when a lift-and-shift needs SMB or a specific enterprise filesystem - which is also the answer to "the monolith depends on a local filesystem, what do you replace it with?": EFS for POSIX, FSx for Windows/SMB.
- **Storage Gateway** for hybrid access from on-premises, and **DataSync** for bulk migration into any of them.

## Example

```text
Choosing, on a real system

  Boot volume, PostgreSQL data directory     -> EBS gp3          (low latency, one writer)
  Redis persistence / build scratch space    -> instance store   (ephemeral, fastest)
  User uploads read by 12 app replicas       -> S3               (API access, cheapest)
  Legacy CMS that writes to /var/www/shared  -> EFS              (many writers, POSIX)
  Windows app needing an SMB share           -> FSx for Windows  (AD-integrated SMB)
  Nightly database dumps kept 7 years        -> S3 + lifecycle   (Glacier/Deep Archive)
  Terabytes of logs scanned by Athena        -> S3 (Parquet)     (query in place)
```

```bash
# EBS: snapshot, then attach the copy to another instance (possibly another AZ)
SNAP=$(aws ec2 create-snapshot --volume-id vol-0abc123 \
  --description "orders-db $(date -u +%F)" --query SnapshotId --output text)
aws ec2 wait snapshot-completed --snapshot-ids "$SNAP"

VOL=$(aws ec2 create-volume --snapshot-id "$SNAP" \
  --availability-zone eu-west-1b --volume-type gp3 --iops 4000 \
  --query VolumeId --output text)                    # note: AZ of the TARGET instance
aws ec2 attach-volume --volume-id "$VOL" --instance-id i-0def456 --device /dev/sdf

# on the instance - mount by UUID, never by device name
lsblk && sudo blkid /dev/nvme1n1
echo "UUID=9f2c8b1d-... /data xfs defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo mount -a && df -h /data
```

```bash
# EFS: shared across AZs, TLS in transit, IA lifecycle for cost
aws efs create-file-system --encrypted --performance-mode generalPurpose \
  --throughput-mode elastic --tags Key=Name,Value=shared-uploads
aws efs put-lifecycle-configuration --file-system-id fs-0abc \
  --lifecycle-policies TransitionToIA=AFTER_30_DAYS TransitionToPrimaryStorageClass=AFTER_1_ACCESS

# one mount target per AZ, each with a security group allowing 2049 from clients
aws efs create-mount-target --file-system-id fs-0abc \
  --subnet-id subnet-0aaa --security-groups sg-0efs

sudo mount -t efs -o tls,iam fs-0abc:/ /mnt/shared     # encrypted in transit
```

```yaml
# Kubernetes: the same distinction, expressed as access modes
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: db-data }
spec:
  accessModes: ["ReadWriteOnce"] # EBS: one node, pinned to one AZ
  storageClassName: gp3
  resources: { requests: { storage: 200Gi } }
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: shared-uploads }
spec:
  accessModes: ["ReadWriteMany"] # EFS: many nodes, many AZs
  storageClassName: efs-sc
  resources: { requests: { storage: 100Gi } }
```

## Interview tips

- Open by classifying them - block, file, object - rather than comparing prices. Then give the decision rule: one writer with a filesystem → EBS, many writers with a filesystem → EFS, API-addressable → S3.
- Answer the EFS-versus-EBS trio precisely: EFS is the multi-node one, EBS is cheaper per GB and lower latency, EFS wins on sharing and elasticity.
- Say clearly that EBS is **single-AZ, single-attach** and explain why (two hosts writing raw blocks without a cluster filesystem corrupts data), then mention io2 Multi-Attach as the narrow exception so you sound precise rather than absolute.
- Volunteer the AZ consequence chain: snapshots are how you move a volume between AZs or regions, and an EBS-backed PVC pins a Pod to one AZ.
- Have the backup-and-attach steps ready: snapshot → (copy region) → create volume in the target AZ → attach → mount by UUID in `/etc/fstab`. Mounting by UUID rather than device name is a small detail that reads as real experience.
- Mention gp3 as the default and the gp2→gp3 migration as an easy cost win; it doubles as a concrete answer when asked what cost optimisations you have actually done.
- For shared storage in EKS, answer EFS CSI for `ReadWriteMany` - and add the nuance that `ReadWriteOnce` means one **node**, so co-located Pods can share an EBS volume.
- Say explicitly that S3 is not a filesystem - no appends, rename is copy-and-delete, no locking - and that mounting it does not change that. Then round out the answer with instance store (ephemeral, fastest) and FSx (SMB/Lustre) for the lift-and-shift cases. See [what are the S3 storage classes](./what-are-the-s3-storage-classes-and-when-do-you-use-each.md), [securing and managing the lifecycle of an S3 bucket](./how-do-you-secure-and-manage-the-lifecycle-of-an-s3-bucket.md), [how does persistent storage work in Kubernetes](../kubernetes/how-does-persistent-storage-work-in-kubernetes.md), and [containerising a legacy application](../cloud-migration/how-do-you-containerise-a-legacy-application-and-move-it-to-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
