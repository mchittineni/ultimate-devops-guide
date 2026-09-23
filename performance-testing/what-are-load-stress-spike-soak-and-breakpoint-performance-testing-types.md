---
title: "What are Load, Stress, Spike, Soak, and Breakpoint performance testing types?"
id: 609
category: "Performance Testing"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - performance-testing
  - performance
  - testing
  - load-testing
  - stress-testing
quiz:
  stem: "Which type of performance test is specifically engineered to detect slow JVM garbage collection degradation and OS file descriptor leaks that occur over extended periods?"
  options:
    - "Spike testing"
    - "Soak (Endurance) testing"
    - "Smoke testing"
    - "Unit testing"
  answer: 2
  explanation: "Soak testing maintains continuous operational load over 24 to 72 hours, making it the primary method for surfacing slow memory leaks, thread starvation, and storage exhaustion."
---

# What are Load, Stress, Spike, Soak, and Breakpoint performance testing types?

**Short answer:** Load tests verify performance under expected production volume; Stress tests determine behavior under extreme load beyond capacity; Spike tests measure reaction to sudden dramatic traffic bursts; Soak tests verify stability and memory leaks over days; Breakpoint tests ramp load continuously until the system fails.

## Detail

Comprehensive performance engineering requires evaluating diverse stress vectors:

### The Performance Testing Matrix

1. **Load Testing**:
   - Ramps up to expected peak traffic (e.g. 5,000 req/sec) and holds for 1-2 hours.
   - Validates that response times (p95, p99) meet Service Level Objectives (SLOs).
2. **Stress Testing**:
   - Pushes load to 2x-3x expected capacity to verify how the application degrades (graceful degradation via HTTP 429 vs hard panics and database deadlocks).
3. **Spike Testing**:
   - Sudden instantaneous jumps from 100 req/sec to 20,000 req/sec (simulating flash sales or breaking news alerts).
   - Validates autoscaling reaction speed and connection pool queueing.
4. **Soak / Endurance Testing**:
   - Sustains moderate load for 24-72 hours.
   - Detects slow memory leaks, connection pool exhaustion, disk log fill, and JVM garbage collection degradation over time.
5. **Breakpoint / Capacity Testing**:
   - Increments load continuously until the system breaks, establishing maximum hardware limits.

## Example

A breakpoint test with k6's arrival-rate executor: it keeps raising requests per second regardless of how slowly the system responds, and aborts at the first sustained SLO breach - that rate is the capacity figure.

```javascript
import http from "k6/http";

export const options = {
  scenarios: {
    breakpoint: {
      executor: "ramping-arrival-rate", // open model: load does not back off when the SUT slows
      startRate: 100,
      timeUnit: "1s",
      preAllocatedVUs: 500,
      maxVUs: 5000,
      stages: [{ duration: "30m", target: 20000 }], // linear ramp to 20k req/s
    },
  },
  thresholds: {
    http_req_duration: [{ threshold: "p(99)<500", abortOnFail: true, delayAbortEval: "1m" }],
    http_req_failed: [{ threshold: "rate<0.01", abortOnFail: true }],
  },
};

export default function () {
  http.get("https://staging.example.com/api/checkout");
}
```

## Interview tips

- Load (expected traffic) vs Stress (beyond capacity).
- Spike testing evaluating autoscaler reaction times.
- Soak testing to isolate memory leaks and resource exhaustion over days.
- Breakpoint testing finding the exact failure threshold.
- Mention open versus closed load models: a fixed number of virtual users waiting for responses (closed) slows down with the system and under-reports saturation, whereas an arrival-rate executor (open) keeps arriving like real users do.
- Trade-off: soak and breakpoint tests are expensive and slow, so they run nightly or before releases, not on every pull request.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?]] (`#536`): [How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?](../cicd/how-do-you-detect-isolate-and-eradicate-flaky-tests-in-a-ci-cd-pipeline.md)
- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
