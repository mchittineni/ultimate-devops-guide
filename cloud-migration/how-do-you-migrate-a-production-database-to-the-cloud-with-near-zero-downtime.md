---
title: "How do you migrate a production database to the cloud with near-zero downtime?"
id: 279
category: "Cloud Migration"
difficulty: "Advanced"
tags:
  - devops
  - cloud-migration
  - interview-questions
---

# How do you migrate a production database to the cloud with near-zero downtime?

**Short answer:** Replicate, do not copy. Take a consistent snapshot, load it into the target, then stream change data capture (CDC) until replication lag is near zero, verify row counts and checksums, and cut over inside a short write freeze - typically seconds to a couple of minutes - by flipping a DNS or connection-string indirection. Keep reverse replication running so rollback is a decision, not a rebuild.

## Detail

**Decide the shape of the move first.** A **homogeneous** migration (PostgreSQL to RDS PostgreSQL) can use native logical replication and is mostly an operations problem. A **heterogeneous** one (Oracle to PostgreSQL) is a schema and application-rewrite project wearing a migration costume: stored procedures, sequences, data types, collation, and SQL dialect all change, and the tooling (AWS SCT, ora2pg) converts perhaps 80% automatically. Never quote a near-zero-downtime figure for a heterogeneous move without a full functional test cycle behind it.

**The pipeline, in order:**

1. **Baseline and budget.** Measure current size, write rate, peak QPS, and largest table. State the RTO and RPO you are being held to, and the maximum acceptable write freeze. These numbers drive every later choice.
2. **Prepare the target.** Same major version to start (upgrade later, separately), matching parameter groups, storage type sized for the _restore_ throughput, and the network path (VPN/Direct Connect/Interconnect) tested for sustained bandwidth - not ping.
3. **Schema first, then constraints.** Create tables and primary keys; **drop or disable secondary indexes, foreign keys, and triggers for the bulk load**, then rebuild them afterwards. This is often the difference between a 4-hour and a 30-hour load.
4. **Snapshot load.** `pg_dump`/`pg_basebackup`, `mydumper`, or the provider's service (DMS, Azure DMS, Database Migration Service). The dump and the CDC start position must describe the same instant - take the dump from the slot's exported snapshot (`pg_dump --snapshot=`, `mydumper` with the recorded GTID/binlog position), or let migration tooling coordinate the two for you. Any gap between them is silent data loss or duplicates.
5. **CDC catch-up.** Start replication from that position and watch lag fall. Tables without a primary key will break most CDC tools; find them before you start (`pg_class`/`information_schema` query), not during.
6. **Verify.** Row counts per table, checksums on a sampled or full basis (`pt-table-checksum`, or a hashed-aggregate query per table), sequence and identity high-water marks, and a read-only application test suite pointed at the target. Verification is the step teams skip and then regret.
7. **Cut over.** Stop writes at the application edge (feature flag, or set the app to read-only), wait for lag to hit zero, promote the target, repoint the connection string, re-enable writes. Cut over via a **DNS CNAME or a proxy** (RDS Proxy, PgBouncer, ProxySQL) that you already use in production - not by editing config in twelve services.
8. **Reverse replication.** Configure the new primary to replicate back to the old one for the first hours or days. Rollback then costs a repoint rather than a restore, and that safety net is what lets you cut over on a Tuesday instead of a bank holiday weekend.

**What actually goes wrong.** Long-running transactions on the source hold up logical replication slots and can fill the source's disk with WAL - monitor slot lag and have a disk alarm. Sequences do not replicate; forgetting to advance them means duplicate-key errors minutes after cutover. Collation differences change index ordering and can break unique constraints and query results. Connection limits on the target are usually far lower than the source's - add a pooler before cutover, not after the thundering herd. And write-freeze durations balloon when the freeze is implemented by "asking teams to stop deploying" rather than by a mechanism.

## Example

```sql
-- Source (PostgreSQL): publication, then a slot that EXPORTS the snapshot the dump must use.
-- The dump and the CDC start position have to describe the same instant, or the rows written
-- during the dump are either duplicated or lost. The SQL function
-- pg_create_logical_replication_slot() does not export a usable snapshot - create the slot on
-- a replication connection instead, which returns a snapshot name, and keep that connection
-- open until the dump finishes.
CREATE PUBLICATION migrate_pub FOR ALL TABLES;

--   psql "host=onprem-db dbname=app replication=database"
--   CREATE_REPLICATION_SLOT migrate_slot LOGICAL pgoutput;
--     -> slot_name | consistent_point (LSN) | snapshot_name  e.g. 00000003-00000002-1
-- Then, in a second session, dump at exactly that snapshot:
--   pg_dump --snapshot=00000003-00000002-1 -Fd -j8 -f /dump host=onprem-db dbname=app

-- Tables with no primary key will silently break CDC. Find them first.
SELECT c.relname FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE c.relkind = 'r' AND n.nspname = 'public'
   AND NOT EXISTS (SELECT 1 FROM pg_index i WHERE i.indrelid = c.oid AND i.indisprimary);
```

```sql
-- Target: restore the exported-snapshot dump FIRST, then attach CDC at the slot's
-- consistent_point. copy_data = false is only safe because the dump came from that exact
-- snapshot; the slot has been buffering every change since, so nothing at the boundary is
-- duplicated or missed.
CREATE SUBSCRIPTION migrate_sub
  CONNECTION 'host=onprem-db dbname=app user=repl'
  PUBLICATION migrate_pub
  WITH (copy_data = false, create_slot = false, slot_name = 'migrate_slot');

-- If you would rather not hand-coordinate the two positions: let PostgreSQL do it with
-- copy_data = true (it takes its own snapshot per table), or use tooling that coordinates
-- snapshot and CDC position for you - AWS DMS full-load-plus-CDC, or Debezium's initial
-- snapshot mode. Hand-coordination is only worth it for a parallel dump of a large database.

-- Cutover gate: this must be ~0 before you unfreeze writes.
SELECT slot_name, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS lag
  FROM pg_replication_slots;

-- Post-cutover, every single time: sequences do not replicate.
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders) + 1);
```

```bash
# Verify before you trust: per-table row counts and a content checksum.
for t in orders customers payments; do
  echo -n "$t "
  psql -Atc "SELECT count(*), md5(string_agg(t::text, '' ORDER BY id)) FROM $t t" -h source
  psql -Atc "SELECT count(*), md5(string_agg(t::text, '' ORDER BY id)) FROM $t t" -h target
done
```

## Interview tips

- Structure the answer as snapshot → CDC → verify → freeze → cut over → reverse-replicate. The reverse replication is the detail that marks experience.
- Separate homogeneous from heterogeneous in your first two sentences, and refuse to promise near-zero downtime for a dialect change without a test cycle.
- Say that CDC must start at the exact snapshot position (LSN/GTID/binlog). It is the mechanism behind "no data loss" and interviewers probe for it.
- Volunteer the index/FK/trigger drop-and-rebuild trick for bulk load - it is a concrete, hard-won detail.
- Name at least three real failure modes: replication slot filling the source disk, un-advanced sequences, missing primary keys, collation-driven index differences, target connection limits.
- Insist on a mechanism for the write freeze (flag or read-only mode) rather than a process. "We asked people not to write" is not an answer at this level.

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
