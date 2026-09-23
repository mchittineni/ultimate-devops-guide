---
title: "What is Coordinated Omission in load testing and how does it invalidate benchmark results?"
id: 611
category: "Performance Testing"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - performance-testing
  - performance
  - testing
  - benchmarking
  - coordinated-omission
quiz:
  stem: "What is the primary consequence of Coordinated Omission in load testing results?"
  options:
    - "It causes test runners to consume all local CPU cores"
    - "It drastically under-reports tail latency percentiles by omitting the queued requests that would have piled up during server pauses"
    - "It generates invalid JSON reports"
    - "It prevents load generators from using HTTPS connections"
  answer: 2
  explanation: "If a testing client blocks on a frozen server, it fails to send subsequent requests on schedule. The tool records one slow request instead of hundreds of backed-up requests, artificially deflating measured latency."
---

# What is Coordinated Omission in load testing and how does it invalidate benchmark results?

**Short answer:** Coordinated Omission occurs when a load testing tool waits for a blocked response before issuing the next request, inadvertently pausing load generation during server freezes and omitting the catastrophic latency queuing that real clients would experience.

## Detail

Coined by Gil Tene, Coordinated Omission explains why benchmark tests claim an app handles 10,000 req/sec with 50ms latency, yet the system crashes in production.

### How Coordinated Omission Corrupts Data

Suppose a load generator runs 1 client thread designed to send a request every 10ms:

1. Requests 1-10 complete in 1ms each. Recorded latency = 1ms.
2. The server experiences a 10-second JVM garbage collection freeze.
3. Request 11 blocks for 10 seconds.
4. **The Flaw**: Because the load testing tool is blocked waiting for Request 11, **it fails to send the 1,000 requests that should have been sent during those 10 seconds!**
5. When the server awakens, the tool records:
   - 10 fast requests (1ms)
   - 1 slow request (10s)
   - **Omitted**: The 1,000 requests that would have sat in socket backlogs experiencing 10s, 9.99s, 9.98s... of latency!

### Avoiding Coordinated Omission

The fix is an **open workload model**: requests are sent on a fixed schedule whether or not earlier ones have returned, and latency is measured from the time each request _should_ have been sent.

- **wrk2** does exactly this (constant throughput via `-R`, latency corrected from the intended send time) and is the tool Gil Tene built to demonstrate the problem.
- **k6** avoids it only with its arrival-rate executors (`constant-arrival-rate`, `ramping-arrival-rate`); the default VU-based executors are a closed model and are affected.
- **Gatling** avoids it with open injection profiles (`constantUsersPerSec`, `rampUsersPerSec`); closed profiles (`constantConcurrentUsers`) are affected.
- **HdrHistogram** can back-fill the missing samples when a tool knows the expected interval (`recordValueWithExpectedInterval`).

**Trade-off.** An open model needs enough connections and virtual users to keep sending while the server is stalled; if the generator runs out, it silently becomes closed again - so watch for k6's `dropped_iterations` metric.

## Example

Compare a closed-loop run with a constant-rate run against the same endpoint - a big gap in the tail is coordinated omission:

```bash
# wrk (closed loop): each connection waits for its response before sending the next
wrk -t4 -c100 -d60s --latency https://staging.example.com/api/items

# wrk2 (open loop, binary is also called wrk): fixed 2,000 req/s, CO-corrected latency
wrk -t4 -c100 -d60s -R2000 --latency https://staging.example.com/api/items
# If p99 is 40 ms in the first run and 3 s in the second, the first run was lying.
```

## Interview tips

- Load generator pausing scheduled requests while waiting for blocked responses.
- Under-reporting latency percentiles during server stalls.
- Decoupling request generation rate (arrival schedule) from response arrival.
- Tools and modes that avoid it (wrk2, k6 arrival-rate executors, Gatling open injection).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?]] (`#536`): [How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?](../cicd/how-do-you-detect-isolate-and-eradicate-flaky-tests-in-a-ci-cd-pipeline.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
