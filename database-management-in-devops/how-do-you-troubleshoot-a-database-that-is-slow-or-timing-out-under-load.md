---
title: "How do you troubleshoot a database that is slow or timing out under load?"
id: 417
category: "Database Management in DevOps"
difficulty: "Advanced"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - performance-testing
  - monitoring-and-logging
  - scalability-and-high-availability
---

# How do you troubleshoot a database that is slow or timing out under load?

**Short answer:** Separate "the database is slow" from "the application cannot get a connection", because they look identical from the outside and have opposite fixes. Look at **active sessions and what they are waiting on** first - that one view tells you whether you are CPU-bound, I/O-bound, lock-bound, or simply out of connections. Then work down: **connection pool exhaustion** (usually the real cause of timeouts, and adding database capacity makes it worse), **a missing index or a plan regression** on one hot query, **lock and transaction contention** (long transactions, idle-in-transaction sessions), **I/O saturation or storage credit exhaustion**, and only then vertical scale, read replicas, or caching. Fix the query before you buy the hardware.

## Detail

### First: is it the database, the pool, or the network?

- **Timeouts with the database at low CPU** = the client never got a connection. Check pool size, pool wait time, and pool timeout in the application, plus `max_connections` on the server and how many are idle. A serverless or autoscaled application multiplies pools by instance count, so 40 Pods × a pool of 20 is 800 connections against a server configured for 200 - the connections are rejected and every request times out while the database looks idle. This is the single most common production shape and the reason to name it first.
- **Timeouts with the database at high CPU or high I/O wait** = genuine server-side saturation. Move to the query and wait analysis below.
- **Intermittent, with clean server metrics** = network path, DNS, failover, or a proxy: check for connection resets, a recent failover event, and DNS TTL on the endpoint. See [how do you debug DNS resolution failures inside a Kubernetes cluster](../kubernetes/how-do-you-debug-dns-resolution-failures-inside-a-kubernetes-cluster.md).

### Wait analysis: the fastest route to the cause

Every mature engine exposes what sessions are waiting on - `pg_stat_activity.wait_event_type` and `pg_stat_statements` in PostgreSQL, `performance_schema` and `SHOW ENGINE INNODB STATUS` in MySQL, Performance Insights on RDS, Query Store on SQL Server. Read the distribution of active sessions by wait type:

- **CPU** - inefficient plans, missing indexes, or too much work per request.
- **I/O** (`DataFileRead`, buffer pool misses) - working set larger than memory, or under-provisioned storage.
- **Lock** (`Lock`, `transactionid`, row lock waits) - contention, long transactions, or a migration holding an exclusive lock.
- **Client** (`ClientRead`, `idle in transaction`) - the application is holding a transaction open while doing something else, which is an application bug that looks like a database problem.

### The recurring server-side causes

1. **One query, missing an index.** Find the top consumers by _total_ time (`pg_stat_statements` ordered by `total_exec_time`, not mean) - a 20 ms query run 10,000 times a second costs more than a 4-second report. Then `EXPLAIN (ANALYZE, BUFFERS)` it and look for sequential scans on large tables, a row-estimate error of orders of magnitude (stale statistics - `ANALYZE`), or a sort spilling to disk. Add the index, or fix the query so it can use one (a function or an implicit type cast on the column makes an index unusable).
2. **Plan regression.** The same query got slower without a code change: statistics drift, data-volume growth crossing a plan threshold, or parameter sniffing. `ANALYZE`, then consider a plan hint or query rewrite as a targeted fix.
3. **Lock contention.** Look for the blocking chain, not the blocked session - `pg_blocking_pids()` or MySQL's `data_lock_waits`. Usual culprits: a schema migration taking `ACCESS EXCLUSIVE` behind a queue of readers, a batch job updating rows in a different order from the online path (deadlocks), and `idle in transaction` sessions holding locks because the application forgot to commit. Set `statement_timeout`, `lock_timeout`, and `idle_in_transaction_session_timeout` so a stuck session cannot take the service down.
4. **I/O and storage limits.** Cloud volumes have IOPS and throughput ceilings, and burst-credit models (gp2, older Azure tiers) fail exactly when sustained load arrives - a database that is fine for an hour then collapses is often burst exhaustion. Check queue depth and read/write latency, then move to provisioned IOPS or a larger volume.
5. **Memory and cache hit ratio.** A buffer pool or `shared_buffers` far smaller than the hot working set turns every query into I/O. Cache hit ratio dropping is often the first signal of data growth outrunning the instance size.
6. **Connection storms and thundering herds.** A restart or failover where every client reconnects at once, or aggressive retries with no backoff, saturates the server. Fix with jittered exponential backoff, circuit breakers, and a pooler.

### The fixes, cheapest first

**Fix the query** (index, rewrite, statistics) → **fix the pooling** (right-size pools, add PgBouncer/ProxySQL/RDS Proxy in transaction mode so hundreds of clients share tens of server connections) → **add caching** for hot read paths (Redis, with an explicit invalidation story) → **offload reads to replicas** (accepting replication lag, and only for queries that tolerate stale reads) → **scale vertically** (simple, has a ceiling, needs a failover) → **partition or shard** (last, because it changes the application). Two guardrails: read replicas do not help write-bound workloads, and vertical scaling a database whose problem is one missing index is how a cloud bill doubles with no improvement.

### Prevention

Alert on the leading indicators, not just availability: p99 query latency, active sessions versus `max_connections`, pool wait time, replication lag, cache hit ratio, oldest transaction age, and deadlock rate. Keep slow-query logging on with a sensible threshold. Run migrations and heavy batch jobs off-peak with lock timeouts. Load test with production-shaped data volumes, since plans change with cardinality. See [what is database performance tuning](./what-is-database-performance-tuning.md) and [how do you load test safely against production](../performance-testing/how-do-you-load-test-safely-against-production.md).

## Example

```sql
-- 1. What are sessions actually waiting on right now? (PostgreSQL)
SELECT state, wait_event_type, wait_event, count(*)
FROM pg_stat_activity WHERE backend_type = 'client backend'
GROUP BY 1,2,3 ORDER BY 4 DESC;
--  active | Lock     | transactionid | 47   <- lock contention, not CPU
--  idle in transaction | Client | ClientRead | 12   <- application not committing

-- 2. Who is blocking whom - chase the blocker, not the victim
SELECT pid, pg_blocking_pids(pid) AS blocked_by, now()-xact_start AS xact_age, left(query,60)
FROM pg_stat_activity WHERE cardinality(pg_blocking_pids(pid)) > 0;

-- 3. Cost by TOTAL time, not average - frequency matters more than duration
SELECT calls, round(total_exec_time) ms_total, round(mean_exec_time,1) ms_avg, left(query,70)
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- 4. Why is that one slow? Look for seq scans and bad row estimates.
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE customer_id = 42 AND status = 'open';
--  Seq Scan on orders (rows=1 000 000) (actual rows=3 loops=1)  <- estimate is wrong
--  -> ANALYZE orders; then CREATE INDEX CONCURRENTLY ... (customer_id, status);

-- 5. Connections: exhausted, or idle?
SELECT count(*) FILTER (WHERE state='active') AS active,
       count(*) FILTER (WHERE state like 'idle%') AS idle,
       current_setting('max_connections') AS max FROM pg_stat_activity;

-- 6. Guardrails so one bad session cannot take the service down
ALTER ROLE app SET statement_timeout = '30s';
ALTER ROLE app SET lock_timeout = '3s';
ALTER ROLE app SET idle_in_transaction_session_timeout = '60s';
```

```text
The pool-exhaustion shape - why "the database is slow" was wrong

  40 app pods x pool_max 20            = 800 possible connections
  postgres max_connections             = 200
  observed: 200 server connections, 85% idle, CPU 12%, p99 app latency 30s (timeouts)

  Wrong fix: scale the instance up   -> same 200 limit, same timeouts, 2x the bill
  Right fix: PgBouncer in transaction mode (800 client conns -> 40 server conns),
             pool_max 5 per pod, acquire timeout 2s with a clear error,
             and a dashboard for pool wait time next to query latency.
```

## Interview tips

- Split "slow database" from "cannot get a connection" in your first sentence, and say the tell: timeouts with low database CPU means the pool, not the engine.
- The pool-exhaustion arithmetic (pods × pool size versus `max_connections`) is the most valuable thing you can say here. It is extremely common and most candidates never mention it.
- Lead the server-side answer with wait analysis rather than a list of tuning tips - naming `pg_stat_activity.wait_event_type` or Performance Insights shows you diagnose by evidence.
- Order slow queries by **total** time, not mean, and explain why frequency dominates. It is a small point that reads as real experience.
- Mention `idle in transaction` as an application bug that presents as a database problem, and the three timeouts (`statement_timeout`, `lock_timeout`, `idle_in_transaction_session_timeout`) as the guardrails you would set.
- Give the escalation ladder cheapest-first and state the anti-pattern plainly: scaling the instance to fix a missing index doubles the bill and changes nothing.
- Know the limits of the popular answers - read replicas do not help writes and add lag; caching needs an invalidation story; sharding changes the application.
- Close on the leading indicators you would alert on, and on load testing with production-shaped data because plans change with cardinality.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
