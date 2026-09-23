---
title: "What are the core differences between Cloud Object Storage, Block Storage, and File Storage?"
id: 545
category: "Cloud Platforms"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - cloud
  - storage
  - s3
  - ebs
  - efs
quiz:
  stem: "Which cloud storage type is optimal for training distributed machine learning models where hundreds of compute nodes must read and write concurrently to a shared POSIX file hierarchy?"
  options:
    - "Single-attach Block Storage (e.g. AWS EBS gp3)"
    - "Managed Shared File Storage (e.g. AWS EFS or FSx for Lustre)"
    - "Instance Store Ephemeral Swap Disks"
    - "Tape Archive Cold Storage"
  answer: 2
  explanation: "Managed file storage (NFS/POSIX) supports concurrent ReadWriteMany access across hundreds of instances simultaneously, allowing distributed workers to share directory trees."
---

# What are the core differences between Cloud Object Storage, Block Storage, and File Storage?

**Short answer:** **Block storage** presents a raw virtual disk to one VM (occasionally a few) for low-latency random I/O - you put a filesystem or database on it. **File storage** is a managed network filesystem (NFS or SMB) that many clients mount concurrently with shared POSIX-style semantics. **Object storage** is a flat namespace of whole objects accessed over an HTTP API, with effectively unlimited capacity and the lowest cost per GB, but no in-place edits or POSIX semantics.

## Detail

| Dimension         | Block (EBS, Persistent Disk/Hyperdisk, Azure Managed Disks) | File (EFS, FSx, Filestore, Azure Files)       | Object (S3, Cloud Storage, Azure Blob)         |
| ----------------- | ----------------------------------------------------------- | --------------------------------------------- | ---------------------------------------------- |
| Interface         | Block device (NVMe/virtio) - you format it                  | NFS / SMB mount, directories and file locks   | HTTP API: `PUT`, `GET`, `DELETE`, `LIST`       |
| Concurrent access | One instance (multi-attach only on specific disk types)     | Hundreds or thousands of clients              | Unlimited clients                              |
| Latency           | Sub-millisecond to low milliseconds                         | Low milliseconds                              | Tens of milliseconds to first byte             |
| Scope             | One AZ (zonal) - regional variants exist on GCP and Azure   | Regional (multi-AZ) or single-AZ tiers        | Regional or multi-region, highly durable       |
| Scaling           | Provisioned size; resize explicitly                         | Elastic (EFS) or provisioned (FSx, Filestore) | Grows automatically                            |
| Cost per GB       | Medium                                                      | Highest                                       | Lowest, with colder tiers cheaper still        |
| Typical use       | Databases, boot volumes, single-writer apps                 | Shared content, lift-and-shift apps, ML/HPC   | Backups, data lakes, media, static sites, logs |

**Mechanisms that matter in design.**

- **Block** gives you byte-level updates and full control of the filesystem, which is why databases want it - but the volume is tied to a zone, so HA needs replication at the database layer or snapshots copied elsewhere.
- **File** handles sharing and locking for you, but every operation is a network round trip, so metadata-heavy workloads (millions of small files) are slow and throughput often scales with provisioned capacity or throughput mode. Specialized variants exist: FSx for Lustre for HPC/ML, FSx for NetApp ONTAP and Windows File Server for enterprise protocols.
- **Object** writes whole objects - "modifying" means rewriting the object. S3 has offered strong read-after-write consistency since 2020. Object storage is the default for anything large and shared, and analytics engines (Spark, Athena, BigQuery external tables) read it directly using open table formats such as Iceberg.

**Trade-off.** The cheapest tier is the least POSIX-like. Mounting object storage as a filesystem (Mountpoint for S3, Cloud Storage FUSE) is useful for read-heavy workloads but does not give you full POSIX semantics like renames and random writes.

## Example

```bash
# Block: a gp3 volume in one AZ, attached to one instance
aws ec2 create-volume --availability-zone eu-west-1a --size 100 --volume-type gp3 --iops 3000

# File: an encrypted EFS filesystem shared by many instances across AZs
aws efs create-file-system --encrypted --performance-mode generalPurpose --throughput-mode elastic

# Object: HTTP API, whole-object operations
aws s3 cp backup.tar.zst s3://acme-backups/2026/09/backup.tar.zst --storage-class STANDARD_IA
```

## Interview tips

- Anchor each type on its access interface: block device, network filesystem, HTTP API. The rest follows.
- Pick by access pattern: single-writer random I/O (block), many writers with shared paths (file), large immutable blobs at scale (object).
- Mention the zone scope of block volumes - it drives HA and recovery design.
- Call out the small-file performance problem on network filesystems and the lack of POSIX semantics in object storage.
- In Kubernetes terms: block usually maps to `ReadWriteOnce` volumes, file to `ReadWriteMany`, object is accessed by the application, not mounted as a PV (FUSE/CSI drivers aside).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How Do You Protect S3 Buckets from Accidental Deletion and Ransomware Attacks?]] (`#736`): [How Do You Protect S3 Buckets from Accidental Deletion and Ransomware Attacks?](../aws-engineering/how-do-you-protect-s3-buckets-from-accidental-deletion-and-ransomware-attacks.md)
- [[What is the difference between ECS, EKS, and Fargate?]] (`#193`): [What is the difference between ECS, EKS, and Fargate?](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- [[How do Auto Scaling groups and load balancers work together on AWS?]] (`#194`): [How do Auto Scaling groups and load balancers work together on AWS?](../aws-engineering/how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
