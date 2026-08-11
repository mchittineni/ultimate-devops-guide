---
title: "What is Database Performance Tuning?"
id: 115
category: "Database Management in DevOps"
difficulty: "Advanced"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
---

# What is Database Performance Tuning?

**Short answer:** Database performance tuning is the systematic process of finding and removing bottlenecks - through query optimisation, indexing, schema design, configuration, and caching - guided by measurement rather than guesswork.

## Detail

**Start by measuring.** Identify the slowest and most frequent queries: `pg_stat_statements` on PostgreSQL, the slow query log and Performance Schema on MySQL, or the cloud provider's performance insights. Optimise by total time consumed (frequency × duration), not by the single slowest query - a 5 ms query run a million times matters more than a 2 s report run hourly.

**Query and index work**

- Read the execution plan (`EXPLAIN ANALYZE`). Look for sequential scans on large tables, nested loops over big row counts, and mis-estimated row counts (a sign of stale statistics).
- Add indexes that match the query's filter and sort columns; composite index column order matters, and a covering index can avoid touching the table at all.
- Remove unused and duplicate indexes - every index slows writes and consumes memory.
- Eliminate N+1 query patterns from the application; this is frequently the single biggest win.
- Avoid `SELECT *`, and paginate with keyset pagination rather than large `OFFSET` values.

**Schema** - appropriate data types, normalisation balanced against read patterns, and partitioning for very large tables so queries touch one partition.

**Configuration** - memory allocation (`shared_buffers`, `work_mem`, buffer pool size), connection limits, checkpoint behaviour, and autovacuum tuning on PostgreSQL, where bloat is a common hidden cause of degradation.

**Architecture** - connection pooling (PgBouncer) because connections are expensive, read replicas for read-heavy workloads, caching (Redis) for hot data, and asynchronous processing for anything that does not need to be in the request path.

## Example

```sql
-- Find the highest-total-cost queries
SELECT calls, mean_exec_time, total_exec_time, query
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, total FROM orders WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 20;

-- Composite index matching filter + sort
CREATE INDEX CONCURRENTLY idx_orders_customer_created
  ON orders (customer_id, created_at DESC);
```

## Interview tips

- Prioritising by total time rather than individual duration is the insight that shows method.
- N+1 queries and connection pooling are the two highest-yield practical fixes - name both.
- Mention that every index is a write cost; unqualified "add an index" is a junior answer.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[How do you take a monthly release process to daily deployments?]] (`#285`): [How do you take a monthly release process to daily deployments?](../core-devops-concepts/how-do-you-take-a-monthly-release-process-to-daily-deployments.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
