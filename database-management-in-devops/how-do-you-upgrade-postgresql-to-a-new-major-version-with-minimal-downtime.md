---
title: "How do you upgrade PostgreSQL to a new major version with minimal downtime?"
id: 782
category: "Database Management in DevOps"
difficulty: "Advanced"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - backup-and-disaster-recovery
---

# How do you upgrade PostgreSQL to a new major version with minimal downtime?

**Short answer:** Pick the method by how much downtime you can afford. **`pg_upgrade`** rewrites the system catalogs in place and, with `--link` (or `--clone`, or `--swap` from PostgreSQL 18), reuses the existing data files, so even a multi-terabyte database is down for minutes rather than hours - but it is still an outage, and with `--link` the old cluster cannot be started again once the new one has run. **Logical replication** gives near-zero downtime: build a new cluster on the target version, replicate into it with a publication and subscription, let it catch up, then switch the application over in seconds - at the cost of real caveats (DDL, sequences, and large objects are not replicated, and every table needs a primary key or replica identity). On managed services the same two options appear as an in-place major version upgrade and a **blue/green deployment** (RDS and Aurora implement theirs with logical replication). Whatever the method: rehearse on a restored copy of production, check extension compatibility, take a backup you have restored, and run `ANALYZE` afterwards so the planner is not working blind.

## Detail

### Why major upgrades are different

Minor releases (17.5 → 17.6) are binary-compatible bug and security fixes: install the new binaries and restart. A **major** release (17 → 18) changes the on-disk catalog format, so the data directory cannot simply be opened by the new server - you either convert it (`pg_upgrade`) or move the data (dump/restore or logical replication). Community support lasts five years per major version, and fleets fall behind quietly: PostgreSQL 13 reached end of life in November 2025 and 14 does in November 2026, and on managed services an unsupported version moves to paid extended support or is upgraded for you on the provider's schedule.

### The three methods

| Method                          | Downtime                     | Rollback                                                      | Watch out for                                                                  |
| ------------------------------- | ---------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `pg_dump` / `pg_restore`        | Hours for large databases    | Old cluster untouched                                         | Only practical for small databases                                             |
| `pg_upgrade --link` / `--clone` | Minutes, independent of size | `--link`: none once the new cluster starts - restore a backup | Extensions must exist for the new version; replicas must be rebuilt or rsynced |
| Logical replication cutover     | Seconds (the switchover)     | Keep the old primary and reverse-replicate                    | No DDL, sequences, or large objects replicated; PK required                    |

### `pg_upgrade`, done properly

1. Install the new major version's binaries **and every extension** you use (PostGIS, `pg_stat_statements`, TimescaleDB) built for it - an extension that has no build for the target version blocks the upgrade.
2. Run `pg_upgrade --check` against the live cluster. It reports incompatibilities (removed data types, `reg*` columns, unsupported extensions) without changing anything.
3. Stop the application and both clusters, then run the real upgrade. `--link` hard-links data files (seconds, but couples old and new); `--clone` uses reflinks on filesystems that support them (as fast, and the old cluster survives); `--swap` (PostgreSQL 18) moves the files and is often fastest. Copy mode, the default, is safe but proportional to data size.
4. Start the new cluster, re-apply configuration differences (`postgresql.conf`, `pg_hba.conf` are not migrated), and run `vacuumdb --all --analyze-in-stages`. PostgreSQL 18's `pg_upgrade` carries most optimizer statistics across (so `vacuumdb --all --analyze-in-stages --missing-stats-only` fills only the gaps); on older targets the planner has no statistics until you analyze, and the first hour of traffic will show it.
5. Rebuild physical replicas (`pg_basebackup`) or use the documented `rsync` procedure for standbys. Logical replication slots are preserved by `pg_upgrade` from PostgreSQL 17 onwards; before that, CDC consumers such as Debezium need a new slot and a re-snapshot.

### Logical replication cutover

1. Create the new cluster on the target version and load the **schema only** (`pg_dump --schema-only`), because logical replication carries rows, not DDL.
2. `CREATE PUBLICATION` on the old primary, `CREATE SUBSCRIPTION` on the new one. The initial table sync copies existing data, then changes stream continuously.
3. Freeze schema changes for the duration - a migration applied to only one side breaks replication.
4. Verify: row counts, checksums on critical tables, replication lag near zero, and the application's read paths tested against the new cluster.
5. Cut over: stop writes (or put the app in read-only mode), wait for lag to reach zero, **copy sequence values** (they are not replicated: `setval` each sequence a safe margin ahead), switch the connection endpoint (DNS, PgBouncer, or a proxy), and re-enable writes.
6. For rollback, set up reverse replication from new to old before re-enabling writes, and keep it for an agreed period.

Requirements to state: every replicated table needs a primary key or `REPLICA IDENTITY`, large objects are not replicated, and the initial sync on very large tables takes time and extra I/O on the source. Tools such as `pgcopydb`, and managed features like RDS/Aurora blue/green deployments or Google Database Migration Service, automate most of these steps.

### What else breaks after an upgrade

- **Query plans** change between versions; compare the top `pg_stat_statements` entries before and after on a rehearsal copy.
- **Removed or renamed settings and functions** - read the release notes' "Migration to version N" section for every major you skip.
- **Client drivers and connection poolers** may need upgrading for new authentication defaults (SCRAM rather than MD5, which PostgreSQL 18 deprecates).
- **Collation changes**: if the OS glibc or ICU version changes as part of the move, text indexes can silently become corrupt - check `pg_collation_actual_version()` and `REINDEX` affected indexes.

### The same question for MySQL

MySQL supports in-place upgrades between adjacent LTS releases and rolling replica-first upgrades; the near-zero-downtime path is again replication to a new-version replica and a promotion. MySQL 8.0 reached end of life in April 2026, which made 8.0 → 8.4 LTS the common upgrade of the year - use MySQL Shell's `util.checkForServerUpgrade()` first.

## Example

```bash
# Rehearse first: compatibility check against the live cluster, nothing is changed
/usr/lib/postgresql/18/bin/pg_upgrade --check \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main

# The upgrade itself (both clusters stopped), reusing data files
/usr/lib/postgresql/18/bin/pg_upgrade --link --jobs "$(nproc)" \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main

# Then: start 18, restore config, and give the planner statistics quickly
vacuumdb --all --analyze-in-stages --missing-stats-only --jobs 4   # PG 18; omit the flag on older targets
```

```sql
-- Logical replication cutover, old (v17) -> new (v18)
-- On the old primary (wal_level = logical):
CREATE PUBLICATION upgrade_pub FOR ALL TABLES;

-- On the new cluster, after loading the schema only:
CREATE SUBSCRIPTION upgrade_sub
  CONNECTION 'host=old-primary dbname=app user=replicator'
  PUBLICATION upgrade_pub;

-- Watch the catch-up (on the old primary)
SELECT slot_name, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS lag
FROM pg_replication_slots;

-- At cutover, with writes stopped: sequences are NOT replicated, so carry them over
SELECT format('SELECT setval(%L, %s);', schemaname || '.' || sequencename, coalesce(last_value, 1) + 1000)
FROM pg_sequences;   -- run the generated statements on the new cluster
```

```bash
# Managed equivalent: RDS blue/green with a major-version green environment
aws rds create-blue-green-deployment \
  --blue-green-deployment-name app-pg18 \
  --source arn:aws:rds:eu-west-1:111122223333:db:app-prod \
  --target-engine-version 18.1 \
  --target-db-parameter-group-name app-pg18-params
# ... validate the green environment, then:
aws rds switchover-blue-green-deployment --blue-green-deployment-identifier bgd-abc123 \
  --switchover-timeout 300
```

## Interview tips

- Start by separating minor upgrades (restart onto new binaries) from major upgrades (catalog format changes), then choose a method by the downtime budget.
- Explain why `pg_upgrade --link` is fast - it rewrites catalogs and links existing data files - and the trade-off that the old cluster is unusable once the new one has started.
- For near-zero downtime, describe the logical replication cutover and volunteer its caveats: schema-only load first, DDL freeze, sequences copied at cutover, primary keys required.
- Mention the steps people forget: extension builds for the new version, `pg_upgrade --check`, `ANALYZE` afterwards, rebuilding replicas, and CDC replication slots.
- Name the managed path - RDS/Aurora blue/green deployments - and say you would still rehearse on a restored snapshot and time it. See [what is database backup strategy](./what-is-database-backup-strategy.md), [CDC with Debezium](./what-is-change-data-capture-cdc-and-how-does-debezium-stream-database-changes-into-event-architectures.md), and [zero-downtime migration with dual writes and shadow reads](../advanced-devops-cloud/what-is-zero-downtime-database-migration-using-dual-writing-and-shadow-reads.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
