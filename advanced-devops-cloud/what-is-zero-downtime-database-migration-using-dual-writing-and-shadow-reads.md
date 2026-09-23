---
title: "What is Zero-Downtime Database Migration using Dual-Writing and Shadow Reads?"
id: 701
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - databases
  - migrations
  - zero-downtime
  - dual-write
  - shadowing
quiz:
  stem: "What is the primary function of 'Shadow Reads' when migrating from an old database to a new database?"
  options:
    - "To reduce the size of database index files"
    - "To execute queries against the new database asynchronously and compare results against the old database, verifying correctness and performance before cutover"
    - "To encrypt all database tables with AES-256"
    - "To bypass SQL syntax parsing"
  answer: 2
  explanation: "Shadow reads query the new database in parallel and compare returned rows and performance against the authoritative old database without impacting users, proving correctness before switching."
---

# What is Zero-Downtime Database Migration using Dual-Writing and Shadow Reads?

**Short answer:** You move from an old datastore to a new one (a different engine, schema, or cluster) while the application stays live, by keeping the old store as the source of truth until the new one has been proven: **backfill** historical data, keep the new store current with **dual writes or change data capture (CDC)**, run **shadow reads** that query both and compare results without affecting users, then **cut over** reads and finally writes, keeping a rollback path until the old store is retired. The hard part is consistency between the two writes - which is why CDC from the old store is usually safer than application-level dual writes.

## Detail

**The phases**

```text
1. Sync        App ──write──> OLD (source of truth) ──CDC / dual write──> NEW
2. Backfill    Batch copy of historical rows into NEW (idempotent, resumable, throttled)
3. Verify      App ──read──> OLD ──> response to user
                    └─shadow read──> NEW ──> compare, log mismatches (async, sampled)
4. Cut reads   App reads NEW (behind a flag, ramped 1% → 100%); still writes OLD first
5. Cut writes  NEW becomes source of truth; reverse replication NEW → OLD for rollback
6. Retire      Stop reverse sync, archive and decommission OLD
```

**Keeping NEW current: dual write versus CDC**

- **Application dual write** - the service writes OLD, then NEW. Simple to start, but the two writes are not atomic: a crash or timeout between them leaves the stores divergent, and ordering can differ under concurrency. If you do it, write OLD synchronously as truth, write NEW asynchronously with retries, and rely on reconciliation to repair drift.
- **CDC** - stream the old store's change log (for example Debezium reading the PostgreSQL WAL or MySQL binlog, or AWS DMS) into NEW. Every committed change is captured in order, and the application does not change. It also combines cleanly with the backfill (snapshot, then stream from the snapshot's log position). For heterogeneous migrations this is usually the better default.

**Shadow reads catch the semantic differences** a row-count check misses: collation and sort order, NULL handling, timestamp precision and time zones, numeric rounding, case sensitivity, and query-plan performance under real concurrency. Compare normalised results, sample to control cost, and track the mismatch rate as the gate for cutting over. Never let a shadow read add latency to the user's request - run it asynchronously or on a copy of the request.

**Cutover and rollback.** Use a feature flag rather than a deploy to switch reads, ramp gradually, and watch error rate and latency. When writes move, keep replicating NEW back to OLD for a defined period so rollback is a flag flip, not a data recovery exercise.

**Costs:** double write load and storage during the migration, a comparison pipeline to build, and weeks of calendar time. For a simple same-engine version upgrade, a managed blue/green or replica-promotion feature is usually far cheaper than this pattern.

## Example

```python
# Shadow read: OLD is authoritative, NEW is compared off the request path
import concurrent.futures, logging

shadow_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
log = logging.getLogger("migration")

def get_order(order_id: str) -> dict:
    result = old_db.fetch_order(order_id)                      # user gets this answer
    if flags.enabled("orders-shadow-read", sample=0.10):      # 10% sampled
        shadow_pool.submit(compare, order_id, result)
    return result

def compare(order_id: str, expected: dict) -> None:
    try:
        actual = new_db.fetch_order(order_id)
        if normalise(actual) != normalise(expected):
            log.warning("shadow_mismatch", extra={"order_id": order_id})
            metrics.increment("orders.shadow.mismatch")
        else:
            metrics.increment("orders.shadow.match")
    except Exception:
        metrics.increment("orders.shadow.error")               # never affects the user
```

## Interview tips

- Say which store is the source of truth at every phase - that single idea keeps the answer coherent.
- Name the dual-write consistency problem and offer CDC (Debezium, DMS) as the safer way to keep the new store in sync.
- Describe shadow reads as a correctness and performance gate with a measured mismatch rate, run off the request path.
- Cut over behind a flag, ramp gradually, and keep reverse replication so rollback stays cheap.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
