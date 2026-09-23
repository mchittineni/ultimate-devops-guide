---
title: "What is Change Data Capture (CDC) and how does Debezium stream database changes into event architectures?"
id: 666
category: "Database Management in DevOps"
difficulty: "Intermediate"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - databases
  - cdc
  - debezium
  - kafka
  - event-driven
quiz:
  stem: "Why is Change Data Capture (CDC via Debezium) superior to periodic polling queries (`SELECT ... WHERE updated_at > ...`) for syncing databases to Elasticsearch?"
  options:
    - "Polling queries can only run on weekends"
    - "CDC reads transaction logs directly, capturing hard row deletions and intermediate state transitions in real time with near-zero database load"
    - "CDC eliminates the need for Apache Kafka"
    - "Polling queries automatically lock the entire database"
  answer: 2
  explanation: "Polling cannot detect rows that were deleted (since they no longer exist to be queried) and misses rapid intermediate state updates. CDC reads the commit log directly."
---

# What is Change Data Capture (CDC) and how does Debezium stream database changes into event architectures?

**Short answer:** Change Data Capture (CDC) reads database transaction logs directly (PostgreSQL WAL, MySQL binlog) to stream row-level insert, update, and delete events into Apache Kafka in real-time, enabling asynchronous event-driven pipelines without polling databases.

## Detail

Historically, extracting data to a search engine (Elasticsearch/OpenSearch) or a warehouse (Snowflake, BigQuery) meant periodic queries:

```sql
SELECT * FROM users WHERE updated_at > :last_poll_time;
```

Polling has three structural flaws: it adds query load to the primary on every cycle, it misses intermediate states (a row updated twice between polls is seen once), and it **cannot see hard `DELETE`s** - the row is gone. It also depends on every writer maintaining `updated_at` correctly.

### How Debezium CDC works

1. **It reads the database's own change log**, through the replication interface the database already provides: PostgreSQL logical decoding (the built-in `pgoutput` plugin, via a publication and a replication slot), the MySQL/MariaDB binlog in `ROW` format, SQL Server CDC tables, Oracle LogMiner, MongoDB change streams.
2. **It takes an initial snapshot**, then switches to streaming from the log position it recorded, so consumers get a complete, ordered history. Incremental snapshots can re-snapshot a table later without stopping the stream.
3. **It emits one event per row change** with `before` and `after` images, the operation (`c`, `u`, `d`, `r` for snapshot reads), and source metadata such as the LSN or binlog position and the transaction ID.
4. **It usually runs on Kafka Connect**, writing one topic per table and storing its log offsets so it resumes exactly where it stopped. Debezium Server can instead deliver to Kinesis, Pub/Sub, Pulsar, Redis Streams, and others, and Debezium can also be embedded as a library.

```json
{
  "op": "u",
  "before": { "id": 101, "status": "pending" },
  "after": { "id": 101, "status": "shipped" },
  "source": { "connector": "postgresql", "table": "orders", "lsn": 24023128 },
  "ts_ms": 1727123456789
}
```

### The outbox pattern

Writing to the database and publishing to Kafka from application code is a dual write: one can succeed while the other fails. Instead, the application writes the business row and an event row into an `outbox` table **in the same local transaction**. Debezium streams the outbox table, and its outbox event router turns each row into a message on the right topic. Consistency comes from the database transaction; no two-phase commit is needed.

### Operational trade-offs

- **Replication slots retain WAL.** If the connector is down or slow, the PostgreSQL slot holds WAL indefinitely and can fill the primary's disk. Monitor slot lag and set `max_slot_wal_keep_size` as a safety valve (at the cost of forcing a re-snapshot if it is exceeded).
- **Delivery is at-least-once.** Consumers must be idempotent (upsert by key, or dedupe on the source position).
- **Schema changes flow downstream.** A column rename breaks consumers; use a schema registry with compatibility rules, and treat CDC topics as a contract - or publish curated outbox events instead of raw table changes.
- **Failover needs care.** Logical slots historically did not survive a primary failover; PostgreSQL 17 added failover slot synchronisation, and managed services each have their own rules - check before relying on it.
- Latency is typically sub-second, but it is not "zero load": log reading and decoding cost CPU and I/O on the source.

## Example

```json
{
  "name": "orders-cdc",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "plugin.name": "pgoutput",
    "database.hostname": "orders-db.internal",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${file:/secrets/db.properties:password}",
    "database.dbname": "orders",
    "topic.prefix": "orders",
    "table.include.list": "public.orders,public.outbox",
    "slot.name": "debezium_orders",
    "publication.autocreate.mode": "filtered",
    "snapshot.mode": "initial"
  }
}
```

```bash
# Register the connector with Kafka Connect, then watch the slot so WAL cannot pile up.
curl -s -X POST -H 'Content-Type: application/json' \
  --data @orders-cdc.json http://connect:8083/connectors
psql -c "SELECT slot_name, active,
         pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS lag
         FROM pg_replication_slots;"
```

## Interview tips

- Start with why polling fails: load, missed intermediate states, and no visibility of deletes.
- Explain the mechanism: Debezium consumes the WAL/binlog through the database's replication interface, snapshots first, then streams with stored offsets.
- The outbox pattern is the highest-value point - it solves the dual-write problem with one local transaction.
- Name the operational risk: an inactive PostgreSQL replication slot retains WAL and can fill the disk.
- Mention at-least-once delivery, idempotent consumers, and schema evolution as the things that bite in production.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
