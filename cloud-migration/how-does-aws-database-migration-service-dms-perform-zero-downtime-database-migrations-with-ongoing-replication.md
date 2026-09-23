---
title: "How does AWS Database Migration Service (DMS) perform zero-downtime database migrations with ongoing replication?"
id: 694
category: "Cloud Migration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cloud-migration
  - dms
  - databases
  - replication
  - cdc
quiz:
  stem: "How does AWS DMS allow a 10TB database to be migrated to the cloud with only a two-minute cutover window?"
  options:
    - "It compresses the 10TB database into a 1MB zip file"
    - "It performs an initial bulk load while the source is online, then continuously replicates transactions via Change Data Capture (CDC) until cutover"
    - "It shuts down the on-premise database for two days"
    - "It transfers database memory directly over satellite links"
  answer: 2
  explanation: "DMS copies existing data while production continues operating, then streams ongoing transaction logs (CDC) to keep the target in sync. Cutover requires only a brief DNS switch."
---

# How does AWS Database Migration Service (DMS) perform zero-downtime database migrations with ongoing replication?

**Short answer:** AWS DMS provisions a replication instance that extracts a baseline data dump from the source database, loads it into the target, and continuously captures ongoing changes via transaction logs (CDC) until cutover, achieving near-zero downtime.

## Detail

A multi-terabyte production database cannot be copied inside a short maintenance window: at a sustained 1 Gbps, 5 TB takes more than 11 hours before any verification. DMS avoids the window by copying while the source stays live and then keeping the target in sync.

### The full load + CDC workflow

```text
[Source: Oracle / SQL Server / PostgreSQL / MySQL]
     │  full load (bulk SELECTs)             ┌───────────────────────┐
     ├──────────────────────────────────────>│ DMS replication       │──> [Target: Aurora / RDS]
     │  CDC (redo logs, WAL via logical      │ instance or DMS       │
     └──── replication, binlog, MS-CDC) ────>│ Serverless            │
                                             └───────────────────────┘
```

1. **Full load**: DMS reads each table in bulk and writes it to the target, several tables in parallel. The source stays online and keeps taking writes.
2. **Change capture from the start**: when the task starts, DMS records the source's log position and begins capturing changes from the transaction log - Oracle redo (LogMiner or Binary Reader), PostgreSQL WAL through a logical replication slot, MySQL binlog in `ROW` format, SQL Server MS-CDC or MS-Replication. Changes made to a table while it loads are cached and applied after that table's load completes.
3. **Catch-up**: DMS applies the change stream until `CDCLatencySource`/`CDCLatencyTarget` fall to seconds.
4. **Cutover**: stop application writes, wait for latency to reach zero, validate, then repoint the application (a DNS name or proxy). Downtime is the freeze, typically minutes.

**Supporting pieces.** For heterogeneous moves (Oracle or SQL Server to PostgreSQL), **DMS Schema Conversion** - the managed successor to the desktop AWS Schema Conversion Tool - converts schemas and code objects and reports what needs manual work. **Data validation** tasks compare rows between source and target. **DMS Serverless** removes instance sizing by scaling capacity automatically. For same-engine moves, native tools (PostgreSQL logical replication, MySQL replication, Aurora read-replica promotion, `pg_dump`/restore plus replication) are often simpler and faster than DMS.

### What goes wrong

- **Prerequisites on the source**: supplemental logging on Oracle, `wal_level = logical` on PostgreSQL, `binlog_format = ROW` and sufficient binlog retention on MySQL. Missing retention means CDC cannot resume after an interruption.
- **Tables without a primary key** cannot be updated reliably by CDC; find them first.
- **DMS migrates data, not everything around it**: secondary indexes, foreign keys, triggers, sequences, users, and stored procedures need their own plan (create secondary indexes after the full load for speed, disable triggers on the target, reset sequences at cutover).
- **LOBs** are slow; tune LOB mode (limited versus full) per table.
- **Replication slot and log growth** on the source while the task is stopped or lagging can fill the source disk.

So "zero downtime" really means a short, planned write freeze plus a verified sync - and it depends on the testing, not on the service.

## Example

```bash
# Full load + ongoing replication, with validation enabled.
aws dms create-replication-task \
  --replication-task-identifier orders-to-aurora \
  --source-endpoint-arn "$SRC_ARN" --target-endpoint-arn "$TGT_ARN" \
  --replication-instance-arn "$RI_ARN" \
  --migration-type full-load-and-cdc \
  --table-mappings file://table-mappings.json \
  --replication-task-settings '{"ValidationSettings":{"EnableValidation":true},
     "FullLoadSettings":{"TargetTablePrepMode":"DO_NOTHING"}}'

aws dms start-replication-task --replication-task-arn "$TASK_ARN" \
  --start-replication-task-type start-replication

# Cutover gate: CDC latency near zero and validation clean before you repoint the app.
aws cloudwatch get-metric-statistics --namespace AWS/DMS --metric-name CDCLatencyTarget \
  --dimensions Name=ReplicationInstanceIdentifier,Value=dms-prod Name=ReplicationTaskIdentifier,Value=orders-to-aurora \
  --statistics Maximum --period 60 \
  --start-time "$(date -u -d '15 minutes ago' +%FT%TZ)" --end-time "$(date -u +%FT%TZ)"  # GNU date
aws dms describe-table-statistics --replication-task-arn "$TASK_ARN" \
  --query 'TableStatistics[?ValidationState!=`Validated`].[TableName,ValidationState]'
```

## Interview tips

- Explain the mechanism: full load while the source is live, change capture from the log position recorded at start, then catch-up.
- Name the log source per engine (redo, WAL/logical slot, binlog, MS-CDC) and the prerequisites that go with it.
- Say what DMS does not migrate - secondary indexes, sequences, users, code objects - and mention DMS Schema Conversion for heterogeneous moves.
- Describe the cutover as a short, controlled write freeze gated on CDC latency and validation, not as "zero downtime" by magic.
- Mention that native replication is often the better tool for homogeneous migrations.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
