---
title: "What is RPO and RTO?"
id: 63
category: "Backup and Disaster Recovery"
difficulty: "Beginner"
tags:
  - devops
  - backup-and-disaster-recovery
  - interview-questions
---

# 63. What is RPO and RTO?

**Short answer:** RPO (Recovery Point Objective) is the maximum acceptable amount of data loss measured in time; RTO (Recovery Time Objective) is the maximum acceptable time to restore service. RPO drives backup and replication design; RTO drives recovery architecture.

## Detail

Picture an outage on a timeline:

```text
   ← RPO →                    ← RTO →
[last good copy] ......... [FAILURE] ......... [service restored]
   data lost in this window        time customers are down
```

**RPO** answers "how much data can we afford to lose?" An RPO of one hour permits hourly backups. An RPO of zero requires synchronous replication — and synchronous replication costs write latency, which is a real product trade-off.

**RTO** answers "how long can we be down?" An RTO of 24 hours allows restore-from-backup. An RTO of five minutes requires a warm standby or active-active deployment.

**How they are set.** Not by engineers guessing — by business impact analysis. Quantify cost per hour of downtime and cost per unit of lost data (revenue, regulatory exposure, reputational harm), then compare with the cost of each DR strategy. Different systems in the same company legitimately get different targets: a payments ledger might be RPO 0 / RTO 5 min, while an internal reporting tool is RPO 24h / RTO 48h.

**Related terms:** MTD (maximum tolerable downtime, of which RTO is a component), and the actual measured RPA/RTA — what you achieved in the last test versus what you promised.

## Example

| Tier | System       | RPO   | RTO    | Implementation                           |
| ---- | ------------ | ----- | ------ | ---------------------------------------- |
| 1    | Payments     | 0     | 5 min  | Synchronous multi-AZ, automatic failover |
| 2    | Customer app | 5 min | 30 min | Async replication, warm standby          |
| 3    | Reporting    | 24 h  | 24 h   | Nightly backups, restore on demand       |

## Interview tips

- Emphasise that these are _business_ decisions costed by engineering, not aspirations.
- Note the synchronous-replication latency cost — it shows you understand the trade-off, not just the term.
- Mention measuring actual achieved values during DR tests, and reporting the gap.

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
