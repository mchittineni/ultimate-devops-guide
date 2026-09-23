---
title: "How Do You Protect S3 Buckets from Accidental Deletion and Ransomware Attacks?"
id: 736
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - s3
  - ransomware
  - data-protection
quiz:
  stem: "Under S3 Object Lock in 'Compliance Mode', who has permission to delete an object or shorten its retention period before the retention duration expires?"
  options:
    - "The AWS account root user."
    - "Any IAM administrator with the 'AdministratorAccess' policy."
    - "Nobody, including the AWS account root user and AWS Support."
    - "Only members of the AWS Organizations billing team."
  answer: 3
  explanation: "In S3 Object Lock Compliance Mode, a locked object version cannot be overwritten or deleted by any user, including the root user in your AWS account, until the retention period expires."
---

# How Do You Protect S3 Buckets from Accidental Deletion and Ransomware Attacks?

**Short answer:** S3 data protection combines S3 Versioning, S3 Object Lock (Write-Once-Read-Many / WORM compliance), MFA Delete, S3 Replication to an isolated account, and strict bucket policies denying unencrypted uploads and unauthorized deletions.

## Detail

### The Threat of Data Destruction in Cloud Storage

Amazon S3 holds critical backups, database dumps, and enterprise data lakes. Attackers who gain compromised administrative credentials frequently attempt to delete backups or encrypt objects with rogue keys (ransomware extortion).

### Multi-Layered S3 Defense Architecture

1. **S3 Versioning**:
   - Preserves all past revisions of every object. A simple `DELETE` request merely places a **delete marker**; the underlying data remains intact and recoverable.
2. **S3 Object Lock (WORM Storage)**:
   - Stores objects using a **Write Once, Read Many (WORM)** model.
   - **Compliance Mode**: Prevents object deletion or retention period alteration by **any** user, including the AWS account `root` user, until the retention period expires.
   - **Governance Mode**: Allows designated IAM users with special permissions to override locks while preventing standard admins from deleting files.
   - Object Lock requires versioning and can now be enabled on existing buckets, not only at bucket creation. Test with Governance mode first - a Compliance-mode retention set too long cannot be shortened, even by AWS Support.
3. **MFA Delete**:
   - Requires physical Multi-Factor Authentication (TOTP or hardware token) to permanently delete an object version or alter bucket versioning states.
   - Can only be enabled via the AWS CLI using the account `root` user credentials.
4. **Cross-Account S3 Replication**:
   - Replicates objects automatically to a separate, highly restricted AWS account (e.g., a dedicated SecOps Archive account).
   - Even if the production account is completely compromised, the destination account's bucket remains isolated.
5. **KMS Encryption with Restricted Key Policies**:
   - Encrypt objects with a customer-managed KMS key. Even if an attacker gains bucket access, denying access to the KMS key prevents unauthorized decryption or re-encryption.
6. **Block SSE-C**:
   - Ransomware campaigns have re-encrypted objects with SSE-C (customer-provided keys the victim never holds). Since April 2026 S3 disables SSE-C by default on new buckets (and on existing buckets in accounts with no SSE-C data); keep it disabled unless a workload genuinely needs it.
7. **AWS Backup logically air-gapped vaults**:
   - An alternative or complement to replication: backups stored in a vault owned by AWS Backup, locked, and shareable to a recovery account.

```text
[Application Write] ──► [S3 Bucket (Production)] ──► Versioning Enabled
                               │                      Object Lock: Compliance Mode
                               ▼ (Replication)
                        [S3 Bucket (Archive Account)]
                         Isolated IAM & Separate Root
```

### Real-World Production Scenario

A malicious insider with compromised administrative credentials logs into an organization's AWS account and issues an automated script to delete all customer backup buckets. Because S3 Object Lock in Compliance Mode was enabled with a 90-day retention period, the AWS API returns `Access Denied` on every deletion attempt, completely foiling the ransomware attack.

## Example

```bash
# Versioning, then Object Lock default retention (Governance first, Compliance once proven)
aws s3api put-bucket-versioning --bucket acme-backups \
  --versioning-configuration Status=Enabled
aws s3api put-object-lock-configuration --bucket acme-backups \
  --object-lock-configuration '{"ObjectLockEnabled":"Enabled",
    "Rule":{"DefaultRetention":{"Mode":"GOVERNANCE","Days":30}}}'

# Default to KMS with bucket keys (SSE-C stays blocked unless a rule explicitly allows it;
# PutBucketEncryption's BlockedEncryptionTypes setting controls that)
aws s3api put-bucket-encryption --bucket acme-backups \
  --server-side-encryption-configuration '{"Rules":[{
    "ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms","KMSMasterKeyID":"alias/backups"},
    "BucketKeyEnabled":true}]}'

# Recover from a "delete": remove the delete marker to restore the previous version
aws s3api list-object-versions --bucket acme-backups --prefix db/2026-09-20.dump \
  --query 'DeleteMarkers[?IsLatest].[Key,VersionId]' --output text
aws s3api delete-object --bucket acme-backups --key db/2026-09-20.dump --version-id "$MARKER_ID"
```

## Interview tips

- Highlight the difference between Governance Mode and Compliance Mode in S3 Object Lock: Compliance Mode cannot be overridden by ANYONE, including the root account.
- Explain that MFA Delete requires root credentials to configure and cannot be toggled via the standard AWS Web Console.
- Mention cross-account replication (with Object Lock on the destination) as the hedge against root credential compromise - replication alone also replicates deletes of new versions if configured to, so the destination needs its own retention.
- Know the newer threat: SSE-C re-encryption attacks, and the April 2026 default that disables SSE-C on new buckets.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core differences between Cloud Object Storage, Block Storage, and File Storage?]] (`#545`): [What are the core differences between Cloud Object Storage, Block Storage, and File Storage?](../cloud-platforms/what-are-the-core-differences-between-cloud-object-storage-block-storage-and-file-storage.md)
- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
