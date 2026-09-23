---
title: "How does the Circuit Breaker pattern prevent cascading failures in microservice architectures?"
id: 591
category: "Scalability and High Availability"
difficulty: "Intermediate"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - circuit-breaker
  - resilience
  - microservices
  - envoy
quiz:
  stem: "What does a Circuit Breaker do when in the 'Open' state?"
  options:
    - "It routes 100% of all production traffic to the database directly"
    - "It immediately fails incoming requests without making any downstream network call, returning a fallback response or error instantly"
    - "It restarts the target container pod"
    - "It opens a persistent SSH debugging tunnel"
  answer: 2
  explanation: "When Open, the breaker does not attempt downstream network calls, failing fast immediately to prevent resource exhaustion and allow the downstream system to recover."
---

# How does the Circuit Breaker pattern prevent cascading failures in microservice architectures?

**Short answer:** A circuit breaker monitors downstream call failures; when errors breach a threshold, it 'trips' open to fail fast immediately without waiting for timeouts, giving the struggling downstream service time to recover before testing recovery in half-open state.

## Detail

**The failure it prevents.** Without circuit breakers, when a downstream payment service slows down, upstream services exhaust their thread pools and connection pools waiting on 30-second timeouts. The caller is now slow too, so _its_ callers pile up, and the slowness propagates hop by hop until the whole request path is down - a cascading failure caused by one sick dependency. Slow is worse than dead here: a dead service fails fast on its own, a slow one holds resources hostage.

### Circuit breaker states

```text
[CLOSED] ──(failures exceed threshold)──> [OPEN]
    ▲                                        │
    │ (probe passes)                         │ (sleep window expires)
    │                                        ▼
    └────────────── [HALF-OPEN] <────────────┘
                    (probe fails)
```

1. **Closed (normal)**: requests pass through. Failures and slow calls are counted over a sliding window (count-based, e.g. the last 100 calls, or time-based, e.g. the last 60 seconds).
2. **Open (tripped)**: once the failure rate crosses the threshold - and only after a minimum number of calls, so three failures out of four at 3 a.m. do not trip it - requests fail immediately with an error or a fallback (cached response, default value, queued write). No network call is made.
3. **Half-open (probe)**: after a wait (e.g. 30 s), a small number of trial requests are let through. If they succeed the breaker closes; if they fail it re-opens and the wait starts again.

**What to count.** Timeouts and 5xx/connection errors, plus calls slower than a threshold ("slow-call rate"), because latency is usually the first symptom. Do not count 4xx client errors - a flood of bad requests should not open the breaker on a healthy service.

**Where it lives.**

- **In the application**: Resilience4j (Java - Netflix Hystrix has been in maintenance mode since 2018 and should not be chosen for new work), Polly (.NET), `gobreaker` (Go), `pybreaker` (Python). Application breakers can return a _meaningful_ fallback because they know the business context.
- **In the proxy/mesh**: Envoy, and therefore Istio and other Envoy-based meshes, provide two related mechanisms. Envoy's **circuit breakers** are really concurrency limits (max connections, pending requests, requests, retries per cluster) - excess requests fail fast with a 503. **Outlier detection** is the state-machine behaviour: hosts returning consecutive 5xx are ejected from the load-balancing pool for a period, then readmitted. Mesh-level breaking needs no code changes but can only return an error, not a business fallback.

**Trade-offs and limitations.** Thresholds are hard to tune: too sensitive and the breaker flaps on normal noise, too lax and it trips after the damage is done. A breaker per _dependency_ (or per host) is essential - one global breaker lets a single bad backend take out calls to healthy ones. Breakers complement, not replace, timeouts, bulkheads (separate pools per dependency), and retry budgets; retries without a breaker simply multiply the load on a struggling service.

## Example

```yaml
# Istio: connection-pool limits (Envoy "circuit breakers") plus outlier ejection.
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: payments
spec:
  host: payments.prod.svc.cluster.local
  trafficPolicy:
    connectionPool:
      tcp: { maxConnections: 100 }
      http:
        http1MaxPendingRequests: 50 # queue bound: excess fails fast with 503
        http2MaxRequests: 200 # max concurrent requests to the cluster
        maxRetries: 3 # concurrent retries across the cluster, a crude budget
    outlierDetection:
      consecutive5xxErrors: 5 # trip a host after 5 straight 5xx
      interval: 10s
      baseEjectionTime: 30s # ejection doubles each time the host is re-ejected
      maxEjectionPercent: 50 # never eject the whole pool
```

```java
// Resilience4j: an application breaker with a business fallback.
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .slidingWindowType(SlidingWindowType.COUNT_BASED)
    .slidingWindowSize(100)
    .minimumNumberOfCalls(20)            // no verdict on tiny samples
    .failureRateThreshold(50)            // % of failed calls that opens the breaker
    .slowCallDurationThreshold(Duration.ofSeconds(2))
    .slowCallRateThreshold(50)           // slow calls count as failures too
    .waitDurationInOpenState(Duration.ofSeconds(30))
    .permittedNumberOfCallsInHalfOpenState(5)
    .build();

CircuitBreaker breaker = CircuitBreaker.of("payments", config);
Supplier<Quote> guarded = CircuitBreaker.decorateSupplier(breaker, paymentsClient::quote);
Quote quote = Try.ofSupplier(guarded).recover(ex -> Quote.cachedOrDefault()).get();
```

## Interview tips

- Lead with the mechanism: failing fast preserves the caller's threads and connection pools, which is what stops the failure spreading upstream.
- Name all three states and what moves between them, including the minimum-call threshold and the half-open probe.
- Say that slow calls should count as failures - latency is usually how a dependency starts dying.
- Distinguish Envoy's circuit breakers (concurrency limits) from outlier detection (host ejection); interviewers who know Envoy will probe this.
- Mention that Hystrix is in maintenance mode and Resilience4j (or a mesh) is the modern choice.
- Close on what a breaker does not do: it needs timeouts, bulkheads, and retry budgets alongside it, and a fallback that is honest about writes.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
