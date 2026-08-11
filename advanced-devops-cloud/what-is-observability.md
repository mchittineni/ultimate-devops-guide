---
title: "What is Observability?"
id: 153
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is Observability?

**Short answer:** Observability is the property of a system that lets you understand its internal state from its external outputs - well enough to answer questions you did not anticipate when you instrumented it.

## Detail

**Monitoring vs observability.** Monitoring answers known questions with predefined dashboards and alerts: is the error rate high? Observability lets you interrogate the system freely: why are requests from this specific customer, on this API version, in this region, slow only when they include a particular parameter? Monitoring tells you _that_ something is wrong; observability lets you discover _why_, including for failure modes nobody predicted.

**The three pillars - and what actually matters**

- **Metrics** - cheap, aggregated numbers over time. Great for alerting and trends, poor for explaining specific requests.
- **Logs** - detailed discrete events. Great for specifics, expensive at volume.
- **Traces** - request paths across services with per-span timing. Great for locating latency and failures in distributed systems.

The pillars framing is useful but incomplete. What actually delivers observability is **high-cardinality, high-dimensionality structured events** that you can slice arbitrarily - by user, version, region, feature flag, and any other attribute - combined with the ability to correlate freely between signals.

**What makes a system observable**

- Wide structured events with rich attributes, not just counters.
- Consistent correlation IDs propagated through every service and included in logs and traces.
- Instrumentation via **OpenTelemetry**, so signals are portable across backends.
- Exemplars linking metrics to representative traces.
- Deploy and configuration-change annotations, so "what changed?" is answerable instantly.

**Why it matters more now:** in a monolith, a stack trace usually explained the failure. In a distributed system with dozens of services and dynamic scheduling, the interesting failures are emergent and cannot be predicted in advance - so pre-defined dashboards are structurally insufficient.

## Interview tips

- "Answering questions you did not anticipate" is the definition that shows real understanding.
- Cardinality as the enabler of observability - and the enemy of Prometheus - is a nuanced point worth making.
- OpenTelemetry plus correlation IDs is the concrete implementation answer.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
