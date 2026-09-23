---
title: "What is Read-Replica Lag in relational databases and how do you prevent stale reads?"
id: 594
category: "Scalability and High Availability"
difficulty: "Intermediate"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - databases
  - replication
  - postgres
  - mysql
  - scaling
quiz:
  stem: "How does the 'Read-Your-Own-Writes' pattern prevent users from seeing stale data after submitting a form?"
  options:
    - "It disables all database caching permanently"
    - "It routes read requests from the authoring user's session directly to the Primary database for a brief window after a write, while other users read from replicas"
    - "It forces all database transactions to execute in serializable isolation"
    - "It delays HTTP responses by 10 seconds to allow replicas to catch up"
  answer: 2
  explanation: "By routing reads back to the Primary database for the specific user who just made an update, that user sees their own changes immediately without forcing all global reads onto the Primary."
---

# What is Read-Replica Lag in relational databases and how do you prevent stale reads?

**Short answer:** Replication lag is the delay between when a transaction commits on the primary database and when it applies on read replicas; applications prevent stale reads using read-after-write routing (directing a user's reads to the primary for 5-10s after they write) or monotonic read consistency.

## Detail

Scaling read throughput by adding PostgreSQL or MySQL read replicas is standard, but replication is asynchronous by default: the primary commits, then ships the change (PostgreSQL WAL, MySQL binlog) and the replica applies it later. Lag is normally milliseconds, but grows to seconds or minutes under a write burst, a long-running transaction or DDL on the replica, a single-threaded apply bottleneck, or an undersized replica.

### The classic user bug

1. User updates their profile photo (`POST /profile`). The write commits on the primary.
2. The browser immediately redirects to `GET /profile`.
3. The read goes to a replica that is 500 ms behind.
4. The user sees the old photo and reports that the update failed.

### Solutions

1. **Read-your-own-writes routing.** For a short window after a user writes (a few seconds, tracked in the session or a cookie), route that user's reads to the primary. Other users keep reading from replicas. Simple and effective, but the window is a guess - if lag exceeds it, the bug returns.
2. **Causal (position-based) reads.** Better than a timer: after a write, record the commit position (PostgreSQL LSN from `pg_current_wal_lsn()`, MySQL GTID). Before reading from a replica, check that it has replayed past that position (`pg_last_wal_replay_lsn()`), or wait for it with MySQL's `WAIT_FOR_EXECUTED_GTID_SET()`. If it has not caught up, wait briefly or fall back to the primary.
3. **Lag-aware routing.** Monitor lag and pull a replica out of the read pool above a threshold (e.g. 1 s). Measure it from the primary with `pg_stat_replication.replay_lag` or on the replica with `now() - pg_last_xact_replay_timestamp()`; on MySQL 8.0.22+ use `SHOW REPLICA STATUS` and `Seconds_Behind_Source` (the older `SHOW SLAVE STATUS`/`Seconds_Behind_Master` names are deprecated). Proxies such as ProxySQL and pgpool, and Aurora's reader endpoint logic, can do this for you.
4. **Synchronous replication - with care.** PostgreSQL `synchronous_commit = remote_apply` makes the primary wait until a synchronous standby has _applied_ the commit, so reads there are fresh. PostgreSQL's default `on` (and MySQL semi-synchronous replication) only wait until the replica has _received/flushed_ the change - that protects durability, but a read on the replica can still be stale. Either way you pay cross-node latency on every commit, and a slow standby slows all writes.

**Trade-offs.** Every option moves cost somewhere: primary routing adds load to the primary, causal reads add a check (and occasionally a wait) to every read, synchronous replication adds write latency. Decide per query which reads can tolerate staleness (a product listing) and which cannot (an account balance after a transfer).

## Example

```sql
-- PostgreSQL: on the primary, how far behind is each replica?
SELECT application_name, state, write_lag, flush_lag, replay_lag
FROM pg_stat_replication;

-- On a replica: seconds since the last replayed transaction
-- (note: this grows on an idle primary too, so pair it with LSN comparison).
SELECT now() - pg_last_xact_replay_timestamp() AS replay_delay;

-- Causal read: capture the LSN after the write on the primary...
SELECT pg_current_wal_lsn();                        -- e.g. 0/5A3C1B8
-- ...then only read from a replica that has replayed past it.
SELECT pg_last_wal_replay_lsn() >= '0/5A3C1B8'::pg_lsn AS caught_up;
```

```sql
-- MySQL 8.0.22+: replica lag and GTID-based wait (up to 1 s) before reading.
SHOW REPLICA STATUS\G                                -- Seconds_Behind_Source
SELECT WAIT_FOR_EXECUTED_GTID_SET('3E11FA47-71CA-11E1-9E33-C80AA9429562:1-77', 1);
-- 0 = caught up, 1 = timed out: fall back to the primary
```

## Interview tips

- Explain where lag comes from: asynchronous WAL/binlog shipping and apply, and what makes it spike.
- Give read-your-own-writes as the quick fix, then upgrade it to position-based (LSN/GTID) causal reads - that is the senior answer.
- Know the lag-monitoring queries and use current MySQL terminology (`SHOW REPLICA STATUS`, `Seconds_Behind_Source`).
- Correct the common mistake: semi-sync replication guarantees the replica _received_ the change, not that it _applied_ it; only `remote_apply`-style settings give fresh reads.
- Close with the trade-off: freshness costs primary load, read latency, or write latency - choose per query.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
