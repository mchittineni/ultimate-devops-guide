---
title: "How do you upgrade, scale, and resize an RDS instance without downtime?"
id: 480
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - database-management-in-devops
  - scalability-and-high-availability
---

# How do you upgrade, scale, and resize an RDS instance without downtime?

**Short answer:** Every change to an RDS instance falls into one of three buckets, and the technique differs. **Truly online**: storage growth (gp3/gp2 autoscaling or a manual increase - you cannot shrink), adding read replicas, and most parameter changes with a `dynamic` apply type. **A brief failover** (~60 seconds, and typically 30-120): instance-class resize and minor engine upgrades on a **Multi-AZ** instance - AWS modifies the standby, then fails over, so the outage is one DNS/endpoint switch rather than a full restart. **Genuinely disruptive**: major version upgrades, which rewrite the catalogue and cannot be rolled back - do those with a **blue/green deployment** (AWS creates a synchronised green copy, you upgrade and test it, then switch over in about a minute) or with logical replication to a new instance. Vertical scaling is a resize; horizontal scaling is read replicas for reads and sharding or Aurora for writes. And the rule that makes all of this survivable: **the application must reconnect**, so connection pooling with retry, short DNS TTL respect, and RDS Proxy are what turn a 60-second failover into something users do not notice.

## Detail

### What each change actually costs you

| Change                                  | Downtime                                                 | Notes                                                                                                         |
| --------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Increase storage                        | **None**                                                 | Online. Cannot shrink - that needs a dump/restore or a new instance. A 6-hour cooldown before the next change |
| Enable storage autoscaling              | None                                                     | Set a max threshold; prevents the 3 a.m. full-disk incident                                                   |
| Add / remove a read replica             | None to the primary                                      | Replica creation adds load; do it off-peak on a busy primary                                                  |
| Change most parameters (`dynamic`)      | None                                                     | `static` parameters need a reboot to take effect                                                              |
| **Resize instance class**               | ~60s with Multi-AZ (failover); several minutes single-AZ | Multi-AZ turns a restart into a failover                                                                      |
| **Minor engine upgrade**                | ~60s with Multi-AZ                                       | Can be automatic in the maintenance window                                                                    |
| **Major engine upgrade** (e.g. 15 → 16) | Minutes to hours, **no rollback**                        | Use blue/green. Test extensions, deprecated syntax, and the query planner                                     |
| Convert single-AZ → Multi-AZ            | None (brief I/O impact)                                  | Do this before you need it                                                                                    |
| Change the primary's AZ or subnet group | Failover                                                 |                                                                                                               |

The single most useful design decision is **Multi-AZ**, because it converts most maintenance from "restart the database" into "fail over to the standby". If an interviewer asks how you resize a production database with minimal downtime, that is the first sentence of the answer.

### Multi-AZ versus a read replica - the distinction that always comes up

|                | Multi-AZ standby                              | Read replica                                               |
| -------------- | --------------------------------------------- | ---------------------------------------------------------- |
| Purpose        | **Availability**                              | **Read scaling** (and a DR building block)                 |
| Replication    | Synchronous (Multi-AZ instance)               | **Asynchronous** - lag is normal                           |
| Readable       | No, on a classic Multi-AZ instance deployment | Yes                                                        |
| Failover       | Automatic, endpoint stays the same            | **Manual promotion**, and it becomes a standalone instance |
| Cross-region   | No                                            | Yes                                                        |
| Data loss risk | None (synchronous)                            | Whatever the replica lag was at failure                    |

The nuance worth adding: **Multi-AZ DB cluster** deployments (two readable standbys, semi-synchronous) narrow the gap by giving you readable standbys and faster failover. And promotion is one-way - a promoted replica cannot go back to being a replica.

For the classic scenario _"RDS is in one region with read replicas in others; the primary region goes down and a second writable database is too expensive"_: promote the cross-region read replica, repoint the application (Route 53 health-check failover or a connection string in Parameter Store rather than a hard-coded endpoint), accept the RPO equal to the replication lag at failure, and afterwards rebuild replication in the new direction. State the RPO explicitly - that is the part interviewers listen for.

### The other frequently-asked failover question

_"A failover happens and the connection switches from A to B; a user is mid-write - how do you manage that?"_ Be honest: the in-flight transaction **fails**. Synchronous replication guarantees the committed data is on the standby, so nothing acknowledged is lost, but uncommitted work is rolled back and the connection is dropped. So the application must: use a connection pool that detects the broken connection and reconnects (not one that caches a dead socket for ten minutes), retry **idempotent** operations with backoff, wrap the write in a transaction so a partial write cannot persist, and use an idempotency key for anything financial so a retry cannot double-charge. Java clients need the JVM DNS TTL lowered (`networkaddress.cache.ttl`), because caching the old IP forever is a genuinely common cause of a "failover that did not work". **RDS Proxy** helps materially here: it holds the connections, absorbs the failover, and reduces failover time as seen by the application.

### Vertical versus horizontal scaling

- **Vertical**: modify the instance class. Fast, no application change, and the ceiling is the largest instance. With Multi-AZ, roughly a minute of downtime. This is the answer to "the SQL database CPU is above 75%, how do you scale it up?" - but first check whether it is a query problem: one missing index frequently beats doubling the instance size, and buying capacity to hide a bad query is a habit that gets expensive.
- **Horizontal, reads**: read replicas plus a reader endpoint (Aurora gives you one built in with load balancing across replicas). The application must be able to route reads separately and tolerate replica lag - "read your own write" bugs come from sending a read to a replica immediately after a write.
- **Horizontal, writes**: RDS does not shard for you. Options are Aurora (a shared storage layer that scales to 15 replicas and supports Serverless v2 auto-scaling), application-level sharding, or Aurora Limitless/a different data model. Say plainly that write scaling is an application-architecture problem, not a knob.
- **Connection limits**: `max_connections` on RDS scales with instance memory, and hundreds of application replicas each holding a pool will exhaust it long before CPU is the issue. The fix is pooling in the application plus **RDS Proxy** - which is exactly the answer to "the client application had no connection pooling, how did you handle that?"

### Storage: full, and how to not be there again

The "production RDS storage is at 95%" scenario has an immediate action and a prevention:

- **Immediate**: enable/raise **storage autoscaling** (online), or manually increase storage (online). Then find the consumer - bloated tables, unvacuumed dead tuples on PostgreSQL, binlogs/WAL retention, oversized temporary files, or an audit table nobody truncates. Free space by archiving to S3 and reclaiming (`VACUUM FULL` locks, `pg_repack` does not; `OPTIMIZE TABLE` on MySQL).
- **Prevention**: autoscaling with a max, a CloudWatch alarm on `FreeStorageSpace` well before it matters, retention policies on log tables, and a scheduled check on table growth. Note the traps: you cannot shrink storage, and there is a cooldown before another storage change - so the fix is not instant if you have already just changed it.

### Read-only access for a developer

A small, very frequently asked one: create a database user (not an IAM/RDS admin) with `SELECT` only on the schemas needed, hand out credentials via Secrets Manager (or better, **IAM database authentication** so there is no password at all), connect through a Session Manager port-forward rather than exposing the instance, and enforce it at both layers - a read-only DB role and a security group that only permits the bastion/endpoint path. "Only one user may access it at a time" is not a database feature - answer with connection limits per role (`ALTER ROLE ... CONNECTION LIMIT 1`), a security group restricted to one source, and pooling through a proxy, and note that the request is usually better solved by an advisory lock or a queue in the application.

### Doing the upgrade safely

1. **Blue/green deployment** (RDS-managed): AWS builds a green environment replicating from blue, you upgrade and test green, then switch over - typically under a minute, with writes blocked briefly and the endpoints swapped. It is the default answer for major version upgrades now.
2. **Pre-flight**: check extension compatibility, deprecated syntax, collation changes, and the query planner (a plan regression after a major upgrade is common - capture baseline plans first). Restore a snapshot into a test instance and run your real workload against it.
3. **Snapshot before, always** - and remember a snapshot restore creates a **new instance** with a new endpoint, so recovery is a repoint rather than an in-place rollback.
4. **Maintenance windows** for automatic minor upgrades; set them deliberately rather than accepting the default, and disable auto-minor-version for anything where you need to test first.
5. **Communicate the failover** as an expected 60-second blip, and validate afterwards with error rates and connection metrics rather than a manual check.

## Example

```hcl
# The configuration that makes maintenance cheap later
resource "aws_db_instance" "orders" {
  identifier     = "orders-prod"
  engine         = "postgres"
  engine_version = "16.4"
  instance_class = "db.r6g.xlarge"

  multi_az                    = true  # turns restarts into ~60s failovers
  allocated_storage           = 200
  max_allocated_storage       = 2000  # storage autoscaling: no 3am full-disk incident
  storage_type                = "gp3"
  storage_encrypted           = true
  kms_key_id                  = aws_kms_key.rds.arn

  backup_retention_period     = 14
  copy_tags_to_snapshot       = true
  deletion_protection         = true
  skip_final_snapshot         = false
  auto_minor_version_upgrade  = false          # we test minor upgrades ourselves
  maintenance_window          = "sun:03:00-sun:04:00"
  performance_insights_enabled = true
  iam_database_authentication_enabled = true   # no passwords for humans
  enabled_cloudwatch_logs_exports     = ["postgresql", "upgrade"]

  blue_green_update { enabled = true }         # major upgrades via blue/green
  lifecycle { prevent_destroy = true }
}

resource "aws_db_instance" "orders_replica_ie" {
  identifier          = "orders-prod-replica-ie"
  replicate_source_db = aws_db_instance.orders.identifier
  instance_class      = "db.r6g.large"
  # async: expect lag. Promotion is one-way and makes it standalone.
}
```

```bash
# Online: storage growth (never shrink), and check the cooldown first
aws rds modify-db-instance --db-instance-identifier orders-prod \
  --allocated-storage 400 --max-allocated-storage 2000 --apply-immediately

# ~60s failover: resize on Multi-AZ. Watch events rather than guessing.
aws rds modify-db-instance --db-instance-identifier orders-prod \
  --db-instance-class db.r6g.2xlarge --apply-immediately
aws rds describe-events --source-identifier orders-prod --source-type db-instance \
  --duration 60 --query 'Events[].[Date,Message]' --output table

# Major upgrade: blue/green, test green, then switch over
aws rds create-blue-green-deployment --blue-green-deployment-name orders-pg17 \
  --source "$(aws rds describe-db-instances --db-instance-identifier orders-prod \
      --query 'DBInstances[0].DBInstanceArn' --output text)" \
  --target-engine-version 17.2
# ... run your test suite against the green endpoint ...
aws rds switchover-blue-green-deployment --blue-green-deployment-identifier bgd-0abc \
  --switchover-timeout 300

# DR: promote a cross-region replica (one-way), then repoint the application
aws rds promote-read-replica --db-instance-identifier orders-prod-replica-ie
aws ssm put-parameter --name /prod/db/endpoint --overwrite \
  --value "orders-prod-replica-ie.abc.eu-west-1.rds.amazonaws.com"
```

```sql
-- Read-only developer access: least privilege at the database layer
CREATE ROLE dev_readonly;
GRANT CONNECT ON DATABASE orders TO dev_readonly;
GRANT USAGE ON SCHEMA public TO dev_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dev_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dev_readonly;

CREATE USER alice WITH LOGIN;                       -- IAM auth: no password stored
GRANT rds_iam TO alice;                             -- authenticate with an IAM token
GRANT dev_readonly TO alice;
ALTER ROLE alice CONNECTION LIMIT 2;                -- cap concurrent connections
```

```bash
# Storage at 95%: act, then find the cause
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name FreeStorageSpace \
  --dimensions Name=DBInstanceIdentifier,Value=orders-prod \
  --start-time "$(date -u -d '-7 days' +%FT%TZ)" --end-time "$(date -u +%FT%TZ)" \
  --period 3600 --statistics Minimum
# in the database: who is eating the disk?
#   SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_catalog.pg_statio_user_tables
#   ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;
#   SELECT name, setting FROM pg_settings WHERE name IN ('wal_keep_size','max_wal_size');
```

## Interview tips

- Structure the answer into online, brief-failover, and disruptive changes. That framing answers half a dozen variations of the question at once and shows you think in terms of blast radius.
- Say **Multi-AZ turns a restart into a ~60-second failover** early. It is the design decision that makes resizes and minor upgrades acceptable in production.
- Get the Multi-AZ-versus-read-replica distinction crisp: availability with synchronous replication and a stable endpoint, versus read scaling with async replication and manual, one-way promotion. Mention Multi-AZ DB clusters as the readable-standby variant.
- For the mid-write failover question, be honest that the in-flight transaction fails, then explain what makes it survivable: pooling with reconnect and retry, idempotent writes with idempotency keys, lowered JVM DNS TTL, and RDS Proxy.
- Answer "CPU is at 75%, scale it up" with a caveat first - check for a missing index or a bad query before buying a bigger instance - then describe the resize with Multi-AZ. That order signals engineering judgement rather than button-pushing.
- Say plainly that RDS does not scale writes: replicas scale reads, and write scaling means Aurora, sharding, or an application change. Add that `max_connections` scales with memory and is often the real limit, fixed by pooling plus RDS Proxy.
- For major upgrades, name **blue/green deployments**, the lack of rollback, and the pre-flight work (extensions, deprecated syntax, plan regressions on a restored snapshot).
- For storage at 95%, give the immediate online action (autoscaling or increase), the investigation (bloat, WAL/binlog retention, unvacuumed tables), and the two constraints - you cannot shrink, and there is a cooldown. See [running a highly available database on AWS](./how-do-you-run-a-highly-available-database-on-aws.md), [troubleshooting a database that is slow or timing out](../database-management-in-devops/how-do-you-troubleshoot-a-database-that-is-slow-or-timing-out-under-load.md), [changing a production schema without downtime](../database-management-in-devops/how-do-you-change-a-production-database-schema-without-downtime.md), and [migrating a production database to the cloud](../cloud-migration/how-do-you-migrate-a-production-database-to-the-cloud-with-near-zero-downtime.md).

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
