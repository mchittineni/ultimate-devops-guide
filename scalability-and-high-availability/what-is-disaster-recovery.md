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
