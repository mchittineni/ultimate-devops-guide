---
title: "What does a DevOps engineer need to know about databases?"
id: 286
category: "Database Management in DevOps"
difficulty: "Beginner"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
---

# What does a DevOps engineer need to know about databases?

**Short answer:** Enough to keep one alive and deployable, not enough to be a DBA. Concretely: how to run **schema migrations safely through a pipeline**, how **backups and restores** actually work (and that an untested backup is not a backup), what **replication and failover** give you, where the **connection limits and pooling** boundaries are, and which handful of metrics tell you a database is in trouble before users do.

## Detail

**The database is the stateful thing in an otherwise stateless world.** You can replace an application container freely; you cannot replace a database. Every deployment practice that assumes disposability - rolling updates, instant rollback, blue/green - needs adapting when a schema is involved. This is the whole reason databases get their own DevOps discipline.

**Migrations, because this is where you will actually be involved.** Schema changes belong in version control next to the application, applied by a migration tool (Flyway, Liquibase, Alembic, Prisma Migrate, `golang-migrate`) as a pipeline step, never by hand in a client. Two rules carry most of the weight:

- **Every migration must be backward compatible with the currently running application version.** During a rolling deploy, old and new code run at the same time against one schema. A migration that drops a column the old version still reads takes production down mid-deploy.
- **Additive first, destructive later.** Add a column, deploy code that writes both, backfill, switch reads, then drop the old column in a later release. Each step is separately revertible.

**Backups and restores.** Know the difference between a full backup, an incremental one, and **point-in-time recovery** (continuous log/WAL archiving, which lets you restore to a specific second - the thing that saves you from a bad `DELETE`). Know your **RPO** (how much data you can lose) and **RTO** (how long recovery may take), and know that the restore has to be rehearsed on a schedule. A managed snapshot you have never restored is a hope, not a plan.

**Replication and high availability.** A **read replica** offloads reads and is asynchronously behind the primary - it is not a backup, and reading your own write from a replica returns stale data. A **standby / Multi-AZ** setup exists for failover, usually synchronous, and costs latency. Failover changes the primary's identity, so applications must reconnect through a name (DNS, a proxy, or a service) rather than a hardcoded IP.

**Connections.** Databases have a hard connection limit and each connection costs memory. Containers multiply the problem: 20 replicas × a pool of 20 = 400 connections from one service. Use a pooler (PgBouncer, RDS Proxy, ProxySQL) and set pool sizes deliberately. "Too many connections" during an autoscaling event is one of the most common self-inflicted outages.

**The metrics worth alerting on:** replication lag, connection count against the limit, disk space and IOPS credit, slow-query count or p95 query latency, deadlocks, and long-running transactions (which block cleanup and can fill the disk with old row versions). Cache hit ratio and lock waits are the next tier.

**What is not your job.** Query plan optimisation, index design, and data modelling belong with developers and DBAs. Your job is to make their changes safe, repeatable, observable, and recoverable.

## Example

```sql
-- A backward-compatible migration set. Run these as three separate releases.
-- V1: additive only. Old code ignores the column; new code writes it.
ALTER TABLE orders ADD COLUMN currency text DEFAULT 'USD' NOT NULL;

-- V2: index without locking the table (PostgreSQL). Never CREATE INDEX plainly in prod.
CREATE INDEX CONCURRENTLY idx_orders_currency ON orders (currency);

-- V3: only once no running version reads the old column.
ALTER TABLE orders DROP COLUMN legacy_currency_code;
```

```yaml
# Migrations as a pipeline step, before the app rollout - and gated.
- name: Run database migrations
  run: flyway -url=$DB_URL -user=$DB_USER migrate
  # Prerequisites, not optional:
  #  - migrations are versioned files in Git, reviewed like code
  #  - the same command ran in staging against production-shaped data
  #  - a tested rollback plan exists (a down migration, or restore-to-PITR)
```

```bash
# The health questions, in the order you ask them during an incident.
psql -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"        # connections
psql -c "SELECT now() - pg_last_xact_replay_timestamp() AS replica_lag;"      # replica lag
psql -c "SELECT pid, now()-xact_start AS age, query FROM pg_stat_activity
          WHERE state <> 'idle' ORDER BY age DESC LIMIT 5;"                   # long transactions
df -h /var/lib/postgresql                                                     # disk

# And the one you should be able to run from memory:
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier prod \
  --target-db-instance-identifier prod-restore-test \
  --restore-time 2026-08-07T09:15:00Z     # rehearse this monthly
```

## Interview tips

- Draw the boundary early: you make database changes safe and recoverable; you are not the query optimiser. It shows you know your lane.
- The backward-compatibility rule for migrations during a rolling deploy is the single most valuable thing to say. Give the add-backfill-switch-drop sequence.
- Say plainly that a read replica is not a backup, and that an untested restore is not a backup. Both are common interview checkpoints.
- Know RPO and RTO as terms and be able to give a real example ("15 minutes of data loss acceptable, 1 hour to recover").
- Mention connection pooling and the replicas × pool-size arithmetic. It is a real outage cause that few candidates volunteer.
- Have five database metrics ready. Replication lag and long-running transactions are the two that signal genuine hands-on time.

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
