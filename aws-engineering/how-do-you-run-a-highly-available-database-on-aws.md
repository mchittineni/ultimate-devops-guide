---
title: "How do you run a highly available database on AWS?"
id: 196
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# How do you run a highly available database on AWS?

**Short answer:** Use a managed engine with multi-AZ replication — RDS Multi-AZ (or better, Multi-AZ DB cluster) or Aurora — put the writer behind the cluster endpoint, route reads to the reader endpoint, and make the application survive a failover: short DNS caching, bounded connection lifetimes, retries on transient errors, and idempotent writes. Then prove it by triggering a failover in a non-production environment.

## Detail

**RDS Multi-AZ versus Aurora.** Classic RDS Multi-AZ keeps a synchronous standby that serves no traffic; failover is typically 60–120 seconds. RDS Multi-AZ DB clusters add two readable standbys and faster failover. Aurora separates compute from a distributed storage layer replicated six ways across three AZs, giving failover usually under 30 seconds, up to 15 low-lag readers, and faster restore/clone operations. Aurora costs more per hour and is not a drop-in for every extension or engine version.

**Failover is not transparent.** In-flight transactions are lost, connections are dropped, and the endpoint's DNS record is repointed. Applications must reconnect and retry — with jitter — and treat writes as idempotent where possible. A JVM caching DNS forever, or a connection pool with unlimited connection lifetime, will keep talking to the old endpoint long after failover; capping DNS TTL caching and pool connection age is required, not optional.

**RDS Proxy for connection-heavy workloads.** Lambda and horizontally scaled containers open far more connections than a relational engine handles well. RDS Proxy pools and multiplexes them, and shortens failover impact by holding client connections while it reconnects behind the scenes. The cost is an extra hop and per-vCPU pricing, plus caveats with session-level state (pinning).

**Reads, and the consistency you give up.** Replicas are asynchronous (except the RDS synchronous standby), so read-after-write from a replica can return stale data. Route reads that must be consistent to the writer, and design the rest to tolerate lag — measure `AuroraReplicaLag`/`ReplicaLag` and alert on it, because silent lag growth becomes a correctness bug in the application.

**Backups are separate from HA.** Multi-AZ protects against infrastructure failure, not against a bad migration or a dropped table. Automated backups with point-in-time recovery, a retention period matching your RPO, snapshot copies to a second region and ideally a second account (protecting against account compromise), and a _restore_ rehearsal — restore time is what your RTO actually depends on, and it is frequently much longer than teams assume.

**Cross-region.** Aurora Global Database offers sub-second-typical replication with promotion in minutes; cross-region read replicas are cheaper and slower. Decide whether you need cross-region disaster recovery or active-active, because active-active with a relational engine means resolving write conflicts, which is an application design problem.

## Example

```hcl
resource "aws_rds_cluster" "orders" {
  cluster_identifier     = "orders"
  engine                 = "aurora-postgresql"
  engine_version         = "16.4"
  database_name          = "orders"
  availability_zones     = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  db_subnet_group_name   = module.vpc.database_subnet_group_name

  backup_retention_period      = 14
  preferred_backup_window      = "02:00-03:00"
  copy_tags_to_snapshot        = true
  storage_encrypted            = true
  kms_key_id                   = aws_kms_key.rds.arn
  deletion_protection          = true
  performance_insights_enabled = true
}

resource "aws_rds_cluster_instance" "orders" {
  count                = 3 # one writer, two readers across AZs
  identifier           = "orders-${count.index}"
  cluster_identifier   = aws_rds_cluster.orders.id
  instance_class       = "db.r7g.large"
  engine               = aws_rds_cluster.orders.engine
  promotion_tier       = count.index # deterministic failover order
}
```

```text
Application requirements, not optional:
  writer -> orders.cluster-xxxx.eu-west-1.rds.amazonaws.com
  reader -> orders.cluster-ro-xxxx.eu-west-1.rds.amazonaws.com
  JVM: networkaddress.cache.ttl=5    pool: maxLifetime < 30 min
  retry transient errors with jitter; writes idempotent where feasible
```

## Interview tips

- Emphasise that HA is only half the answer — the application must survive failover, and backups cover a different failure class.
- Naming the DNS-cache and connection-lifetime pitfalls is the detail that shows you have lived through a failover.
- Expect: "what is your RTO?" — tie it to _tested_ restore time, and admit if you have not tested it.

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
