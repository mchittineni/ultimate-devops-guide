---
title: "What are the S3 storage classes and when do you use each?"
id: 195
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# What are the S3 storage classes and when do you use each?

**Short answer:** All classes share the same durability design (11 nines); they differ in availability, retrieval cost, retrieval latency, and minimum storage duration. Standard for hot data, Intelligent-Tiering when access is unpredictable, One Zone-IA for reproducible data, Glacier Instant/Flexible/Deep Archive as access frequency drops towards never.

## Detail

| Class                | Use when                                 | Watch out for                              |
| -------------------- | ---------------------------------------- | ------------------------------------------ |
| Standard             | active data, unknown-but-frequent access | most expensive per GB                      |
| Intelligent-Tiering  | access pattern unknown or changing       | small per-object monitoring fee            |
| Standard-IA          | accessed monthly, needs multi-AZ         | 30-day minimum, per-GB retrieval fee       |
| One Zone-IA          | reproducible data (derived, cached)      | lost if that AZ is lost                    |
| Glacier Instant      | archives needing millisecond access      | 90-day minimum                             |
| Glacier Flexible     | archives, minutes-to-hours retrieval     | 90-day minimum, retrieval jobs             |
| Glacier Deep Archive | compliance retention, 12-hour retrieval  | 180-day minimum, most expensive to restore |

**Minimum duration charges are the trap.** Moving an object to Standard-IA and deleting it after a week bills 30 days; Deep Archive bills 180. Lifecycle rules that transition objects too early routinely increase cost. Also note that each transition is a request charge - transitioning millions of tiny objects can cost more than the storage saved, which is why small objects should often be aggregated rather than tiered.

**Durability versus availability.** 11 nines of durability is a design property of replication within the region and is not a promise that your bucket is reachable - the availability SLA is separate and lower. And durability does not protect against deletion: versioning, MFA delete or bucket policies denying delete, Object Lock for compliance retention, and cross-region replication for regional loss are the actual protections. "S3 is durable, so we do not need backups" is a wrong answer.

**Intelligent-Tiering is the sane default for unknown patterns.** It moves objects between frequent, infrequent, and (optionally) archive tiers automatically with no retrieval fees between the instant-access tiers, charging a small monitoring fee per object. For large objects with unpredictable access it is usually cheaper than guessing; for millions of tiny objects the monitoring fee can dominate.

**Requester-side costs matter as much as storage.** Cross-region and internet egress, request charges (`GET`/`PUT`/`LIST`), and NAT processing when accessing S3 from private subnets without a gateway endpoint. Adding a free S3 gateway VPC endpoint is one of the highest-return single changes on many AWS bills.

## Example

```json
{
  "Rules": [
    {
      "ID": "logs-tiering",
      "Filter": { "Prefix": "logs/", "ObjectSizeGreaterThan": 131072 },
      "Status": "Enabled",
      "Transitions": [
        { "Days": 30, "StorageClass": "STANDARD_IA" },
        { "Days": 120, "StorageClass": "GLACIER_IR" },
        { "Days": 365, "StorageClass": "DEEP_ARCHIVE" }
      ],
      "Expiration": { "Days": 2555 },
      "NoncurrentVersionExpiration": { "NoncurrentDays": 30 }
    },
    {
      "ID": "abort-stalled-multipart",
      "Filter": {},
      "Status": "Enabled",
      "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 7 }
    }
  ]
}
```

## Interview tips

- Frame the classes along one axis - access frequency versus retrieval cost - rather than listing them.
- Minimum-duration charges and the incomplete-multipart cleanup rule are the two details that mark real bill-owning experience.
- Push back firmly on "durability means we do not need backups": versioning, Object Lock, and replication protect against deletion; durability does not.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
- [[How do you design least-privilege identity in the cloud?]] (`#217`): [How do you design least-privilege identity in the cloud?](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
