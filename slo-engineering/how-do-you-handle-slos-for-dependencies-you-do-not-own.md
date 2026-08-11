---
title: "How do you handle SLOs for dependencies you do not own?"
id: 182
category: "SLO Engineering"
difficulty: "Advanced"
tags:
  - devops
  - slo-engineering
  - interview-questions
---

# How do you handle SLOs for dependencies you do not own?

**Short answer:** Own your user-facing SLO regardless of whose fault a failure is, then engineer so that a dependency's failure does not automatically become yours: timeouts, retries with jitter, circuit breakers, caching, and graceful degradation. Track each dependency's contribution to your error budget so the conversation with that team - or that vendor - is evidence-based.

## Detail

**Users do not care whose fault it is.** If your checkout fails because a payment provider is down, your SLI records failures. Excluding third-party failures from your SLO makes the number pleasant and useless. Measure the user experience; attribute causes separately.

**Dependency maths sets the ceiling.** Serial dependencies multiply: three dependencies at 99.9% each give at most 99.7% before your own failures. If your target exceeds what the chain permits, you need redundancy (a second provider), asynchrony (accept the request now, settle later), or degradation (serve a cached or reduced response).

**The degradation catalogue** is where reliability is actually won:

- **Hard dependency** - no answer possible without it. Minimise these deliberately.
- **Soft dependency** - degrade: hide recommendations, skip fraud enrichment, serve stale cache, queue for later processing.
- **Fallback path** - a second provider or a simpler algorithm.

Classifying every dependency as hard or soft, and testing the soft path, is the concrete work behind "we handle dependency failure".

**Protect yourself from slow, not just down.** A dependency that answers in 30 seconds exhausts your connection pool and takes you down more effectively than one that refuses connections. Aggressive timeouts (well inside your own latency SLO), bounded concurrency, and a circuit breaker are non-negotiable. Retries need jitter and a budget - retry storms turn a partial dependency failure into a total one.

**Attribution, then leverage.** Label error-budget consumption by cause so you can say "this dependency cost us 40% of last quarter's budget". Internally that funds a fix or a redundancy project; with a vendor it is the input to a contractual conversation - and note that a vendor's SLA credit never compensates for your own breached commitment.

## Example

```yaml
# Envoy/Istio: outlier detection ejects a failing upstream, with a strict timeout
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payments
spec:
  host: payments.external.svc
  trafficPolicy:
    connectionPool:
      http: { http2MaxRequests: 200, maxRequestsPerConnection: 10 }
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

```promql
# Attribute budget burn by dependency so the conversation has numbers
sum by (dependency) (
  rate(http_requests_total{job="checkout",code=~"5..",failure_source!=""}[28d])
)
```

## Interview tips

- Say plainly: "the SLO is ours even when the failure is not" - then pivot to degradation as the engineering answer.
- Do the serial-availability multiplication out loud; interviewers use it to test whether targets are grounded.
- Expect: "slow versus down, which is worse?" - slow, and explain the connection-pool exhaustion mechanism.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
