---
title: "What is Disaster Recovery?"
id: 60
category: "Scalability and High Availability"
difficulty: "Intermediate"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
---

# What is Disaster Recovery?

**Short answer:** Disaster recovery is the set of plans, capabilities, and procedures for restoring service after a major failure - a region outage, data corruption, or ransomware - measured by how much data you can lose (RPO) and how long recovery may take (RTO).

## Detail

**RPO (Recovery Point Objective)** - maximum acceptable data loss, expressed as time. RPO of 15 minutes means backups or replication must be no more than 15 minutes behind.

**RTO (Recovery Time Objective)** - maximum acceptable time to restore service.

**The four standard strategies**, from cheapest to fastest:

| Strategy                 | RPO / RTO                 | Cost    | How it works                                                            |
| ------------------------ | ------------------------- | ------- | ----------------------------------------------------------------------- |
| Backup & restore         | Hours / hours–days        | Lowest  | Restore from backups into rebuilt infrastructure                        |
| Pilot light              | Minutes / tens of minutes | Low     | Core data replicated; minimal always-on footprint scaled up on failover |
| Warm standby             | Minutes / minutes         | Medium  | A scaled-down but fully functional copy running continuously            |
| Multi-site active-active | Near zero / near zero     | Highest | All regions serve traffic; failure removes one from rotation            |

**What a real DR capability requires**

- Infrastructure as code, so the environment can be rebuilt deterministically.
- Data replication (cross-region snapshots, database read replicas, object-store replication) with monitored lag.
- Backups stored immutably in a separate account or subscription, so a compromised production identity cannot delete them.
- DNS/traffic-management failover with health checks.
- A documented, versioned runbook naming decision-makers and communication channels.
- **Regular, rehearsed testing** - a game day or full failover exercise. An untested DR plan should be assumed not to work.

**Trade-off.** Every step up the table buys a lower RPO/RTO with standing cost and operational complexity - an active-active estate roughly doubles infrastructure and makes data consistency a design problem. And replication is not a backup: corruption, a bad migration, or ransomware replicates to the standby within seconds, so you need point-in-time, immutable copies as well.

## Example

```hcl
# Ransomware-resistant backups: a copy into a separate account's vault with Vault Lock.
resource "aws_backup_plan" "prod" {
  name = "prod-daily"
  rule {
    rule_name         = "daily"
    target_vault_name = aws_backup_vault.local.name
    schedule          = "cron(0 3 * * ? *)"
    lifecycle { delete_after = 35 }

    copy_action { # cross-account, cross-region copy
      destination_vault_arn = "arn:aws:backup:eu-west-1:222222222222:backup-vault:dr-vault"
      lifecycle { delete_after = 35 }
    }
  }
}

# In the DR account: compliance-mode lock - nobody, including root, can delete early.
resource "aws_backup_vault_lock_configuration" "dr" {
  backup_vault_name   = aws_backup_vault.dr.name
  min_retention_days  = 30
  max_retention_days  = 365
  changeable_for_days = 3 # grace period, after which the lock is immutable
}
```

## Interview tips

- Derive RPO/RTO from business impact, then pick the strategy - never the other way round.
- Immutable, separately-owned backups are the ransomware answer, and interviewers listen for it.
- The strongest closing point: "we test failover quarterly, and here is what we learned last time."

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[How do you take a monthly release process to daily deployments?]] (`#285`): [How do you take a monthly release process to daily deployments?](../core-devops-concepts/how-do-you-take-a-monthly-release-process-to-daily-deployments.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
