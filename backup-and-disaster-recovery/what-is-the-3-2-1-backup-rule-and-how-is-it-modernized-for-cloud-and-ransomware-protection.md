---
title: "What is the 3-2-1 backup rule and how is it modernized for cloud and ransomware protection?"
id: 597
category: "Backup and Disaster Recovery"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - backup-and-disaster-recovery
  - backup
  - 3-2-1
  - ransomware
  - s3-object-lock
quiz:
  stem: "Why should critical cloud backups be stored in S3 buckets with Object Lock in Compliance Mode?"
  options:
    - "Compliance Mode compresses backups by 80%"
    - "It makes objects immutable (WORM), preventing any user—including the AWS root account—from deleting backups during a ransomware attack"
    - "It allows backups to be restored directly without a network connection"
    - "It bypasses AWS billing charges for object storage"
  answer: 2
  explanation: "In Compliance Mode, S3 Object Lock enforces strict WORM guarantees. Even compromised root or administrator credentials cannot delete or alter protected snapshots until the retention timer expires."
---

# What is the 3-2-1 backup rule and how is it modernized for cloud and ransomware protection?

**Short answer:** The classic 3-2-1 rule mandates 3 copies of data on 2 different media types with 1 copy stored offsite; modern cloud architectures extend this with 3-2-1-1-0 by adding an immutable/WORM (Write Once Read Many) air-gapped copy and zero-error automated restore validation.

## Detail

Ransomware attackers actively target backup catalogs first. If attackers compromise AWS root or IAM admin credentials, they delete production snapshots and S3 backups before encrypting the live disks.

### Modern Cloud 3-2-1-1-0 Rule

- **3 Copies of Data**: The production data plus two independent backup copies (for example, snapshots and an exported dump in another account). A live replica does not count - it replicates deletions and encryption just as faithfully as good writes.
- **2 Different Storage Formats**: E.g. block storage snapshot and exported database logical dump.
- **1 Offsite Copy**: Stored in a separate geographic cloud region or secondary cloud provider.
- **1 Immutable / Air-Gapped Copy**:
  - **S3 Object Lock (WORM)** in Compliance Mode: Prevents deletion or overwriting by ANY user, including the AWS root account, until the retention period expires.
  - **Separate AWS Account**: Backup vault in an isolated AWS account with no shared IAM roles or SSO links. AWS Backup Vault Lock (compliance mode) and logically air-gapped vaults give the same guarantee for AWS Backup recovery points; Azure immutable vaults and GCP backup vaults with enforced retention are the equivalents.
- **0 Errors**: Automated daily restore verification pipelines proving backups actually boot.

## Example

Create a bucket whose objects cannot be deleted by anyone, root included, for 30 days:

```bash
# Object Lock must be enabled at bucket creation (versioning is turned on automatically)
aws s3api create-bucket --bucket acme-backups-locked --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1 \
  --object-lock-enabled-for-bucket

aws s3api put-object-lock-configuration --bucket acme-backups-locked \
  --object-lock-configuration \
  '{"ObjectLockEnabled":"Enabled","Rule":{"DefaultRetention":{"Mode":"COMPLIANCE","Days":30}}}'
```

## Interview tips

- 3 copies, 2 media, 1 offsite.
- Ransomware targeting backups first to eliminate recovery leverage.
- Immutable backups using S3 Object Lock (Compliance mode / WORM).
- Air-gapped isolated AWS accounts and automated restore verification (the '0' errors).
- Know the trade-off of compliance mode: nobody can shorten the retention, so a mistake (a 10-year retention on a huge bucket) is a bill you cannot undo. Governance mode allows privileged override and is often used for testing the policy first.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
