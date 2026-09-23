---
title: "What are ACID and BASE consistency models and how do they govern SQL versus NoSQL architectures?"
id: 663
category: "Database Management in DevOps"
difficulty: "Beginner"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - databases
  - acid
  - base
  - nosql
  - sql
quiz:
  stem: "What does the 'Eventual Consistency' property of the BASE model guarantee?"
  options:
    - "Data will be written to disk within exactly 10 milliseconds"
    - "If no further updates are made to a record, all distributed replicas will eventually synchronize and return identical data"
    - "Transactions are guaranteed to never fail"
    - "The database will automatically delete stale data every 24 hours"
  answer: 2
  explanation: "Eventual consistency concedes that replicas may temporarily serve out-of-sync data during updates, but guarantees that all nodes will converge to identical state once replication catches up."
---

# What are ACID and BASE consistency models and how do they govern SQL versus NoSQL architectures?

**Short answer:** ACID (Atomicity, Consistency, Isolation, Durability) guarantees strict transactional correctness standard in relational databases; BASE (Basically Available, Soft state, Eventual consistency) prioritizes high availability and partition tolerance standard in distributed NoSQL systems.

## Detail

The choice between relational and distributed NoSQL stores used to be framed as ACID versus BASE. The terms are still worth knowing precisely, but the dividing line has blurred.

### ACID (relational databases - PostgreSQL, MySQL, Oracle, SQL Server)

- **Atomicity**: all operations in a transaction succeed, or all are rolled back.
- **Consistency**: every committed transaction leaves the data satisfying its constraints - types, foreign keys, unique and check constraints. (This is _not_ the "C" in CAP, which means linearizability across replicas.)
- **Isolation**: concurrent transactions do not see each other's partial work. Engines offer levels - read committed (the PostgreSQL default), repeatable read (the MySQL InnoDB default), serializable - and lower levels permit anomalies such as non-repeatable reads or write skew in exchange for concurrency.
- **Durability**: once committed, data survives a crash, because the change was flushed to the write-ahead log (WAL/redo log) before the commit was acknowledged.

### BASE (distributed NoSQL - Cassandra, DynamoDB, Riak)

- **Basically available**: the system keeps accepting reads and writes during node failures or partitions.
- **Soft state**: replica state can change without new input, as background replication and repair converge it.
- **Eventual consistency**: if writes stop, all replicas eventually return the same value. Until then, a read may be stale, and concurrent writes need conflict resolution (last-writer-wins, vector clocks, CRDTs).

### Why the split is no longer clean

- **NoSQL systems added transactions.** MongoDB has multi-document ACID transactions (since 4.0), DynamoDB has `TransactWriteItems` and strongly consistent reads, and Cassandra offers lightweight transactions (Paxos-based compare-and-set).
- **Distributed SQL gives ACID at scale.** Spanner, CockroachDB, YugabyteDB, and Aurora DSQL provide serializable or snapshot transactions across nodes and regions, paying with write latency rather than consistency.
- **Relational databases are often run with BASE-like reads.** An asynchronous read replica is eventually consistent, whatever the engine.

So the practical question is per operation: _which invariants must never be violated, and what latency or availability am I willing to pay for them?_

### Rule of thumb

- Money movement, ledgers, inventory reservation, and anything with a uniqueness invariant need ACID transactions (or a carefully designed single-item atomic operation).
- Clickstreams, IoT telemetry, activity feeds, and counters that tolerate brief staleness are good BASE candidates, where availability and write throughput matter more than instant agreement.

## Example

```sql
-- ACID: a transfer either fully happens or not at all, and cannot overdraw.
BEGIN ISOLATION LEVEL SERIALIZABLE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1 AND balance >= 100;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;  -- on a serialization failure (SQLSTATE 40001) the app retries the whole transaction
```

```sql
-- BASE (Cassandra CQL): fast, available writes; reads at ONE may be briefly stale.
CONSISTENCY ONE;
INSERT INTO clicks (user_id, ts, url) VALUES (42, toTimestamp(now()), '/pricing');
```

## Interview tips

- Define each letter precisely, and point out that ACID's "C" (constraints) and CAP's "C" (linearizability) are different things.
- Mention isolation levels - saying "ACID" without knowing that the default is usually read committed is a common gap.
- Explain eventual consistency with its cost: stale reads and conflict resolution such as last-writer-wins, which can silently drop an update.
- Show you know the landscape has moved: MongoDB and DynamoDB transactions, and distributed SQL giving ACID at scale.
- Frame the decision per operation - which invariants need a transaction - rather than per product.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[What is the difference between Artifact Promotion and rebuilding binaries across environments?]] (`#534`): [What is the difference between Artifact Promotion and rebuilding binaries across environments?](../cicd/what-is-the-difference-between-artifact-promotion-and-rebuilding-binaries-across-environments.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
