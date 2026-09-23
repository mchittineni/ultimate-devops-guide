---
title: "What are Performance Testing Best Practices?"
id: 74
category: "Performance Testing"
difficulty: "Intermediate"
tags:
  - devops
  - performance-testing
  - interview-questions
---

# What are Performance Testing Best Practices?

**Short answer:** Test against realistic workloads and data in a production-like environment, define pass/fail thresholds from your SLOs, measure percentiles, change one variable at a time, and automate a regression test in the pipeline.

## Detail

**Design**

- Derive targets from SLOs and real traffic patterns, not from guesses.
- Model the workload from production logs: endpoint mix, payload sizes, think time, and the long tail of rare-but-slow operations.
- Use production-shaped data volumes - a query that is fast against 1,000 rows may collapse at 100 million.
- Vary test data so you are not measuring cache hit rates.

**Environment**

- Provision with the same IaC as production; document any scaling ratio.
- Isolate the environment so other traffic does not pollute results.
- Reset to a known state between runs, and always include a warm-up period (JIT, caches, connection pools).

**Execution**

- Change one variable per run.
- Run each configuration multiple times; single runs are noisy.
- Monitor the load generator's own CPU, memory, and network - a saturated client produces meaningless numbers.

**Analysis**

- Percentiles, not averages. Watch p95, p99, and max.
- Correlate client-side latency with server-side metrics: CPU, GC pauses, thread and connection pool saturation, database locks.
- Find the "knee" - the concurrency level at which latency starts rising faster than throughput. That is your real capacity.

**Automation**

- Short benchmark on every pull request to catch regressions; full load test before major releases; nightly soak.
- Fail the build on threshold breaches, and trend the results over time so slow degradation is visible.

## Example

A pipeline gate: k6 exits with a non-zero code (99) when a threshold fails, which fails the CI job.

```javascript
// perf/smoke.js - short regression benchmark run on every pull request
import http from "k6/http";

export const options = {
  vus: 20,
  duration: "2m",
  thresholds: {
    "http_req_duration{endpoint:search}": ["p(95)<300", "p(99)<800"],
    http_req_failed: ["rate<0.005"],
  },
};

export default function () {
  http.get(`${__ENV.BASE_URL}/search?q=boots`, { tags: { endpoint: "search" } });
}
```

```bash
k6 run -e BASE_URL=https://pr-1234.preview.example.com perf/smoke.js
```

## Interview tips

- The knee of the throughput/latency curve is a precise, senior way to define capacity.
- Emphasise repeatability - a test you cannot reproduce cannot prove a fix worked.
- Have a story about a bottleneck you found and what the fix actually was.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
