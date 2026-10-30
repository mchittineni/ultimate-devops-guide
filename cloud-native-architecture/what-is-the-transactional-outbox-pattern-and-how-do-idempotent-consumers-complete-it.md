---
title: "What is the transactional outbox pattern and how do idempotent consumers complete it?"
id: 775
category: "Cloud Native Architecture"
difficulty: "Advanced"
tags:
  - devops
  - cloud-native-architecture
  - interview-questions
  - outbox
  - event-driven
  - idempotency
---

# What is the transactional outbox pattern and how do idempotent consumers complete it?

**Short answer:** A service that must both change its database and publish an event has a **dual-write** problem: if it commits and then crashes before publishing, the event is lost; if it publishes first and the commit fails, consumers act on something that never happened. The **transactional outbox** fixes this by writing the event into an `outbox` table **in the same local transaction** as the state change, and having a separate relay (a poller or change data capture such as Debezium) publish rows from that table to the broker. The relay can publish a row more than once, so delivery is at-least-once. **Idempotent consumers** - which record processed message IDs or apply changes in a naturally idempotent way - finish the job, giving you effectively-once processing end to end.

## Detail

**Why not just publish after commit?** Nothing makes "commit the database" and "publish to Kafka/SQS" atomic. A two-phase commit across them is unavailable on most brokers and too fragile anyway. Any code ordering leaves a window where a crash, a timeout, or a deploy loses or invents an event.

**How the outbox works**

1. In one transaction, the service updates its business tables and inserts a row into `outbox` (event ID, aggregate ID, type, payload, created time).
2. A relay reads committed outbox rows and publishes them:
   - **Polling publisher**: a worker selects unpublished rows (`FOR UPDATE SKIP LOCKED` lets several workers share the load), publishes, then marks or deletes them. It is simple but adds query load and some latency.
   - **Log-tailing (CDC)**: Debezium, or DynamoDB Streams for DynamoDB, reads the database's transaction log and emits outbox inserts. It adds no polling load and keeps commit order, but it is another system to run. Debezium's outbox event router routes each row to a topic by type.
3. If the relay crashes after publishing but before marking the row, it publishes the row again on restart. That is why consumers must be idempotent.

**Ordering.** Use the aggregate ID (for example `order_id`) as the message or partition key, so all events for one entity land on the same partition or message group and stay in order. Across different entities, order is not guaranteed and should not be needed.

**Idempotent consumers (sometimes called the inbox pattern)**

- Record each processed event ID in a `processed_messages` table **in the same transaction** as the consumer's own state change. A unique-key violation means the event is a duplicate, so skip it.
- Or make the operation naturally idempotent: an upsert guarded by a version number, `SET status = 'shipped'` instead of incrementing a counter.
- Expire the dedup records after the broker's maximum redelivery window so the table does not grow forever.

**Operational details.** Delete or archive published outbox rows (or partition the table by day) so it stays small. Alert on outbox age - the oldest unpublished row - because a stuck relay shows up as nothing being published while the service itself looks healthy. Version event schemas, because the outbox payload is a public contract.

**Alternatives and their limits.** Event sourcing makes the event store the source of truth, so there is no dual write, at a much larger design cost. Kafka transactions give exactly-once only for consume-transform-produce flows _inside_ Kafka, not for a database plus Kafka. "Listen to yourself" (publish first, then update your own state from the event) works but makes the service's own reads eventually consistent.

## Example

```sql
-- 1. Producer: state change and event in ONE local transaction (PostgreSQL).
CREATE TABLE outbox (
  id           uuid PRIMARY KEY,
  aggregate_id text        NOT NULL,
  type         text        NOT NULL,
  payload      jsonb       NOT NULL,
  created_at   timestamptz NOT NULL DEFAULT now(),
  published_at timestamptz
);

BEGIN;
UPDATE orders SET status = 'PLACED' WHERE id = 'A-1042';
INSERT INTO outbox (id, aggregate_id, type, payload)
VALUES (gen_random_uuid(), 'A-1042', 'OrderPlaced', '{"orderId":"A-1042","totalMinor":4599}');
COMMIT;   -- both happen, or neither does
```

```python
# 2. Polling relay: safe to run several copies; may publish twice, never loses a row.
def relay_once(db, producer, batch=100):
    with db.transaction():
        rows = db.query(
            """SELECT id, aggregate_id, type, payload FROM outbox
               WHERE published_at IS NULL ORDER BY created_at
               LIMIT %s FOR UPDATE SKIP LOCKED""", (batch,))
        for row in rows:
            producer.send("orders", key=row.aggregate_id,          # per-entity ordering
                          value=row.payload, headers={"event-id": str(row.id)})
        producer.flush()                                            # acked before we mark
        db.execute("UPDATE outbox SET published_at = now() WHERE id = ANY(%s)",
                   ([r.id for r in rows],))

# 3. Idempotent consumer: dedup record and side effect commit together.
def handle(db, event_id: str, payload: dict):
    with db.transaction():
        inserted = db.execute(
            "INSERT INTO processed_messages (event_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (event_id,)).rowcount
        if inserted == 0:
            return                                  # duplicate delivery: already applied
        db.execute("INSERT INTO shipments (order_id) VALUES (%s)", (payload["orderId"],))
```

## Interview tips

- Name the dual-write problem first and show both failure orders (commit then crash, publish then rollback). The pattern only makes sense once that is clear.
- Explain that atomicity comes from the local transaction, and that the relay (polling or CDC with Debezium) gives at-least-once delivery.
- Say plainly that duplicates are expected, and that idempotent consumers with a dedup table in the same transaction are what make processing effectively-once.
- Mention per-aggregate keys for ordering, outbox cleanup, and an alert on the age of the oldest unpublished row.
- Know the limits of the alternatives: Kafka transactions do not cover a database write, and event sourcing is a bigger commitment.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
