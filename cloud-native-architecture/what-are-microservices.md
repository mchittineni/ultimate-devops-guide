---
title: "What are Microservices?"
id: 67
category: "Cloud Native Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-native-architecture
  - interview-questions
---

# What are Microservices?

**Short answer:** Microservices are an architectural style that structures an application as a set of small, independently deployable services, each owning a single business capability and its own data, communicating over the network.

## Detail

**Defining characteristics**

- **Single business capability** per service, aligned to a domain boundary rather than a technical layer.
- **Independent deployability** - the whole point. If two services must be released together, they are one service.
- **Decentralised data** - each service owns its datastore. Shared databases recreate the coupling you were escaping.
- **Independent scaling** - scale only the part under load.
- **Technology heterogeneity** - each service can pick its language and store, within reason.
- **Team ownership** - one team owns a service end to end, including on-call.

**Communication.** Synchronous (REST, gRPC) is simple but propagates latency and failure. Asynchronous events (Kafka, Pub/Sub, SQS) decouple services and improve resilience, at the cost of eventual consistency and harder debugging.

**The costs are real.** Distributed transactions become sagas. Debugging requires distributed tracing. Local development needs stubs or a shared environment. Network calls fail in ways in-process calls do not. Operational surface multiplies - every service needs a pipeline, dashboards, alerts, and an owner.

**The usual advice** - and the answer interviewers want - is to start with a modular monolith, learn the true domain boundaries, and extract services where independent deployment or scaling genuinely pays. Splitting a domain you do not yet understand produces a distributed monolith: all the complexity, none of the independence.

## Example

```text
One business capability, owned end to end - what "a microservice" means in practice

  service:      orders
  owns:         orders schema (PostgreSQL) - no other service has credentials
  exposes:      REST /v1/orders (OpenAPI spec in repo), event OrderPlaced v2 (schema registry)
  consumes:     PaymentCaptured, PaymentFailed (idempotent handlers, keyed by order_id)
  deploys:      its own pipeline; canary 5% -> 100%; no release train with other services
  resilience:   2 s timeout + 1 jittered retry to payments; circuit breaker; outbox for events
  runs:         3-20 replicas (HPA on CPU and queue lag); readiness probe on /ready
  observes:     RED metrics, traces via OpenTelemetry, SLO 99.9% on POST /v1/orders
  on-call:      orders team rotation - the team that ships it is paged for it
```

## Interview tips

- Independent deployability is the acid test; state it as the definition.
- Name the anti-pattern by name: distributed monolith, and the shared database that causes it.
- Discuss data consistency - sagas, outbox pattern, idempotency - to show you have run this in production.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
