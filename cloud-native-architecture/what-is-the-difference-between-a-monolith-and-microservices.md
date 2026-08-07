---
title: "What is the difference between a monolith and microservices?"
id: 280
category: "Cloud Native Architecture"
difficulty: "Beginner"
tags:
  - devops
  - cloud-native-architecture
  - interview-questions
---

# What is the difference between a monolith and microservices?

**Short answer:** A monolith is one deployable unit containing all the application's functionality; microservices split that functionality into many independently deployable services that talk over the network. The real difference is not code size - it is **the unit of deployment**, and therefore who can ship without coordinating with whom.

## Detail

**The monolith.** One codebase, one build, one artifact, one deploy. Modules call each other in-process, so calls are fast and reliable, refactoring across boundaries is easy, and a single database transaction can span the whole request. You scale it by running more copies of the whole thing.

**Microservices.** Each service owns its code, its data, and its release schedule. Team A deploys checkout at 2pm without asking team B about search. Services communicate over HTTP/gRPC or through a message broker, which means every previously in-process call is now a network call that can be slow, fail, or arrive twice.

**What actually changes:**

| Dimension  | Monolith                              | Microservices                                           |
| ---------- | ------------------------------------- | ------------------------------------------------------- |
| Deploy     | One artifact, all-or-nothing          | Independent per service                                 |
| Scaling    | Scale the whole app                   | Scale only the hot service                              |
| Failure    | A bad module can take down everything | Blast radius is one service, if you designed for it     |
| Data       | One schema, real transactions         | A database per service, eventual consistency            |
| Debugging  | A stack trace                         | Distributed tracing across many hops                    |
| Team model | Coordinated releases                  | Autonomous teams, independent roadmaps                  |
| Operations | One thing to run                      | Service discovery, retries, mTLS, per-service pipelines |

**Microservices are an organisational solution before they are a technical one.** They exist to let many teams ship independently. Below roughly three teams, the coordination problem they solve barely exists, and you pay the operational cost for nothing. This is why the common recommendation is to start with a **modular monolith** - one deployable, but strict internal module boundaries with no cross-module database access - and extract a service when a specific pressure appears: a component with wildly different scaling needs, a team blocked by another team's release cadence, or a piece that needs a different language or compliance boundary.

**The tax nobody mentions in the design review.** A network between two modules means timeouts, retries, idempotency, circuit breakers, and versioned contracts. A database per service means no cross-service joins and no cross-service transactions - you need sagas or outbox patterns instead. Local development needs mocks or a way to run a subset. And a "distributed monolith", where services are separate but must all deploy together because their contracts are entangled, is worse than either option: all the network cost with none of the autonomy.

**Where DevOps sits in this.** Microservices only work on top of platform investment: containers and an orchestrator, automated per-service pipelines, centralised logs, metrics and traces, service discovery, and a paved road so a new service does not take three weeks of setup. If that platform does not exist, splitting the monolith moves the problem into the network where it is harder to see.

## Example

```text
Monolith                              Microservices
┌────────────────────────────┐        ┌─────────┐  ┌─────────┐  ┌──────────┐
│  orders │ payments │ users │        │ orders  │→ │ payments│→ │  users   │
│  ────────────────────────  │        └────┬────┘  └────┬────┘  └────┬─────┘
│        one process         │             │            │            │
└────────────┬───────────────┘          ┌──▼──┐      ┌──▼──┐      ┌──▼──┐
             │                          │ db  │      │ db  │      │ db  │
        ┌────▼────┐                     └─────┘      └─────┘      └─────┘
        │ one db  │                    in-process call → network call
        └─────────┘                    transaction     → saga / outbox
```

```python
# In a monolith, this is one transaction and it either happens or it does not.
with db.transaction():
    order = orders.create(user_id, items)
    payments.charge(order.id, order.total)      # same process, same transaction

# Split across services, the same intent needs a durable step and a compensation.
order = orders.create(user_id, items)           # local transaction + outbox row
publish("order.created", {"order_id": order.id, "total": order.total})
# payments consumes it, charges idempotently by order_id, and emits
# payment.succeeded or payment.failed - which orders must handle by cancelling.
```

## Interview tips

- Define the difference as the unit of deployment, not as "small services". That reframing is what interviewers are listening for.
- Say microservices solve a team-coordination problem. Reaching for them with two teams and no platform is the mistake they want you to avoid.
- Recommend the modular monolith as a starting point, and name a concrete trigger for extraction (different scaling profile, blocked release cadence, compliance boundary).
- Name the tax explicitly: network failures, eventual consistency, distributed tracing, per-service pipelines.
- Know the phrase "distributed monolith" and why it is the worst outcome - services that cannot deploy independently.
- If your experience is only monoliths, say so and describe where you would draw the first boundary and why. That answers better than pretending.

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
