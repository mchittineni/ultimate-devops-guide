---
title: "What is Database per Service pattern and how do you handle cross-service queries and joins?"
id: 608
category: "Cloud Native Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - microservices
  - database-per-service
  - data-management
  - cqrs
quiz:
  stem: "Why does the 'Database per Service' microservice pattern strictly forbid services from accessing another service's database directly?"
  options:
    - "Cloud databases charge licensing fees per connected microservice"
    - "Direct database access tightly couples internal table schemas, prevents autonomous deployments, and risks database lock contention"
    - "Database engines cannot handle more than one username"
    - "It violates basic Linux network routing rules"
  answer: 2
  explanation: "If Service B queries Service A's database directly, Service A cannot alter its internal schema without breaking Service B, completely undermining the independence of microservice deployments."
---

# What is Database per Service pattern and how do you handle cross-service queries and joins?

**Short answer:** Each service owns its data and is the only thing allowed to read or write its schema; everyone else goes through its API or its published events. That keeps schemas private, so a service can change or migrate its storage without coordinating releases. The price is that cross-service joins and transactions disappear, and you replace them with **API composition** (query each owner and join in memory), **replicated read models** (subscribe to events or CDC and keep a local, denormalised copy), or an **analytics store** fed by CDC for reporting - each trading freshness, latency, and complexity differently.

## Detail

**What "owns" means.** Not necessarily a separate database server - a private schema or set of tables with credentials only that service holds is enough. The rule is about access, not infrastructure. Shared tables are the most common cause of a distributed monolith: a column rename in one team's service breaks another team's release.

**Replacing the join**

| Approach                | How it works                                                                           | Freshness                       | Costs                                                                              |
| ----------------------- | -------------------------------------------------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------- |
| API composition         | A composer (BFF, gateway, GraphQL federation) calls each owner and joins results       | Real-time                       | Latency and availability of every owner; N+1 unless the API supports batch lookups |
| Replicated read model   | Service subscribes to `CustomerUpdated` events (or CDC) and stores the fields it needs | Eventually consistent (seconds) | Duplicate data, event contracts, backfill and replay handling                      |
| Dedicated query service | A separate CQRS read service builds a joined view from several services' events        | Eventually consistent           | Another service to own; the most flexible for complex queries                      |
| Analytics / lakehouse   | CDC (Debezium, managed CDC) into a warehouse where arbitrary SQL joins run             | Minutes                         | Not for user-facing requests; governance of copied data                            |

**Replacing the transaction.** Use a saga with compensations for multi-service business operations, and the **transactional outbox** so a service's state change and the event announcing it are committed atomically.

**Choosing the service boundary is the real fix.** If two services constantly need each other's data in the same request, the boundary is probably wrong; merging them is often better than building elaborate replication.

**Operational consequences:** more databases to back up, patch, and monitor (platform automation helps), consistent identifiers across services, and clear ownership of reference data that many services need.

## Example

```python
# Replicated read model: orders keeps the customer fields it displays, updated from events.
# Idempotent upsert keyed by customer id, guarded by the event's version.
def on_customer_updated(event: dict) -> None:
    c = event["data"]
    db.execute(
        """
        INSERT INTO customer_view (customer_id, name, tier, version)
        VALUES (%(id)s, %(name)s, %(tier)s, %(version)s)
        ON CONFLICT (customer_id) DO UPDATE
          SET name = EXCLUDED.name, tier = EXCLUDED.tier, version = EXCLUDED.version
          WHERE customer_view.version < EXCLUDED.version     -- ignore stale or duplicate events
        """,
        c,
    )

# The former cross-service join is now a local query
ORDERS_WITH_CUSTOMER = """
SELECT o.order_id, o.total, cv.name, cv.tier
FROM orders o JOIN customer_view cv ON cv.customer_id = o.customer_id
WHERE o.created_at > now() - interval '7 days';
"""
```

## Interview tips

- Define ownership as exclusive access to a schema, not necessarily a separate server.
- Offer the three replacements for joins - composition, replicated read models, analytics via CDC - with their freshness and latency trade-offs.
- Mention the outbox and sagas for the write side, and idempotent, version-guarded event consumers.
- Say that constant cross-service joins are a signal the boundary is wrong.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
