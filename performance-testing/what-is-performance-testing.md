---
title: "What is Performance Testing?"
id: 71
category: "Performance Testing"
difficulty: "Beginner"
tags:
  - devops
  - performance-testing
  - interview-questions
---

# What is Performance Testing?

**Short answer:** Performance testing measures how a system behaves under a defined workload - its throughput, latency, resource use, and stability - to verify it meets requirements and to find the point at which it degrades.

## Detail

**What it answers:** Can we handle Black Friday traffic? What is p99 latency at 5,000 requests per second? Where is the bottleneck? Does the system leak memory over 12 hours? How does it fail when overloaded - gracefully or catastrophically?

**The process**

1. **Define objectives** in measurable terms tied to the SLO: "p95 checkout latency under 400 ms at 2,000 concurrent users, error rate under 0.1%."
2. **Model the workload** from production telemetry: real endpoint mix, think times, session shapes, and data variety. A synthetic workload that hammers one cached endpoint proves nothing.
3. **Prepare the environment** - ideally production-scale, provisioned by the same IaC. If it is scaled down, record the ratio and be careful extrapolating.
4. **Execute** with a warm-up period, then a steady measurement window.
5. **Analyse** using percentiles, correlated with server-side metrics - CPU, memory, GC pauses, connection pools, database wait events.
6. **Tune and repeat**, changing one thing at a time.

**Report percentiles, never averages.** An average of 200 ms can hide a p99 of 5 seconds affecting your most valuable users. Report p50, p95, p99, and the maximum.

**Common pitfalls:** load generators that saturate before the system under test, unrealistic caching (same user, same product every request), missing think time, and the coordinated-omission problem where a struggling system's slow responses are silently under-sampled.

## Interview tips

- Percentiles over averages is the single most reliable signal of experience here.
- Mention monitoring the load generator itself - testing your own client's limits is a classic mistake.
- Tie targets to SLOs so the test has a pass/fail meaning rather than producing a number nobody acts on.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you prevent and handle secret leaks in CI/CD pipelines?]] (`#237`): [How do you prevent and handle secret leaks in CI/CD pipelines?](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md)
- [[Explain Docker Architecture]] (`#10`): [Explain Docker Architecture](../docker/explain-docker-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
