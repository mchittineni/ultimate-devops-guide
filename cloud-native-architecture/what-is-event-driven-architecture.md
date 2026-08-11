---
title: "What is Event-Driven Architecture?"
id: 69
category: "Cloud Native Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-native-architecture
  - interview-questions
---

# What is Event-Driven Architecture?

**Short answer:** Event-driven architecture structures a system around the production, detection, and consumption of events, so producers emit facts about what happened and consumers react independently, without the producer knowing who is listening.

## Detail

**Core idea.** Instead of service A calling service B and waiting, A publishes `OrderPlaced` to a broker. Inventory, payments, and notifications each consume it independently. A does not know they exist and does not fail if one of them is down.

**Patterns**

- **Publish/subscribe** - events broadcast to any number of subscribers.
- **Event streaming** - a durable, replayable log (Kafka, Kinesis, Pub/Sub) where consumers track their own offset and can reprocess history.
- **Event sourcing** - the sequence of events _is_ the source of truth; current state is derived by replaying them.
- **CQRS** - separate write and read models, typically synchronised by events.
- **Outbox pattern** - write the event to a table in the same transaction as the state change, then relay it, eliminating the dual-write problem.

**Benefits:** loose coupling, independent scaling, natural resilience (the broker buffers while a consumer is down), replayability, and easy addition of new consumers.

**Costs:** eventual consistency, harder end-to-end debugging, message ordering and duplicate handling (consumers must be idempotent), schema evolution across producers and consumers, and the operational weight of the broker itself.

**Delivery semantics** matter: at-most-once, at-least-once (the common default - so design idempotent consumers), and effectively-once, which requires deduplication or transactional processing.

## Example

```json
{
  "eventId": "8f2b...",
  "eventType": "OrderPlaced",
  "version": "1.0",
  "occurredAt": "2026-03-14T10:32:11Z",
  "traceId": "b7e1...",
  "data": {
    "orderId": "A-1042",
    "customerId": "C-88",
    "totalMinor": 4599,
    "currency": "GBP"
  }
}
```

## Interview tips

- Idempotent consumers is the answer to at-least-once delivery - raise it before you are asked.
- The outbox pattern is the standard solution to "how do you avoid updating the database and failing to publish?"
- Mention schema registries and versioning; event contracts break teams silently otherwise.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
