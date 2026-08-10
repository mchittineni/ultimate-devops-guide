---
title: "How do you change a production database schema without downtime?"
id: 418
category: "Database Management in DevOps"
difficulty: "Advanced"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - cicd
  - devops-tools-and-automation
  - incident-management
---

# How do you change a production database schema without downtime?

**Short answer:** Use **expand/contract** (also called parallel change) so the schema is always compatible with the version of the code either side of a deploy: **expand** - add the new nullable column, table, or index in a backward-compatible migration; **migrate** - deploy code that writes both old and new, then backfill existing rows in batches; **contract** - only after the new code is fully rolled out and proven, stop writing the old field and drop it in a later release. Every migration must be **backward compatible with the previous release**, because a rolling deploy runs both versions at once and a rollback must not break the database. And know which operations take a blocking lock on your engine - `CREATE INDEX CONCURRENTLY`, `lock_timeout`, and batched backfills are what keep the change invisible.

## Detail

### Why "just run the migration" fails

Two facts make naive migrations outages:

1. **During any rolling deploy, old and new code run simultaneously.** A migration that renames a column breaks every old Pod instantly, and a rollback breaks every new one.
2. **Some DDL takes an exclusive lock and queues every query behind it.** In PostgreSQL, `ALTER TABLE ... ADD COLUMN` with a volatile default, a type change, or a non-concurrent index build takes `ACCESS EXCLUSIVE`. The lock itself may be fast - the danger is that it **queues behind a long-running read and then blocks everything behind it**, so a 50 ms migration causes a 4-minute outage. That is why `lock_timeout` plus retry is mandatory, not optional.

### Expand / contract, concretely

Splitting `users.name` into `first_name` and `last_name`, over three releases:

| Release | Migration                                            | Code                                  | Rollback safe?                              |
| ------- | ---------------------------------------------------- | ------------------------------------- | ------------------------------------------- |
| **1**   | Add `first_name`, `last_name` (nullable, no default) | Writes both old and new; reads `name` | Yes - old code ignores the new columns      |
| **1b**  | Backfill in batches, throttled, restartable          | unchanged                             | Yes                                         |
| **2**   | none                                                 | Reads new columns, still writes both  | Yes - data exists in both places            |
| **3**   | Add `NOT NULL` (validated), drop `name`              | Writes and reads new only             | Rollback now needs release 2, not release 1 |

The rule to state out loud: **a migration and the code that depends on it never ship in the same release**. The schema change goes first and is inert; the code that requires it follows.

### The operations that are dangerous, and their safe forms

- **Adding a column** - safe when nullable with no default (and, on modern PostgreSQL and MySQL 8, a constant default is also metadata-only). A volatile default rewrites the table.
- **Adding an index** - `CREATE INDEX CONCURRENTLY` in PostgreSQL (no write lock, cannot run in a transaction, can leave an `INVALID` index that you must drop and retry), `ALGORITHM=INPLACE, LOCK=NONE` in MySQL 8, or `gh-ost`/`pt-online-schema-change` for older MySQL.
- **Adding `NOT NULL`** - two steps: add a `CHECK ... NOT VALID` constraint, then `VALIDATE CONSTRAINT` (which takes only a share lock), rather than a full-table rewrite.
- **Adding a foreign key** - `NOT VALID` then `VALIDATE`, same reasoning.
- **Changing a column type** - usually a rewrite. Do it as add-new-column + dual-write + backfill + swap, not `ALTER TYPE`.
- **Renaming anything** - never in place. Add the new name, dual-write, migrate readers, drop the old one.
- **Dropping a column** - only after no deployed code references it. On PostgreSQL, `DROP COLUMN` is metadata-only and fast; the risk is entirely about code, and about rollback (the data is gone). Rename-then-drop-later, or take a snapshot first.
- **Backfills** - always batched (`LIMIT 1000` loops with a key cursor), throttled, restartable, and idempotent. A single `UPDATE` across 200 million rows holds locks, bloats WAL, and floods replicas with lag.

### Wiring it into the pipeline

- **Migrations are versioned, reviewed code** - Flyway, Liquibase, Alembic, or the framework's tool - applied automatically, never by hand. See [what are database migration tools](./what-are-database-migration-tools.md).
- **Run migrations as a separate, gated step before the deploy** (a Kubernetes Job or pipeline stage), not from application startup - concurrent startup migrations across replicas race, and an advisory lock is a workaround rather than a design.
- **Enforce safety in CI.** Lint migrations automatically (Squawk, `atlas migrate lint`, `strong_migrations` for Rails) so a dangerous statement fails review rather than production. Rehearse on a production-sized restored snapshot and record how long the change actually takes.
- **Make rollback explicit.** Every migration has a tested down-path or a documented "forward-only, here is the compensating change". Additive migrations rarely need reverting; destructive ones cannot be, which is the whole argument for expand/contract.
- **Watch during and after**: lock waits, replication lag, error rate, p99 latency, and the migration's own duration - with an abort rule agreed in advance.

### Planned maintenance windows still exist

Some changes genuinely need one - a storage engine change, a major-version upgrade, a repartition. Then the answer is different: announce it, put the application into a **degraded read-only mode** rather than fully down where possible (serve reads from a replica, queue writes for replay), keep the window short and rehearsed, and have the abort decision defined before you start. Saying "not every change can be online, and here is how I would minimise impact" is stronger than pretending everything is zero-downtime. See [how do you migrate a production database to the cloud with near-zero downtime](../cloud-migration/how-do-you-migrate-a-production-database-to-the-cloud-with-near-zero-downtime.md).

## Example

```sql
-- Release 1: expand. Additive, inert, safe with old and new code running.
ALTER TABLE users ADD COLUMN first_name text;      -- nullable, no volatile default
ALTER TABLE users ADD COLUMN last_name  text;

-- Index without blocking writes (cannot run inside a transaction)
CREATE INDEX CONCURRENTLY idx_users_last_name ON users (last_name);
-- if it fails it leaves an INVALID index:
--   SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;  then DROP and retry

-- Always: never let DDL queue behind a long read and block the world
SET lock_timeout = '3s';                            -- fail fast, retry, do not block
SET statement_timeout = '0';                        -- but let the DDL itself finish
```

```bash
# Release 1b: backfill in batches - throttled, restartable, replica-lag aware
last_id=0
while :; do
  rows=$(psql -qtAX "$DB" <<SQL
    WITH batch AS (
      SELECT id FROM users WHERE id > $last_id AND first_name IS NULL
      ORDER BY id LIMIT 1000
    )
    UPDATE users u SET first_name = split_part(u.name,' ',1),
                       last_name  = nullif(split_part(u.name,' ',2),'')
    FROM batch b WHERE u.id = b.id
    RETURNING u.id;
SQL
  )
  [ -z "$rows" ] && break
  last_id=$(echo "$rows" | tail -1)
  # back off if replicas are falling behind - the usual cause of a "successful"
  # backfill that takes the read path down
  lag=$(psql -qtAX "$REPLICA" -c "SELECT coalesce(extract(epoch from now()-pg_last_xact_replay_timestamp()),0)::int")
  [ "$lag" -gt 30 ] && sleep 30 || sleep 0.2
done
```

```sql
-- Release 3: contract. Only once no deployed code reads or writes the old column.
ALTER TABLE users ADD CONSTRAINT users_first_name_nn
  CHECK (first_name IS NOT NULL) NOT VALID;         -- instant, no rewrite
ALTER TABLE users VALIDATE CONSTRAINT users_first_name_nn;  -- share lock only
ALTER TABLE users DROP COLUMN name;                 -- metadata-only in PostgreSQL
```

## Interview tips

- Name the pattern - expand/contract, or parallel change - and state the invariant: every migration must be backward compatible with the previous release, because rolling deploys run both versions at once.
- Say that a migration and the code depending on it ship in **different** releases. This is the sentence that tells an interviewer you have done this in production.
- Explain the lock-queue mechanism, not just "DDL takes locks": the migration queues behind a long-running query and then blocks everything behind it, so a fast statement causes a long outage. `lock_timeout` plus retry is the fix.
- Know the safe forms by name - `CREATE INDEX CONCURRENTLY`, `CHECK ... NOT VALID` then `VALIDATE`, `gh-ost`/`pt-online-schema-change` for MySQL - and that concurrent index builds can leave an invalid index.
- Insist on batched, restartable, replica-lag-aware backfills. A single `UPDATE` over 200 million rows is the classic self-inflicted incident.
- Reject running migrations from application startup, and explain the race across replicas. Recommend a gated pipeline step instead.
- Tie it to rollback: additive migrations keep rollback safe, destructive ones do not - which is the entire justification for the three-release dance.
- Mention automated migration linting in CI, and rehearsal on a restored production-sized snapshot to get a real duration.
- Be willing to say some changes need a maintenance window, and describe read-only degraded mode as the way to shrink the impact. Honesty beats absolutism here. See [what is database DevOps](./what-is-database-devops.md).

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
