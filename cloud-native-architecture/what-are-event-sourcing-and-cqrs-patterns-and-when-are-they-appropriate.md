---
title: "What are Event Sourcing and CQRS patterns and when are they appropriate?"
id: 607
category: "Cloud Native Architecture"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - event-sourcing
  - cqrs
  - architecture
  - kafka
  - event-driven
quiz:
  stem: "In an Event Sourced banking architecture, how is a customer's current account balance determined?"
  options:
    - "By querying a single mutable `balance` column in a SQL table"
    - "By replaying the immutable historical sequence of deposit and withdrawal events from the event store"
    - "By guessing based on the customer's average monthly income"
    - "By reading the browser's local storage cache"
  answer: 2
  explanation: "Event sourcing stores all state modifications as an append-only stream of facts. Current state is reconstructed by replaying the historical sequence of events from genesis or a snapshot."
---

# What are Event Sourcing and CQRS patterns and when are they appropriate?

**Short answer:** **Event sourcing** stores every state change as an immutable, append-only event (`FundsDeposited`, `FundsWithdrawn`) and derives current state by replaying them, usually from a snapshot. **CQRS** (Command Query Responsibility Segregation) separates the model that handles writes from the models that serve reads, so each can be shaped and scaled for its job; read models are often projections built from the event stream. They fit domains that need a full audit history, temporal queries, or very different read and write shapes - finance, logistics, booking. For ordinary CRUD they add eventual consistency, schema-evolution work, and operational weight that is rarely repaid.

## Detail

**Event sourcing**

- The event store holds ordered streams per aggregate (for example one stream per account): `AccountOpened`, `FundsDeposited { amount: 150 }`, `FundsWithdrawn { amount: 50 }`.
- A command is validated against the current state (rebuilt from the stream), and if accepted, new events are appended with an **expected version** - optimistic concurrency that rejects the write if someone else appended first.
- **Snapshots** cap replay cost for long streams.
- Benefits: a complete audit log by construction, "what was the state on 1 June?" queries, the ability to build new read models by replaying history, and debugging by replay.
- Costs: events are a permanent contract, so **schema evolution** (versioned events, upcasters) is ongoing work; deleting personal data conflicts with immutability (crypto-shredding - encrypting per-subject data and destroying the key - is the usual answer); and querying current state requires projections.

**CQRS**

- **Write side** - accepts commands, enforces invariants, emits events (or writes a normalised store).
- **Read side** - one or more denormalised projections optimised per query: a relational table for reports, a search index (OpenSearch or Elasticsearch) for full-text, a key-value store for hot lookups.
- Projections are updated asynchronously, so reads are **eventually consistent**; the UI must handle "I just saved it and it is not in the list yet" (read-your-own-writes via the command response, or waiting for the projection version).
- CQRS does not require event sourcing - a normal database plus change data capture into read models is CQRS too.

**When to use them.** Use event sourcing where history _is_ the business (ledgers, order lifecycles, compliance audits); use CQRS where read and write loads or shapes differ sharply. Apply them to the bounded contexts that need them, not the whole system.

**Tooling:** EventStoreDB (now KurrentDB), Axon, Marten on PostgreSQL, or a relational table with an append-only design; Kafka is often used to distribute events to projections, but its topics are a poor primary event store for per-aggregate streams with optimistic concurrency.

## Example

```sql
-- A minimal event store on PostgreSQL with optimistic concurrency per stream
CREATE TABLE events (
  stream_id   text        NOT NULL,
  version     int         NOT NULL,
  type        text        NOT NULL,
  data        jsonb       NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (stream_id, version)      -- a second writer at the same version fails
);

-- Append: the command handler read the stream at version 2, so it writes version 3
INSERT INTO events (stream_id, version, type, data)
VALUES ('account-1', 3, 'FundsWithdrawn', '{"amount": 50}');

-- Rebuild current state (in practice: latest snapshot + later events)
SELECT sum(CASE type WHEN 'FundsDeposited' THEN (data->>'amount')::numeric
                     WHEN 'FundsWithdrawn' THEN -(data->>'amount')::numeric
                     ELSE 0 END) AS balance
FROM events WHERE stream_id = 'account-1';
```

## Interview tips

- Define both separately and say that CQRS does not require event sourcing.
- Mention optimistic concurrency on append and snapshots - they show you know how the write path actually works.
- Name the real costs: eventual consistency in the UI, event schema evolution, and the tension with data-deletion obligations.
- Recommend applying them per bounded context where history or read/write asymmetry justifies it, not across a CRUD application.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
