---
title: "What is Database Sharding and what are the trade-offs of Range, Hash, and Directory-based sharding?"
id: 665
category: "Database Management in DevOps"
difficulty: "Advanced"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - databases
  - sharding
  - horizontal-scaling
  - partitioning
quiz:
  stem: "What is a major limitation of Hash-Based database sharding when executing queries that span numeric ranges (e.g. `WHERE id BETWEEN 50 AND 100`)?"
  options:
    - "The database engine refuses to execute the query"
    - "The query cannot be localized to a single shard and must scatter-gather query every database shard in the cluster"
    - "Hash sharding permanently corrupts primary keys"
    - "Hash sharding only supports string data types"
  answer: 2
  explanation: "Because hash functions scatter consecutive numbers across random shards, range queries cannot target one server and must broadcast across all shards, increasing latency."
---

# What is Database Sharding and what are the trade-offs of Range, Hash, and Directory-based sharding?

**Short answer:** Sharding partitions data horizontally across independent database instances; Range sharding divides data by value intervals (risking hotspots); Hash sharding distributes rows uniformly using mathematical hash functions; Directory-based sharding uses a lookup service for dynamic mapping.

## Detail

When a single database exhausts vertical scaling - or the write rate, data size, or blast radius of one instance becomes unacceptable - sharding splits rows across independent database instances by a **shard key**. Each shard holds a subset of the data and handles its share of reads and writes.

### Sharding strategies

1. **Range-based sharding**
   - Shard 1 holds user IDs 1-1,000,000; shard 2 holds 1,000,001-2,000,000; and so on.
   - **Pros**: range scans on the shard key stay on one shard; splitting a range is conceptually simple.
   - **Cons**: **hotspots**. With a monotonically increasing key (auto-increment ID, timestamp), all new writes land on the last shard while older shards sit idle.
2. **Hash-based sharding**
   - `shard = hash(user_id) mod number_of_shards`, or better, hashing into many fixed buckets/slots that are assigned to shards.
   - **Pros**: even distribution of data and writes.
   - **Cons**: range queries on the key (`WHERE id BETWEEN 50 AND 100`) must scatter-gather across every shard. With naive `mod N`, adding a shard remaps almost every row - which is why real systems use consistent hashing or a fixed large number of virtual buckets that move between shards.
3. **Directory-based sharding**
   - A lookup service maps each key (often tenant ID) to a shard.
   - **Pros**: maximum flexibility - move a large tenant to dedicated hardware, rebalance one tenant at a time.
   - **Cons**: the directory is on every request's path, so it must be highly available and heavily cached, or it becomes the bottleneck and single point of failure.

### Choosing the shard key

The shard key matters more than the strategy. A good key has high cardinality, spreads writes evenly, and is present in almost every query so requests route to one shard. In multi-tenant SaaS, `tenant_id` is the usual choice because it also keeps each tenant's joins and transactions on one shard.

### The costs of sharding

- **Cross-shard joins and transactions** become application problems (or need distributed transactions and sagas).
- **Global uniqueness and secondary indexes** no longer come for free - IDs need a scheme such as UUIDv7 or Snowflake-style IDs, and lookups by a non-shard-key column scatter.
- **Resharding** - moving data while serving traffic - is the hardest operational task and needs tooling.
- **Operations multiply**: backups, migrations, and monitoring now run N times, and a schema change must roll out across all shards.

Because of this, exhaust cheaper options first: query and index tuning, read replicas, caching, table partitioning within one instance, and splitting unrelated domains into separate databases. When sharding is necessary, prefer a system that manages it - Vitess (MySQL), Citus (PostgreSQL), MongoDB sharded clusters, or distributed SQL such as CockroachDB, YugabyteDB, or Spanner - over hand-rolled routing.

## Example

```sql
-- Citus (PostgreSQL extension): hash-distribute by tenant, co-locate related tables
-- so a tenant's joins and transactions stay on one worker.
CREATE EXTENSION citus;
SELECT create_distributed_table('accounts', 'tenant_id');
SELECT create_distributed_table('orders',   'tenant_id', colocate_with => 'accounts');

-- Single-shard query: routed to one worker because it filters on the shard key.
SELECT * FROM orders WHERE tenant_id = 42 AND status = 'open';

-- Scatter-gather: no shard key, so every worker is queried and results merged.
SELECT count(*) FROM orders WHERE created_at > now() - interval '1 day';
```

## Interview tips

- Say what sharding costs before you recommend it, and list the cheaper alternatives you would try first.
- Give each strategy's failure mode: range → hotspots on sequential keys, hash → scatter-gather ranges and painful resharding with `mod N`, directory → a critical lookup service.
- Spend time on the shard key - cardinality, even writes, and being present in most queries.
- Mention consistent hashing or fixed virtual buckets as the fix for resharding.
- Name managed options (Vitess, Citus, MongoDB, distributed SQL) - hand-rolled sharding is rarely the right call today.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
