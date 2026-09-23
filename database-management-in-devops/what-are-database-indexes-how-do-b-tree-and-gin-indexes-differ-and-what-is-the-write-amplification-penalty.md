---
title: "What are Database Indexes, how do B-Tree and GIN indexes differ, and what is the write amplification penalty?"
id: 664
category: "Database Management in DevOps"
difficulty: "Intermediate"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - databases
  - indexing
  - b-tree
  - gin
  - performance
quiz:
  stem: "Which PostgreSQL index type is specifically optimized for querying inside semi-structured JSONB documents and array columns?"
  options:
    - "B-Tree index"
    - "Hash index"
    - "Generalized Inverted Index (GIN)"
    - "BRIN index"
  answer: 3
  explanation: "GIN (Generalized Inverted Index) indexes decompose composite types (arrays, full-text documents, and JSONB keys), making it the optimal choice for JSONB containment operators (`@>`)."
---

# What are Database Indexes, how do B-Tree and GIN indexes differ, and what is the write amplification penalty?

**Short answer:** Indexes are auxiliary search trees that accelerate SELECT queries from $O(N)$ sequential scans to $O(\log N)$ lookups; B-Tree indexes excel at equality and range comparisons, GIN indexes excel at multi-value arrays and JSONB documents, and every index imposes a write amplification penalty on INSERT, UPDATE, and DELETE operations.

## Detail

Without a usable index, the database must scan every row (a sequential or full table scan). An index is a separate structure, kept in sync with the table, that lets the engine find matching rows directly.

### Common PostgreSQL index types

| Type       | Structure                              | Best for                                                                                             |
| ---------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **B-tree** | Balanced tree of sorted keys (default) | Equality, ranges (`<`, `BETWEEN`), `ORDER BY`, prefix `LIKE 'abc%'`, uniqueness                      |
| **GIN**    | Inverted index: element → list of rows | Arrays (`tags @> '{devops}'`), JSONB containment (`data @> '{"status":"active"}'`), full-text search |
| **GiST**   | Balanced tree of bounding predicates   | Geometric/PostGIS data, ranges, nearest-neighbour, exclusion constraints                             |
| **BRIN**   | Min/max summary per block range        | Huge, naturally ordered tables (time-series by insert time) - tiny and cheap                         |
| **Hash**   | Hash table                             | Equality only; rarely better than B-tree                                                             |

A B-tree finds a key in $O(\log N)$ page reads and returns rows in order, which is why it can also satisfy sorts. A GIN index stores each _element_ of a composite value (each array item, JSONB key/value, or lexeme) with a posting list of rows containing it, so "which rows contain X" is fast - but one row with 50 tags produces 50 index entries.

### The write amplification penalty

Every index must be maintained on every write:

- An `INSERT` into a table with 10 indexes writes the heap row **plus 10 index entries**, each also written to the WAL and shipped to replicas.
- An `UPDATE` in PostgreSQL normally creates a new row version and new index entries in _every_ index - unless it is a **HOT (heap-only tuple) update**, which is possible only when no indexed column changes and the page has free space. Indexing a frequently updated column disables HOT for that table's updates.
- GIN is especially expensive to update; PostgreSQL mitigates this with a pending list (`fastupdate`), which makes inserts cheaper but some reads slower until the list is merged by vacuum.

Over-indexing therefore costs write throughput, WAL volume, replication lag, vacuum work, and buffer-cache memory. Indexes that are never used are pure cost.

### Practical rules

- Index to match real query predicates and sort order; in a composite index, put equality columns first, then the range or sort column.
- Use **covering indexes** (`INCLUDE`) to enable index-only scans, and **partial indexes** (`WHERE status = 'open'`) when queries target a small subset.
- A function or type cast on the column (`WHERE lower(email) = ...`) prevents index use unless you create an expression index.
- Build indexes on live tables with `CREATE INDEX CONCURRENTLY`, and audit for unused ones regularly.

## Example

```sql
-- B-tree matching filter + sort; GIN for JSONB containment.
CREATE INDEX CONCURRENTLY idx_orders_customer_created ON orders (customer_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_events_payload ON events USING gin (payload jsonb_path_ops);

EXPLAIN (ANALYZE, BUFFERS)
SELECT id FROM events WHERE payload @> '{"status": "active"}';
-- Bitmap Index Scan on idx_events_payload   <- GIN used

-- Find indexes that are never scanned but still paid for on every write.
SELECT relname, indexrelname, idx_scan, pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
-- Check replicas too before dropping: these statistics are per server.
```

## Interview tips

- Explain the structures, not just the names: B-tree is sorted and supports ranges; GIN is inverted and supports "contains".
- Quantify write amplification - one write becomes N index writes plus WAL - and mention HOT updates as the PostgreSQL-specific nuance.
- Name partial, covering, and expression indexes as the tools that keep index count down.
- Say you would find unused indexes with `pg_stat_user_indexes`, and check every replica before dropping one.
- "Add an index" without the write cost is a junior answer; the trade-off is what the question is testing.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[How does Docker BuildKit work and what caching and build features does it unlock?]] (`#515`): [How does Docker BuildKit work and what caching and build features does it unlock?](../docker/how-does-docker-buildkit-work-and-what-caching-and-build-features-does-it-unlock.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
