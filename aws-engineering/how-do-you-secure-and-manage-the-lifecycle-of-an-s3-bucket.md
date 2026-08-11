---
title: "How do you secure and manage the lifecycle of an S3 bucket?"
id: 478
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - security-and-compliance
  - cloud-cost-optimization
---

# How do you secure and manage the lifecycle of an S3 bucket?

**Short answer:** Security is five defaults you should never deviate from: **Block Public Access** on at the account and bucket level, **encryption** (SSE-S3 by default, SSE-KMS where you need key policy and audit), **versioning** plus a lifecycle rule for old versions, **a bucket policy that denies unencrypted and non-TLS access** and restricts the source (VPC endpoint, organisation, or specific principals), and **access logging or CloudTrail data events** so you can answer "who read this object?" ACLs are legacy - with Object Ownership set to `BucketOwnerEnforced` they are disabled entirely, and all access is decided by IAM plus the bucket policy. Lifecycle is a separate configuration: rules that **transition** objects between storage classes as they age (Standard → Standard-IA → Glacier Instant/Flexible → Deep Archive) and **expire** them - current versions, noncurrent versions, incomplete multipart uploads, and expired delete markers, all of which cost money if you leave them.

## Detail

### The security baseline

| Control              | Setting                                             | Why                                                                                                     |
| -------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Block Public Access  | On, at **account** level and bucket level           | The single control that prevents the classic public-bucket breach, regardless of policy or ACL mistakes |
| Object Ownership     | `BucketOwnerEnforced`                               | Disables ACLs entirely - one access model, no "the object has a different owner" surprises              |
| Default encryption   | SSE-S3, or SSE-KMS for regulated data               | Encryption at rest without relying on clients to ask                                                    |
| Bucket policy        | Deny non-TLS, deny unencrypted PUT, restrict source | Enforces the baseline even for principals with broad IAM permissions                                    |
| Versioning           | Enabled + MFA delete on critical buckets            | Recovers from overwrite and accidental delete; the basis of ransomware recovery                         |
| Object Lock          | Compliance or Governance mode where required        | Immutability for audit logs and backups; **must be enabled at bucket creation**                         |
| Logging              | Server access logs and/or CloudTrail data events    | Object-level audit trail                                                                                |
| Public access checks | Access Analyzer for S3, Config rules                | Continuous detection of drift, not a one-off review                                                     |

**SSE-KMS versus SSE-S3** matters more than it looks: KMS gives you a key policy (a second authorisation gate independent of IAM), CloudTrail records every decrypt, and you can revoke access by changing the key policy. The cost is per-request KMS charges - which **S3 Bucket Keys** reduce by up to 99% and should be enabled by default. For very high-volume workloads that is the difference between KMS being affordable and not.

### The bucket policy that does the work

Three deny statements cover most requirements, and denies are unconditional - they beat any IAM allow:

1. **Deny non-TLS**: `"Bool": {"aws:SecureTransport": "false"}`.
2. **Deny unencrypted uploads**: deny `s3:PutObject` when `s3:x-amz-server-side-encryption` is absent or not the expected value.
3. **Restrict the source**: `aws:SourceVpce` (only via our VPC endpoint), `aws:PrincipalOrgID` (only our organisation), or a principal list. This is the control that makes leaked credentials useless from outside your network - a genuinely strong posture and the thing most candidates never mention.

Note the distinction interviewers probe: **IAM policies** are attached to the identity and answer "what may this principal do?"; **bucket policies** are attached to the resource and answer "who may touch this bucket?" - and only a bucket policy can grant cross-account access to a resource or apply a condition to _everyone_, including principals in other accounts. **ACLs** are the legacy third mechanism, per-object, and should be off.

### Sharing a bucket with a user, properly

The full process, which comes up as a step-by-step question: create or identify the **principal** (ideally a role, not an IAM user with keys), attach an **identity policy** granting the specific actions on the specific bucket and prefix ARNs (both `arn:...:bucket` for `ListBucket` and `arn:...:bucket/*` for object actions - forgetting the first is why `aws s3 ls` fails while `cp` works), add a **bucket policy** statement if the principal is in another account, ensure the **KMS key policy** allows that principal if the bucket uses SSE-KMS, and then verify with `aws sts get-caller-identity` and an actual call. For temporary sharing with someone who has no AWS identity at all, use a **presigned URL** with a short expiry rather than making anything public.

The related debugging question - _a user has a role with a policy granting bucket access but still cannot access it_ - has a fixed checklist: an explicit **deny** somewhere (bucket policy, SCP, or a permissions **boundary**), a **KMS key policy** that does not include them, **Block Public Access** or a `SourceVpce`/`SourceIp` condition they do not satisfy, the missing bucket-level ARN, a **wrong region endpoint**, or an SCP at the organisation level. Name permission boundaries and SCPs explicitly - that is often the intended answer.

### Lifecycle configuration

Rules are per-prefix or per-tag and can do four independent things:

```text
Transitions (current versions)     Standard → Standard-IA (30d) → Glacier IR (90d)
                                            → Glacier Flexible (180d) → Deep Archive (365d)
Expiration (current versions)      delete after N days
NoncurrentVersionTransition/       old versions to cheaper classes, then delete
  NoncurrentVersionExpiration        (keep N newer versions with NewerNoncurrentVersions)
AbortIncompleteMultipartUpload     7 days  <- pure waste otherwise, and invisible in the console
ExpiredObjectDeleteMarker          tidies versioning artefacts
```

Three details that separate a real answer:

- **Minimum durations and per-object charges.** Standard-IA and One Zone-IA bill a 30-day minimum; Glacier Flexible 90 days; Deep Archive 180. There is also a per-object transition request charge, so transitioning millions of tiny objects can cost more than the storage you save. The rule of thumb: do not transition objects under ~128 KB.
- **Versioned buckets need noncurrent rules.** A bucket with versioning on and no noncurrent expiry grows forever, invisibly - "we delete objects but storage keeps rising" is always this. The scenario _"in a versioned bucket, how do you delete objects and all their older versions after 10 days?"_ is answered with `Expiration: 10 days` **plus** `NoncurrentVersionExpiration: 10 days` **plus** `ExpiredObjectDeleteMarker: true`.
- **Intelligent-Tiering** as the default for unpredictable access patterns: it moves objects between frequent and infrequent tiers automatically for a small monitoring fee per object, with no retrieval charges, which removes the need to guess. Prefer it over hand-written transitions unless you know the access pattern.

### Cost levers beyond storage class

- **Delete what nobody wants**: incomplete multipart uploads, old build artefacts, verbose logs with no retention.
- **Storage Lens** to find the buckets and prefixes actually driving the bill, and **Storage Class Analysis** before committing to transitions.
- **Requester Pays** for datasets consumed by other teams or customers.
- **Data transfer**: keep compute in the same region, use a **gateway VPC endpoint** so S3 traffic does not pay NAT processing charges, and put CloudFront in front of public read traffic so egress is cheaper and cached.
- **Fewer, larger objects**: request charges and per-object overheads dominate small-object workloads.

### Large uploads and integrity

Multipart upload splits a large object into parts, uploads them in parallel (and retries only failed parts), then completes. That is the answer to "how do you speed up a 10 GB upload?" - multipart with a tuned part size and concurrency, plus **S3 Transfer Acceleration** when the client is far from the bucket's region. And when a 10 GB upload fails after 5 GB, the parts are **still there, billed, and invisible in the object listing**: `aws s3api list-multipart-uploads` shows them, `list-parts` shows what arrived, and you either complete the upload or abort it - which is exactly why the `AbortIncompleteMultipartUpload` lifecycle rule belongs on every bucket. For integrity, use checksums (`--checksum-algorithm SHA256`) so corruption is detected rather than assumed away.

### Static websites without public access

The modern pattern: keep the bucket **private**, put CloudFront in front, and use **Origin Access Control** so only that distribution can read the bucket. You get TLS, a custom domain, caching, WAF, and no public bucket. The legacy S3 website endpoint requires public objects and is not the right answer any more.

### Replication

**Cross-Region Replication** needs versioning on both buckets, an IAM role for S3 to assume, and a replication configuration; it replicates **new** objects only unless you run S3 Batch Replication for existing ones. Uses: disaster recovery, data residency, and reducing latency for a second region. Same-Region Replication is used for log aggregation into a separate account and for compliance copies. Replication is asynchronous - so it is not a backup against logical deletion unless the destination has Object Lock or a different retention policy.

## Example

```hcl
# The baseline: private, encrypted, versioned, TLS-only, endpoint-restricted
resource "aws_s3_bucket" "data" { bucket = "acme-prod-data" }

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "data" {
  bucket = aws_s3_bucket.data.id
  rule { object_ownership = "BucketOwnerEnforced" } # ACLs disabled entirely
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.data.arn
    }
    bucket_key_enabled = true # cuts KMS request costs dramatically
  }
}

data "aws_iam_policy_document" "data" {
  statement { # 1. TLS only
    effect = "Deny"  actions = ["s3:*"]
    resources = [aws_s3_bucket.data.arn, "${aws_s3_bucket.data.arn}/*"]
    principals { type = "*"  identifiers = ["*"] }
    condition { test = "Bool"  variable = "aws:SecureTransport"  values = ["false"] }
  }
  statement { # 2. only through our VPC endpoint -> leaked keys are useless outside
    effect = "Deny"  actions = ["s3:*"]
    resources = [aws_s3_bucket.data.arn, "${aws_s3_bucket.data.arn}/*"]
    principals { type = "*"  identifiers = ["*"] }
    condition { test = "StringNotEquals"  variable = "aws:SourceVpce"
                values = [aws_vpc_endpoint.s3.id] }
  }
}
```

```hcl
# Lifecycle: transitions, expiry, noncurrent versions, and the multipart cleanup
resource "aws_s3_bucket_lifecycle_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    id     = "logs-tiering-and-expiry"
    status = "Enabled"
    filter { prefix = "logs/" }

    transition { days = 30  storage_class = "STANDARD_IA" }
    transition { days = 90  storage_class = "GLACIER_IR" }
    transition { days = 365 storage_class = "DEEP_ARCHIVE" }
    expiration { days = 2555 } # 7 years, then gone

    noncurrent_version_expiration {          # versioned buckets grow forever without this
      noncurrent_days           = 30
      newer_noncurrent_versions = 3
    }
    abort_incomplete_multipart_upload { days_after_initiation = 7 } # invisible waste
  }

  rule { # "delete objects AND all older versions after 10 days"
    id     = "ephemeral-exports"
    status = "Enabled"
    filter { prefix = "exports/" }
    expiration { days = 10 }
    noncurrent_version_expiration { noncurrent_days = 10 }
    expiration { expired_object_delete_marker = true }
  }
}
```

```bash
# The 10 GB upload that failed at 5 GB: the parts are there, and they are billed
aws s3api list-multipart-uploads --bucket acme-prod-data \
  --query 'Uploads[].[Key,UploadId,Initiated]' --output table
aws s3api list-parts --bucket acme-prod-data --key big.tar --upload-id "$UP" \
  --query 'sum(Parts[].Size)'                       # how many bytes actually arrived
aws s3api abort-multipart-upload --bucket acme-prod-data --key big.tar --upload-id "$UP"

# Faster large uploads: tuned multipart + acceleration
aws configure set default.s3.multipart_chunksize 64MB
aws configure set default.s3.max_concurrent_requests 20
aws s3 cp big.tar s3://acme-prod-data/ --checksum-algorithm SHA256

# Where is the storage and the money actually going?
aws s3api list-objects-v2 --bucket acme-prod-data --query \
  '[sum(Contents[].Size), length(Contents)]'
aws s3api get-bucket-metrics-configuration --bucket acme-prod-data --id EntireBucket

# Why can this role not read the bucket? Check for denies, not just allows.
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::111122223333:role/app \
  --action-names s3:GetObject --resource-arns arn:aws:s3:::acme-prod-data/x
aws accessanalyzer list-findings --analyzer-arn "$ANALYZER"   # unintended public/cross-account
```

## Interview tips

- Give the five-control baseline as a list - Block Public Access, encryption, versioning, a restrictive bucket policy, and logging - and say ACLs are legacy and disabled by `BucketOwnerEnforced`. Structure makes this answer sound like a standard you apply rather than facts you know.
- Distinguish IAM policy (identity, "what can this principal do") from bucket policy (resource, "who can touch this bucket", and the only place to grant cross-account or apply a condition to everyone). That comparison is asked directly.
- Volunteer the `aws:SourceVpce` / `aws:PrincipalOrgID` conditions as the control that makes leaked credentials useless from outside your network. Few candidates raise exfiltration prevention.
- On encryption, compare SSE-S3 with SSE-KMS in terms of key policy, CloudTrail visibility, and revocation - then mention S3 Bucket Keys as the way to make KMS affordable at volume.
- For lifecycle, cover all four rule types and lead with the two people forget: **noncurrent version expiry** (why storage grows despite deletions) and **AbortIncompleteMultipartUpload** (invisible, billed waste). Answer the versioned-delete-after-10-days scenario with expiration plus noncurrent expiration plus delete-marker cleanup.
- Mention minimum storage durations and per-object transition charges, and the "do not transition tiny objects" rule. Then offer Intelligent-Tiering as the default when access patterns are unknown.
- For the failed 5 GB of a 10 GB upload, answer with `list-multipart-uploads`/`list-parts` and note the parts are billed - then either complete or abort. That is the exact question, and the storage-cost consequence is the part that impresses.
- For static websites, give the private-bucket-plus-CloudFront-with-OAC pattern rather than the legacy public website endpoint.
- Have the "policy allows but access is denied" checklist ready: explicit deny, SCP, permissions boundary, KMS key policy, missing bucket-level ARN, or a source condition. See [what are the S3 storage classes](./what-are-the-s3-storage-classes-and-when-do-you-use-each.md), [how does AWS IAM evaluate a request](./how-does-aws-iam-evaluate-a-request.md), [what are VPC endpoints](./what-are-vpc-endpoints-and-when-do-you-use-a-gateway-versus-an-interface-endpoint.md), and [choosing between EBS, EFS, and S3](./how-do-you-choose-between-ebs-efs-and-s3.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
