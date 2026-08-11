---
title: "What is Cloud Native Architecture?"
id: 66
category: "Cloud Native Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-native-architecture
  - interview-questions
---

# What is Cloud Native Architecture?

**Short answer:** Cloud native architecture designs applications specifically for cloud environments - as loosely coupled, containerised, dynamically orchestrated services that are resilient, observable, and changed frequently through automation.

## Detail

The CNCF definition names the enabling technologies: containers, service meshes, microservices, immutable infrastructure, and declarative APIs. The underlying principles matter more than the tools:

- **Designed for failure.** Instances are disposable and will be killed at any moment. Applications handle restarts, retries with backoff, timeouts, and circuit breaking as normal behaviour.
- **Loose coupling.** Services communicate through well-defined APIs or events, deploy independently, and own their data.
- **Elasticity.** Stateless services scale horizontally on demand; state is externalised.
- **Automation everywhere.** Infrastructure as code, CI/CD, and declarative configuration reconciled continuously.
- **Observability by default.** Structured logs, metrics, traces, and health endpoints are part of the definition of done.
- **Immutability.** Deploy new versions by replacement, never by patching running instances.

**The trade-off.** Cloud native buys independent scaling and deployment at the cost of distributed-systems complexity: network partitions, eventual consistency, distributed tracing, and far more operational surface. It is the right choice when you have many teams and a genuine need to deploy and scale independently - and the wrong choice for a small team with a modest application, where a well-built monolith on a managed platform wins.

## Interview tips

- Lead with the principles; naming Kubernetes first is the weaker answer.
- "Designed for failure" is the phrase that captures the mindset shift.
- Show judgement by naming when a monolith is the better architecture - seniority is visible in restraint.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
