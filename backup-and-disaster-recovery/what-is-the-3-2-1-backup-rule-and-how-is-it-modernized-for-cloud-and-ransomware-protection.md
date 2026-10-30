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

**Short answer:** The classic 3-2-1 rule is three copies of the data, on two different media types, with one copy off-site. The modern **3-2-1-1-0** version adds **one immutable or logically air-gapped copy** that no production credential can delete or overwrite, and **zero errors** in automated restore tests. The additions exist because ransomware operators now go after the backups first.

## Detail

**Why the rule had to change.** A modern ransomware attack on a cloud estate usually starts with stolen admin credentials. Before encrypting anything, the attacker deletes snapshots, shortens retention, removes backup vaults, or re-encrypts objects with a key they control (in 2025 the "Codefinger" campaign used S3 server-side encryption with customer-provided keys, SSE-C, to do this). If production credentials can reach the backups, the backups are part of the blast radius.

### The 3-2-1-1-0 rule in the cloud

- **3 copies of data.** Production plus two independent backup copies, for example snapshots and an exported dump in another account. A live replica does not count, because it replicates deletions and encryption just as faithfully as good writes.
- **2 different storage formats.** For example a block-storage snapshot and a logical database dump, so one class of corruption or tooling bug cannot break both.
- **1 off-site copy.** A different region, and ideally a different account or provider.
- **1 immutable or air-gapped copy.**
  - **S3 Object Lock in Compliance mode** (WORM). No user, including the account root, can delete or overwrite a locked object version or shorten its retention until the retention period expires.
  - **AWS Backup Vault Lock** (compliance mode) and **logically air-gapped vaults**. The latter are locked by default, held in AWS-owned accounts, and can be shared to a recovery account through AWS RAM, so you can restore even if the source account is lost. Azure Backup **immutable vaults** (locked) with soft delete, and Google Cloud **Backup and DR backup vaults** with enforced minimum retention, are the equivalents.
  - **Separate security domain.** Backups go into a dedicated account with no trust from production roles and no shared SSO permission sets, and with its own break-glass access. Encrypt them with a KMS key owned by the backup account, because a key the attacker can schedule for deletion makes the copy useless.
- **0 errors.** Restore tests run automatically and prove the copies actually restore and boot. AWS Backup restore testing and GuardDuty Malware Protection for AWS Backup (scans of EBS snapshots, AMIs, and S3 recovery points) also help you find the last _clean_ recovery point instead of restoring the malware with the data.

**Recovering, not just restoring.** After a ransomware incident, restore into an **isolated recovery environment** (a clean account or VPC with no route to the compromised estate), scan and validate the data there, and only then promote it. Restoring straight into the compromised account lets the attacker hit the restored copy too.

**Trade-offs.** Compliance-mode retention cannot be shortened by anyone. A mistake, such as a 10-year retention on a huge bucket, is a storage bill you cannot undo, so trial the policy in governance mode first, where privileged users can override it. Air-gapped copies also make restores slower and harder to automate. That is the point of them, but your RTO has to account for it.

## Example

Turn on default compliance-mode retention for a backup bucket. Since late 2023 you can enable Object Lock on an existing bucket as long as versioning is on, so it no longer has to be set at creation:

```bash
aws s3api put-bucket-versioning --bucket acme-backups-locked \
  --versioning-configuration Status=Enabled

aws s3api put-object-lock-configuration --bucket acme-backups-locked \
  --object-lock-configuration \
  '{"ObjectLockEnabled":"Enabled","Rule":{"DefaultRetention":{"Mode":"COMPLIANCE","Days":30}}}'

# Proof: deleting a locked version fails, even for an administrator
aws s3api delete-object --bucket acme-backups-locked --key db/2026-10-29.dump --version-id "$VID"
# An error occurred (AccessDenied) ... object is WORM protected and cannot be overwritten
```

## Interview tips

- State 3-2-1 first, then explain why it grew to 3-2-1-1-0: ransomware goes for the backups first, so you need one copy that production credentials cannot touch.
- Name concrete immutability mechanisms: S3 Object Lock compliance mode, AWS Backup Vault Lock and logically air-gapped vaults, and Azure immutable vaults.
- Say that the backup account and its KMS key have to be a separate security domain. Immutability does not help if the attacker can delete the key.
- Describe recovery into an isolated, clean environment and scanning for the last clean recovery point. Restoring straight back into a compromised account is a common mistake.
- Know the compliance-mode trade-off: nobody can shorten the retention, so test the policy in governance mode first.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
