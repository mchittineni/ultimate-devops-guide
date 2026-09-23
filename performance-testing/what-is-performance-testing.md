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

## Example

The objective from step 1 written as an executable k6 test - the thresholds are the pass/fail criteria:

```javascript
import http from "k6/http";
import { sleep } from "k6";

export const options = {
  stages: [
    { duration: "5m", target: 2000 },  // ramp to 2,000 concurrent users
    { duration: "20m", target: 2000 }, // steady measurement window
  ],
  thresholds: {
    "http_req_duration{name:checkout}": ["p(95)<400"],
    http_req_failed: ["rate<0.001"],
  },
};

export default function () {
  http.post("https://staging.example.com/api/checkout", JSON.stringify({ cart: "c-123" }), {
    headers: { "Content-Type": "application/json" },
    tags: { name: "checkout" },
  });
  sleep(3); // think time
}
```

## Interview tips

- Percentiles over averages is the single most reliable signal of experience here.
- Mention monitoring the load generator itself - testing your own client's limits is a classic mistake.
- Tie targets to SLOs so the test has a pass/fail meaning rather than producing a number nobody acts on.
- Trade-off to acknowledge: a production-scale test environment is expensive, so many teams test a scaled-down copy and extrapolate carefully, or run controlled tests in production - be ready to say which you would choose and why.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[How do you prevent and handle secret leaks in CI/CD pipelines?]] (`#237`): [How do you prevent and handle secret leaks in CI/CD pipelines?](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md)
- [[Explain Docker Architecture]] (`#10`): [Explain Docker Architecture](../docker/explain-docker-architecture.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
