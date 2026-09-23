---
title: "What are RTO and RPO and how do they drive Disaster Recovery architecture tiers?"
id: 596
category: "Backup and Disaster Recovery"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - backup-and-disaster-recovery
  - disaster-recovery
  - rto
  - rpo
  - backup
  - business-continuity
quiz:
  stem: "If an organization has an RPO of 15 minutes and an RTO of 1 hour, what is the impact if a failure occurs at 12:00 PM?"
  options:
    - "The system must be restored by 12:15 PM and can lose up to 1 hour of data"
    - "Service must be restored by 1:00 PM (1 hour RTO) and data loss cannot exceed records created after 11:45 AM (15 min RPO)"
    - "All user passwords must be reset within 15 minutes"
    - "The primary database must take snapshots every 1 hour"
  answer: 2
  explanation: "RTO dictates that the system must be operational within 1 hour (1:00 PM). RPO dictates that data can only be lost back to 11:45 AM (15 minutes prior to the disaster)."
---

# What are RTO and RPO and how do they drive Disaster Recovery architecture tiers?

**Short answer:** RTO (Recovery Time Objective) is the maximum acceptable duration of downtime before service is restored; RPO (Recovery Point Objective) is the maximum acceptable amount of data loss measured in time (e.g. 15 minutes of lost transactions). Together they pick the DR tier: the lower the targets, the more of the standby environment must already be running and replicating, and the more it costs.

## Detail

RTO and RPO are business requirements, not technical choices:

```text
Last Data Backup             Incident Occurs             Service Restored
      │                             │                            │
      └─────────── RPO ─────────────┴─────────── RTO ────────────┘
         (Max Acceptable Data Loss)      (Max Acceptable Downtime)
```

### The Four Standard DR Tiers

| DR Strategy                    | Cost    | RTO             | RPO                                                | Architecture                                                                                      |
| ------------------------------ | ------- | --------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Backup & Restore**           | Low     | Hours to Days   | Hours to Days                                      | Daily snapshots in S3/Glacier; restore infrastructure via Terraform when needed                   |
| **Pilot Light**                | Medium  | Tens of Minutes | Seconds to Minutes                                 | Core database continuously replicates to standby region; compute instances are off until failover |
| **Warm Standby**               | High    | Minutes         | Seconds                                            | Scaled-down version of full stack always running in secondary region; auto-scales up on failover  |
| **Multi-Region Active-Active** | Highest | Near zero       | Near zero (zero only with synchronous replication) | All regions live, handling traffic concurrently with continuous replication                       |

## Example

A tier decision is recorded per system, straight from the business impact analysis. AWS Elastic Disaster Recovery, Aurora Global Database, and Route 53 map onto the tiers like this:

```yaml
# dr-tiers.yaml - reviewed with the business owner each year
- system: payments-api
  rto: 5m
  rpo: 1s
  tier: warm-standby          # Aurora Global Database + scaled-down EKS in us-west-2
  failover: route53-health-check
- system: order-history
  rto: 1h
  rpo: 5m
  tier: pilot-light           # cross-region replica; compute via Terraform on failover
- system: internal-reporting
  rto: 48h
  rpo: 24h
  tier: backup-and-restore    # AWS Backup copy to a second region
```

## Interview tips

- RTO is downtime duration (how fast to recover).
- RPO is data loss duration (how far back data can be lost).
- The four tiers: Backup/Restore, Pilot Light, Warm Standby, Active-Active.
- Higher availability / lower RTO/RPO exponentially increases cloud costs.
- Say the trade-off out loud: RPO zero needs synchronous replication, and synchronous replication across regions adds round-trip latency to every write, which is why most "active-active" designs quietly accept a few seconds of RPO.
- Measured RTO/RPO from DR tests beat the targets on paper - interviewers like hearing that you track the gap.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
