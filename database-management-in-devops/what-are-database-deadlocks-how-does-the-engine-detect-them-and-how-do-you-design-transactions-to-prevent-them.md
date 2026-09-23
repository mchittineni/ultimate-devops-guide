---
title: "What are Database Deadlocks, how does the engine detect them, and how do you design transactions to prevent them?"
id: 667
category: "Database Management in DevOps"
difficulty: "Intermediate"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - databases
  - deadlocks
  - transactions
  - locking
  - sql
quiz:
  stem: "What is the most effective application design pattern for preventing database deadlocks when transactions must update multiple rows?"
  options:
    - "Increasing the database CPU core count to 64"
    - "Ensuring that all transactions acquire locks on rows in the exact same deterministic order (e.g. sorted by Primary Key)"
    - "Disabling transactions across all application services"
    - "Converting all tables into unindexed heap tables"
  answer: 2
  explanation: "If every transaction locks rows in the exact same sorted order (e.g. always lock ID 1 before ID 2), circular wait dependencies are mathematically impossible, preventing deadlocks."
---

# What are Database Deadlocks, how does the engine detect them, and how do you design transactions to prevent them?

**Short answer:** A deadlock occurs when two transactions hold locks on separate resources and each waits for the other to release its lock, forming a circular wait dependency; database engines detect circular lock wait cycles via dependency graphs and terminate one transaction with an error.

## Detail

A deadlock is a cycle in the "waits-for" relationship between transactions. No amount of waiting resolves it, so the engine must break it by aborting one participant.

### Anatomy of a deadlock

1. **Transaction 1** updates row A and holds an exclusive lock on it.
2. **Transaction 2** updates row B and holds an exclusive lock on it.
3. **Transaction 1** tries to update row B and blocks, waiting for T2.
4. **Transaction 2** tries to update row A and blocks, waiting for T1.

Neither can ever proceed. Common real-world sources: two code paths updating the same tables in a different order, a batch job and the online path touching rows in different key orders, foreign-key checks taking share locks on parent rows, and lock escalation or gap/next-key locks in MySQL InnoDB under repeatable read.

### Detection

- **PostgreSQL**: a backend that has waited on a lock for `deadlock_timeout` (default 1 s) builds the wait-for graph and checks for a cycle. If it finds one, one transaction is aborted with `ERROR: deadlock detected` (SQLSTATE `40P01`). The timeout exists because the check is relatively expensive and most lock waits resolve on their own.
- **MySQL InnoDB**: detection is immediate on each lock wait (`innodb_deadlock_detect = ON`), and the transaction that has modified the fewest rows is rolled back (error 1213). On very high-concurrency systems detection itself can become a bottleneck, and some teams disable it and rely on `innodb_lock_wait_timeout` instead.
- **SQL Server**: a background lock monitor detects cycles and chooses a victim by `DEADLOCK_PRIORITY` and rollback cost (error 1205).

The aborted transaction is rolled back, so **the application must retry it** - deadlocks under concurrency are expected, not exceptional.

### Prevention

- **Consistent lock ordering**: always touch rows (and tables) in the same deterministic order, e.g. sorted by primary key. A cycle needs two transactions acquiring in opposite orders, so a total order makes it impossible.
- **Keep transactions short**: no HTTP calls, user think-time, or heavy computation while holding locks.
- **Lock what you need up front**: `SELECT ... FOR UPDATE` on all rows at the start, in key order, rather than acquiring them one by one.
- **Fail or skip instead of waiting**: `FOR UPDATE NOWAIT` errors immediately if a row is locked; `FOR UPDATE SKIP LOCKED` is the right tool for job-queue tables where workers should take the next free row.
- **Index foreign keys and filter columns** so updates lock only the rows they need rather than scanning (and locking) more.
- **Retry with jittered backoff** on `40P01`/`1213`, with a small attempt limit, and alert on the deadlock rate rather than on individual occurrences.

**Trade-off.** Ordering and up-front locking reduce concurrency and require discipline across every code path; retries hide deadlocks until their rate grows. Measure the rate so a rising trend is noticed.

## Example

```sql
-- Deadlock-safe transfer: lock both rows in primary-key order, whichever direction
-- the money moves, so two opposite transfers cannot form a cycle.
BEGIN;
SELECT id FROM accounts WHERE id IN (7, 3) ORDER BY id FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 7;
UPDATE accounts SET balance = balance + 100 WHERE id = 3;
COMMIT;

-- Job queue: workers never wait on each other.
SELECT id FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED;

-- PostgreSQL: log lock waits longer than deadlock_timeout, and count deadlocks.
ALTER SYSTEM SET log_lock_waits = on;
SELECT datname, deadlocks FROM pg_stat_database WHERE datname = current_database();
```

## Interview tips

- Describe the circular wait precisely, then explain that the engine breaks it by aborting a victim - it does not "time out".
- Know engine differences: PostgreSQL checks after `deadlock_timeout`, InnoDB detects immediately, SQL Server uses a lock monitor.
- Lead prevention with consistent lock ordering and short transactions; add `SKIP LOCKED` for queues.
- Say the application must retry on the deadlock error code - an unhandled deadlock becomes a user-facing 500.
- Mention monitoring: `log_lock_waits`, `pg_stat_database.deadlocks`, or `SHOW ENGINE INNODB STATUS` for the last deadlock.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
