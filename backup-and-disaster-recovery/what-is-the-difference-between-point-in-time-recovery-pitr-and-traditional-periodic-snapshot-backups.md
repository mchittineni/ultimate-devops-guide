---
title: "What is the difference between Point-in-Time Recovery (PITR) and traditional periodic snapshot backups?"
id: 598
category: "Backup and Disaster Recovery"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - backup-and-disaster-recovery
  - backup
  - pitr
  - wal
  - databases
  - rds
quiz:
  stem: "How does Point-in-Time Recovery (PITR) achieve restoration to an exact second before a data corruption incident occurred?"
  options:
    - "By taking a full multi-terabyte disk snapshot every single second"
    - "By restoring the latest base snapshot and replaying continuous Write-Ahead Logs (WAL) up to the target timestamp"
    - "By reversing the system clock on the database operating system"
    - "By querying the Git commit history of the database application"
  answer: 2
  explanation: "PITR restores the closest preceding base snapshot and rolls forward by replaying transaction logs (WAL) entry by entry until reaching the exact millisecond requested."
---

# What is the difference between Point-in-Time Recovery (PITR) and traditional periodic snapshot backups?

**Short answer:** Periodic snapshots take point-in-time disk freezes every N hours, leaving an RPO gap equal to the snapshot frequency; PITR continuously archives write-ahead transaction logs (WAL/binlog) alongside base snapshots, allowing restoration to any exact second in time.

## Detail

Consider what happens when a developer runs `DROP TABLE users;` at 14:23:15:

### Periodic Snapshots (e.g. Midnight Daily)

- You restore the snapshot taken at 00:00.
- You have lost **14 hours and 23 minutes of customer transactions and payments** (RPO = 14 hours).

### Point-in-Time Recovery (PITR)

- PITR combines two streams:
  1. Regular base storage snapshots.
  2. Continuous streaming of transaction logs (Write-Ahead Logs in PostgreSQL, Binary Logs in MySQL, Redo Logs in Oracle) to durable cloud object storage (S3) every few seconds.
- **Restoration**:
  - The database restores the most recent base snapshot prior to the incident (e.g., 14:00).
  - It replays the continuous WAL stream sequentially up to **14:23:14** (one second before the accidental `DROP TABLE` command!).
  - Nothing written before the mistake is lost. Writes made _after_ 14:23:15 are not in the restored copy, so the usual pattern is to restore PITR into a **new** instance and copy the dropped table back into production, rather than rewinding the whole database.

**Limits.** Your RPO is bounded by how often logs are shipped (RDS uploads transaction logs roughly every five minutes, so its latest restorable time trails now by a few minutes), and restore time grows with the amount of log to replay since the last base backup - which is why base backups are still taken regularly.

## Example

PostgreSQL 12+ recovery to one second before the mistake, from a base backup plus archived WAL:

```bash
# Restore the base backup (pg_basebackup or a tool such as pgBackRest) into the data dir, then:
cat >> "$PGDATA/postgresql.auto.conf" <<'EOF'
restore_command = 'cp /mnt/wal-archive/%f %p'
recovery_target_time = '2026-09-23 14:23:14+00'
recovery_target_action = 'promote'
EOF
touch "$PGDATA/recovery.signal"   # recovery.conf was removed in PostgreSQL 12
pg_ctl -D "$PGDATA" start
```

On RDS the same operation is one call that always creates a new instance:

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier prod-db \
  --target-db-instance-identifier prod-db-pitr-1423 \
  --restore-time 2026-09-23T14:23:14Z
```

## Interview tips

- Snapshots leave RPO gaps between backup schedules.
- PITR combines base backups with continuous Write-Ahead Log (WAL/binlog) streaming.
- Ability to replay transactions up to the exact second before an accidental DROP TABLE.
- Minimizing RPO from hours down to seconds.
- Point out that PITR does not protect against losing the log archive itself - keep it in a separate, immutable location like any other backup.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
