---
title: "How does the Saga pattern manage distributed transactions across microservices without two-phase commit (2PC)?"
id: 604
category: "Cloud Native Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - microservices
  - saga-pattern
  - distributed-transactions
  - consistency
quiz:
  stem: "What is the role of a 'Compensating Transaction' in the distributed Saga pattern?"
  options:
    - "To calculate employee annual financial bonuses"
    - "To explicitly undo the business effects of previously committed local transactions when a downstream step in the saga fails"
    - "To encrypt all database tables during transmission"
    - "To convert SQL queries into NoSQL JSON documents"
  answer: 2
  explanation: "Since Sagas do not use distributed locks and commit each local step immediately, failure at step 4 requires executing compensating transactions to undo the business changes of steps 1, 2, and 3."
---

# How does the Saga pattern manage distributed transactions across microservices without two-phase commit (2PC)?

**Short answer:** A saga replaces one distributed transaction with a sequence of **local** transactions, one per service, each committed immediately. If a later step fails, the saga runs **compensating transactions** for the steps already completed - cancel the hotel, refund the card - to restore business consistency. Steps are coordinated either by an **orchestrator** (a workflow engine such as Temporal, AWS Step Functions, or Camunda that tells each service what to do) or by **choreography** (services reacting to each other's events). The trade-off is that you give up isolation: other requests can see intermediate states, so the design must tolerate them.

## Detail

**Why not 2PC.** Two-phase commit holds locks across every participant until a coordinator decides, so latency and availability are bounded by the slowest and least available participant, a coordinator failure can leave participants blocked, and most managed databases, queues, and third-party APIs do not support XA at all. Sagas trade atomicity and isolation for availability and loose coupling.

**A worked flow - booking a trip**

```text
T1 Book flight      ✔  (compensation C1: cancel flight)
T2 Reserve hotel    ✔  (compensation C2: release hotel)
T3 Charge card      ✔  (compensation C3: refund)          <- pivot: after this, only go forward
T4 Book car         ✘  no cars
   -> run C3? No - T3 was the pivot; retry T4 or offer an alternative (forward recovery)
   If T3 had failed instead: run C2, then C1 (backward recovery, reverse order)
```

**Rules that make sagas work**

- **Compensations are semantic, not rollbacks.** You cannot un-send an email; you send a correction. Some steps (a card charge) are only compensable by a new action (a refund) with its own fees and visibility.
- **Every step and compensation is idempotent**, because retries and duplicate messages are guaranteed.
- **Compensations must eventually succeed** - retry with backoff, and escalate to a human queue if they cannot.
- **Order steps by risk**: put steps most likely to fail first and irreversible steps (the pivot) as late as possible.
- **Publish reliably**: each local transaction and its outgoing event/command must be atomic, which is what the **transactional outbox** pattern provides.
- **Handle the missing isolation**: use semantic locks (a `PENDING` status other requests respect), commutative updates, or re-reading values before acting, because a concurrent request can see the flight booked before the saga completes.

**Orchestration versus choreography.** An orchestrator makes the flow explicit, stores its state durably, handles timeouts and compensation centrally, and is easy to observe - the usual choice for more than three or four steps. Choreography avoids a central component but spreads the flow across services and becomes hard to reason about as it grows.

## Example

```python
# Orchestrated saga with Temporal (Python SDK): each step is an activity with retries;
# compensations are registered as steps succeed and run in reverse on failure.
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

@workflow.defn
class BookTrip:
    @workflow.run
    async def run(self, trip: dict) -> str:
        opts = dict(start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(maximum_attempts=5))
        compensations = []
        try:
            await workflow.execute_activity("book_flight", trip, **opts)
            compensations.append("cancel_flight")
            await workflow.execute_activity("reserve_hotel", trip, **opts)
            compensations.append("release_hotel")
            await workflow.execute_activity("book_car", trip, **opts)
            return "confirmed"
        except Exception:
            for step in reversed(compensations):          # backward recovery
                await workflow.execute_activity(step, trip, **opts)
            raise
```

## Interview tips

- Start with why 2PC does not fit: blocking locks across services, coordinator failure, and no XA support in most cloud services.
- Explain compensations as business-level undo, idempotent and retried until they succeed.
- Mention the pivot transaction and forward versus backward recovery; it shows you have designed one.
- Name the lost isolation and how you handle it (semantic locks, pending states), and the outbox for reliable event publishing.
- Choose orchestration for complex flows because state, timeouts, and compensation live in one visible place.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[How do you take a monthly release process to daily deployments?]] (`#285`): [How do you take a monthly release process to daily deployments?](../core-devops-concepts/how-do-you-take-a-monthly-release-process-to-daily-deployments.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
