---
title: "What is Backup and Disaster Recovery?"
id: 61
category: "Backup and Disaster Recovery"
difficulty: "Beginner"
tags:
  - devops
  - backup-and-disaster-recovery
  - interview-questions
---

# What is Backup and Disaster Recovery?

**Short answer:** Backup is copying data so it can be restored after loss; disaster recovery is the broader capability of restoring an entire service after a major failure. Backup is one component of DR, not a substitute for it.

## Detail

|                  | Backup                           | Disaster Recovery                                         |
| ---------------- | -------------------------------- | --------------------------------------------------------- |
| Scope            | Data                             | Whole service: data, infrastructure, network, DNS, people |
| Protects against | Deletion, corruption, ransomware | Region outage, site loss, catastrophic failure            |
| Typical recovery | Hours                            | Minutes to days depending on strategy                     |
| Artifact         | Backup sets and retention policy | Runbook, replicated environment, failover automation      |

**The 3-2-1 rule** remains the baseline: three copies of the data, on two different media types, with one copy off-site. Modern practice extends it to **3-2-1-1-0**: one copy immutable or offline, and zero errors on verified restores.

**What good looks like**

- Backups are automated, monitored, and alert on failure - a silently failing backup job is the classic disaster.
- Retention matches business and regulatory need, with lifecycle transitions to cheaper storage.
- Backups are encrypted in transit and at rest, and stored in a separate account/subscription with different credentials, so compromised production access cannot destroy them.
- Object lock / immutability protects against ransomware.
- **Restores are tested on a schedule.** The only evidence a backup works is a successful restore.

The uncomfortable truth interviewers probe: most organisations have backups; far fewer have proven restores. "When did you last restore from backup, and how long did it take?" is the question that separates the two.

## Example

An AWS Backup plan that covers both halves - a local backup for everyday restores, plus a copy to another region for DR:

```json
{
  "BackupPlanName": "prod-daily",
  "Rules": [
    {
      "RuleName": "daily-35d",
      "TargetBackupVaultName": "prod-vault",
      "ScheduleExpression": "cron(0 3 * * ? *)",
      "Lifecycle": { "DeleteAfterDays": 35 },
      "CopyActions": [
        {
          "DestinationBackupVaultArn": "arn:aws:backup:us-west-2:123456789012:backup-vault:dr-vault",
          "Lifecycle": { "DeleteAfterDays": 35 }
        }
      ]
    }
  ]
}
```

```bash
aws backup create-backup-plan --backup-plan file://prod-daily.json
```

The backup plan protects data; DR still needs the runbook, infrastructure as code for the second region, and DNS failover to use that copy.

## Interview tips

- Say the 3-2-1 rule, then extend it with immutability - it shows current ransomware awareness.
- Volunteer a restore-testing cadence before being asked.
- Note that replication is not backup: it faithfully replicates a deletion or corruption too.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[What is Docker Compose?]] (`#9`): [What is Docker Compose?](../docker/what-is-docker-compose.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
