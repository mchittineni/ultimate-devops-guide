---
title: "How to analyze Performance Test Results?"
id: 75
category: "Performance Testing"
difficulty: "Intermediate"
tags:
  - devops
  - performance-testing
  - interview-questions
---

# How to analyze Performance Test Results?

**Short answer:** Start from the user-facing signals - throughput, error rate, and latency percentiles over time - then correlate with resource and dependency metrics to locate the bottleneck, and validate the finding by fixing one thing and re-testing.

## Detail

**Step 1 - read the headline signals.** Plot requests per second, error rate, and p50/p95/p99 latency against time, overlaid with the load ramp. The shape tells the story: latency flat then rising sharply at a specific concurrency indicates saturation; errors appearing before latency rises suggests a hard limit such as a connection pool or rate limiter.

**Step 2 - find the knee.** Throughput rises with concurrency until a resource saturates; past that point, throughput plateaus and latency climbs. That inflection is your capacity number.

**Step 3 - correlate server-side.** Walk the layers using the USE method (Utilisation, Saturation, Errors) for each resource:

- CPU high with low latency variance → genuine compute limit; scale out or optimise hot paths.
- CPU low but latency high → waiting on something: database, downstream service, lock contention, or GC.
- Memory climbing steadily across a soak run → a leak.
- Long GC pauses aligned with latency spikes → heap tuning or allocation reduction.
- Connection pool at maximum with queueing → pool sizing or slow queries downstream.

**Step 4 - go one level deeper.** Use traces to find the slow span, database performance views for slow queries and lock waits, and a profiler (flame graph) for CPU hot spots.

**Step 5 - validate.** Change one thing, re-run the identical test, compare against the baseline. If the fix does not move the number, it was not the bottleneck.

**Report** with context: configuration, workload, environment, the percentile table, the identified bottleneck, and the recommendation with expected impact.

## Interview tips

- "CPU low, latency high - so it is waiting on something" is the diagnostic instinct interviewers want to hear.
- Mention coordinated omission if you want to demonstrate depth on measurement accuracy.
- Always end with re-testing to prove the fix - analysis without validation is a hypothesis.

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
