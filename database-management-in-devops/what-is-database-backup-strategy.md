---
title: "What is Database Backup Strategy?"
id: 114
category: "Database Management in DevOps"
difficulty: "Intermediate"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
---

# What is Database Backup Strategy?

**Short answer:** A database backup strategy combines full backups, continuous transaction-log archiving for point-in-time recovery, off-site immutable copies, and - critically - regularly tested restores, all sized to meet defined RPO and RTO targets.

## Detail

**The layers**

- **Full backups** - a complete copy on a schedule (typically daily or weekly), application-consistent.
- **Incremental / differential** - changed blocks or pages between fulls, shortening the backup window.
- **Continuous log archiving** - PostgreSQL WAL, MySQL binlog, SQL Server transaction log - shipped continuously. This is what enables **point-in-time recovery**: restore the last full backup then replay logs to the second before a bad migration ran.
- **Snapshots** - fast volume-level copies; excellent for rapid recovery, but they live on the same storage system, so they are not a substitute for off-site backups.
- **Logical dumps** (`pg_dump`, `mysqldump`) - portable and good for single-table recovery, but slow for large databases.

**Replication is not backup.** A replica faithfully reproduces a `DROP TABLE`. Delayed replicas (a replica deliberately kept, say, one hour behind) are a useful middle ground for fast recovery from human error.

**Requirements**

- Encryption in transit and at rest, with keys managed separately.
- Storage in a different account/subscription and region, with object lock so backups cannot be deleted before retention expires.
- Monitoring that alerts on the _absence_ of a recent successful backup and on replication lag.
- Retention aligned to legal and business need, with lifecycle transitions to cheaper tiers.

**Testing.** Restore into an isolated environment on a schedule, verify data integrity and row counts, and record the elapsed time - that measurement is your real RTO.

## Example

```bash
# PostgreSQL: base backup plus continuous WAL archiving for PITR
pg_basebackup -D /backup/base -Ft -z -Xs -P

# postgresql.conf
# archive_mode = on
# archive_command = 'aws s3 cp %p s3://acme-db-wal/%f --sse aws:kms'

# Restore to a precise moment
# recovery_target_time = '2026-03-14 09:14:00+00'
```

## Interview tips

- Point-in-time recovery via log archiving is the capability that separates a real strategy from nightly dumps.
- "Replication is not backup" is a line worth saying out loud.
- Close with restore testing and the measured restore time - it is the most credible evidence.

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
