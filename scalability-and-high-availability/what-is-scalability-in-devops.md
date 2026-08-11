---
title: "What is Scalability in DevOps?"
id: 56
category: "Scalability and High Availability"
difficulty: "Beginner"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
---

# What is Scalability in DevOps?

**Short answer:** Scalability is a system's ability to handle increased load by adding resources - vertically (a bigger machine) or horizontally (more machines) - ideally automatically and without redesign.

## Detail

**Vertical scaling (scale up)** - more CPU, memory, or IOPS on one machine. Simple, no application changes, but bounded by the largest instance available, usually requires a restart, and leaves a single point of failure.

**Horizontal scaling (scale out)** - more instances behind a load balancer. Effectively unbounded, improves availability, and enables rolling deploys - but requires the application to be stateless or to externalise state, and introduces distributed-systems concerns.

**What makes horizontal scaling possible**

- **Statelessness** - no session or user data in instance memory or local disk; push it to Redis, a database, or a signed token.
- **Externalised configuration** - instances are interchangeable.
- **Idempotent operations** - safe retries when a request is routed to a different instance.
- **Shared-nothing design** - instances do not coordinate directly.

**Where scaling actually stops.** Application tiers scale easily; the database is usually the bottleneck. The progression is: read replicas → caching → connection pooling → partitioning/sharding → a different storage engine for the hot path.

**Elasticity** is scalability plus automation: capacity that grows _and shrinks_ with demand, which is where the cloud cost benefit comes from.

## Example

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 3
  maxReplicas: 50
  metrics:
    - type: Resource
      resource:
        { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300 # avoid flapping
```

## Interview tips

- State the vertical/horizontal trade-off, then immediately move to what makes horizontal scaling possible - statelessness is the key insight.
- Name the database as the usual bottleneck; it is the follow-up question in most interviews.
- Distinguish scalability (can grow) from elasticity (grows and shrinks automatically).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
