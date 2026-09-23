---
title: "What are different types of Performance Tests?"
id: 72
category: "Performance Testing"
difficulty: "Beginner"
tags:
  - devops
  - performance-testing
  - interview-questions
---

# What are different types of Performance Tests?

**Short answer:** Load (expected traffic), stress (beyond capacity, to find the breaking point), spike (sudden surge), soak/endurance (sustained over hours), volume (large data sets), scalability (does adding resources help), and benchmark (comparison baseline).

## Detail

| Type                     | Question it answers                                         | Typical duration   |
| ------------------------ | ----------------------------------------------------------- | ------------------ |
| **Load**                 | Do we meet SLOs at expected peak traffic?                   | 30–60 min          |
| **Stress**               | Where does it break, and how does it fail?                  | Ramp until failure |
| **Spike**                | Can we survive a sudden 10× surge?                          | Minutes            |
| **Soak / endurance**     | Do we leak memory, connections, or file handles?            | 8–72 hours         |
| **Volume**               | How does the system behave with a production-sized dataset? | Varies             |
| **Scalability**          | Does throughput scale linearly with added instances?        | Stepped ramps      |
| **Benchmark / baseline** | Has this release regressed against the last?                | Short, repeatable  |

**What each catches.** Load tests validate capacity assumptions. Stress tests reveal failure modes - does the service shed load gracefully, or does it fall over and take the database with it? Spike tests expose autoscaling lag and cold-start behaviour. Soak tests catch the slow leaks that only appear after hours, and are the most frequently skipped and most valuable.

**In CI/CD**, a short benchmark test on every build catches regressions early; the long soak and full-scale load tests run nightly or before a major release.

Note the related but distinct disciplines: **capacity planning** uses these results to size infrastructure, and **chaos engineering** tests resilience to failure rather than to load.

## Example

A spike test in k6 - the shape of the `stages` array is what makes it a spike rather than a load test:

```javascript
import http from "k6/http";

export const options = {
  stages: [
    { duration: "2m", target: 50 },   // normal traffic
    { duration: "10s", target: 1000 }, // sudden 20x surge
    { duration: "3m", target: 1000 },  // hold: does autoscaling catch up?
    { duration: "10s", target: 50 },   // drop back
    { duration: "3m", target: 50 },    // does it recover cleanly?
  ],
  thresholds: { http_req_failed: ["rate<0.01"] },
};

export default function () {
  http.get("https://staging.example.com/api/products");
}
```

## Interview tips

- Be able to name the specific defect class each test type finds - that is the real question.
- Soak testing for memory and connection leaks is the one most candidates omit.
- Mention automated performance regression gates in the pipeline as the mature practice.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)
- [[How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?]] (`#536`): [How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?](../cicd/how-do-you-detect-isolate-and-eradicate-flaky-tests-in-a-ci-cd-pipeline.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
