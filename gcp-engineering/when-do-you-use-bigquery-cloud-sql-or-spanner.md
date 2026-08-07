---
title: "When do you use BigQuery, Cloud SQL, or Spanner?"
id: 214
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - gcp-engineering
  - interview-questions
---

# When do you use BigQuery, Cloud SQL, or Spanner?

**Short answer:** Cloud SQL is managed PostgreSQL/MySQL/SQL Server for ordinary transactional workloads that fit on one primary. Spanner is a horizontally scalable, strongly consistent relational database for workloads that outgrow a single writer or need multi-region writes. BigQuery is an analytical warehouse - columnar, separated storage and compute, priced per query or per slot - and is not a transactional database.

## Detail

| Need                                                              | Choose    | Why                                             |
| ----------------------------------------------------------------- | --------- | ----------------------------------------------- |
| Standard OLTP, familiar engine, < ~64 TB                          | Cloud SQL | cheapest, standard SQL, easy migration          |
| Global writes, > single-node throughput, 99.999% multi-region SLA | Spanner   | horizontal scale with strong consistency        |
| Aggregations over billions of rows                                | BigQuery  | columnar scan, elastic compute                  |
| Key-value at massive scale, time series                           | Bigtable  | not relational, but the honest answer sometimes |
| Document model, mobile sync                                       | Firestore | per-document consistency, offline clients       |

**Cloud SQL's ceiling is a single writer.** Read replicas scale reads; write throughput does not scale horizontally. High availability is a regional standby with failover in the tens of seconds, so applications still need retry and connection handling. Cloud SQL Enterprise Plus raises the performance and HA ceiling, and Cloud SQL Auth Proxy or Private Service Connect keeps access private. Plan for maintenance windows - managed does not mean invisible.

**Spanner's price is design discipline.** You get horizontal scale with external consistency (TrueTime), but schema and key design decide whether you succeed: monotonically increasing keys create hotspots, so use UUIDs or bit-reversed sequences; interleaved tables co-locate parent and child rows for efficient joins. It is not a drop-in PostgreSQL replacement even with the PostgreSQL interface, and its cost floor is much higher than Cloud SQL's - choose it for a scale or consistency requirement you can name.

**BigQuery is analytics, not OLTP.** No indexes or point updates in the transactional sense; partitioning and clustering are how you keep scans small. Cost control is the operational discipline: always filter on the partition column, avoid `SELECT *`, set custom quotas per project, and choose between on-demand (per TB scanned) and capacity/slot reservations once volume is predictable. Materialised views and BI Engine handle repeated dashboard queries.

**Analytics without a pipeline.** BigQuery federated queries and Datastream let you analyse Cloud SQL data without building ETL, and change streams from Spanner or CDC into BigQuery is the standard pattern for near-real-time analytics. The interview point is that "which database" is usually answered as "an OLTP store plus a warehouse, with CDC between them" rather than one system doing both.

**Operational realities to mention:** point-in-time recovery and tested restores in Cloud SQL; backup and export policies in BigQuery (a dropped table is recoverable only within the time-travel window, seven days by default); and IAM at dataset/table/column level plus policy tags for column-level security in BigQuery, which is how regulated data is handled.

## Example

```sql
-- BigQuery: partition and cluster so queries scan a fraction of the table
CREATE TABLE analytics.orders (
  order_id STRING NOT NULL,
  customer_id STRING,
  country STRING,
  amount NUMERIC,
  created_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY country, customer_id
OPTIONS (
  partition_expiration_days = 1095,
  require_partition_filter = TRUE  -- forces every query to bound the scan
);
```

```sql
-- Spanner: avoid a hotspot by not using a monotonically increasing key,
-- and interleave the child table for co-located joins
CREATE TABLE Customers (
  CustomerId STRING(36) NOT NULL,  -- UUID, spreads writes across splits
  Name       STRING(MAX),
) PRIMARY KEY (CustomerId);

CREATE TABLE Orders (
  CustomerId STRING(36) NOT NULL,
  OrderId    STRING(36) NOT NULL,
  Amount     NUMERIC,
) PRIMARY KEY (CustomerId, OrderId),
  INTERLEAVE IN PARENT Customers ON DELETE CASCADE;
```

## Interview tips

- Answer by requirement - single-writer OLTP, global consistency, or analytical scan - rather than listing products.
- `require_partition_filter` and the Spanner hotspot point are the two details that show production experience.
- Expect: "why not BigQuery for the application database?" - no point lookups at OLTP latency or cost, and no transactional semantics for that pattern.

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
