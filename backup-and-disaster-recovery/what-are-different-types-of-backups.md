---
title: "What are different types of backups?"
id: 62
category: "Backup and Disaster Recovery"
difficulty: "Beginner"
tags:
  - devops
  - backup-and-disaster-recovery
  - interview-questions
---

# What are different types of backups?

**Short answer:** Full (everything, every time), incremental (changes since the last backup of any type), differential (changes since the last full backup), plus snapshots, continuous data protection, and synthetic fulls.

## Detail

| Type             | What it copies                         | Backup time            | Storage    | Restore complexity              |
| ---------------- | -------------------------------------- | ---------------------- | ---------- | ------------------------------- |
| Full             | All data                               | Longest                | Largest    | Simplest - one set              |
| Incremental      | Changes since last backup of any type  | Shortest               | Smallest   | Full + every increment in order |
| Differential     | Changes since last full                | Medium                 | Medium     | Full + one differential         |
| Synthetic full   | Server-side merge of full + increments | Short (no client load) | Full-sized | Simple                          |
| Snapshot         | Point-in-time block/volume state       | Near instant           | Delta only | Very fast, same storage system  |
| Continuous (CDP) | Every write, journalled                | Continuous             | High       | Restore to any second           |

**A typical schedule:** a weekly full, daily incrementals, monthly fulls retained for a year. This balances backup window, storage cost, and restore complexity.

**Important qualifiers**

- **Application-consistent vs crash-consistent.** A snapshot taken while a database is mid-write is crash-consistent - it may need recovery on restore. Application-consistent backups quiesce the application or use its native tooling (`pg_dump`, `mysqldump`, log shipping).
- **Snapshots are not backups** when they live on the same storage system as the data. Losing the volume loses both. Copy them to an independent location.
- **Point-in-time recovery** from continuous log archiving (WAL, binlog) is what lets you restore to the moment before a bad migration.
- **Restore chain risk**: one corrupt incremental invalidates everything after it - which is why increments are verified, not assumed.

## Interview tips

- The incremental-versus-differential trade-off (backup speed vs restore speed) is the classic exam question.
- Application-consistent backups for databases is the detail that shows production experience.
- Always close with verification: checksums, test restores, and monitoring of backup job outcomes.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
