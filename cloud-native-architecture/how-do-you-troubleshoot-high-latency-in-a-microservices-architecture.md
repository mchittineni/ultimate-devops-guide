---
title: "How do you troubleshoot high latency in a microservices architecture?"
id: 426
category: "Cloud Native Architecture"
difficulty: "Advanced"
tags:
  - devops
  - cloud-native-architecture
  - interview-questions
  - monitoring-and-logging
  - api-gateway-and-service-mesh
  - performance-testing
---

# How do you troubleshoot high latency in a microservices architecture?

**Short answer:** Localise before you optimise. Use **distributed tracing** to find which span in the request path owns the time - that single step replaces hours of guessing, because in a chain of eight services the slow one is rarely the one being blamed. Then classify what you found: **fan-out and N+1 calls** (the most common architectural cause), **a slow dependency** (usually the database), **queueing from insufficient concurrency or a saturated connection pool**, **retries amplifying load**, **tail latency from one bad instance or availability zone**, or **serialisation and payload size**. Always work in **percentiles** - a p50 that looks fine while p99 is 30x worse is the normal shape of this problem - and remember that a synchronous chain multiplies failure and latency, so the durable fix is often architectural rather than a faster query.

## Detail

### Step 1: measure the right thing

- **Percentiles, not averages.** Report p50, p95, p99, and max. An average hides the 1% of users who are timing out, and averaging percentiles across instances is statistically meaningless - aggregate from histograms instead.
- **Where do you measure?** Client-observed latency (RUM or the API gateway) is the truth; a service's own timer excludes queueing before it and the network back. Compare the two: a large gap _is_ the finding, and it usually means queueing or connection setup.
- **Separate the paths.** One slow endpoint dragging the aggregate is common; break down by route, tenant, region, and instance before concluding "the service is slow".

### Step 2: localise with tracing

A trace shows the request as a tree of spans with durations. Read it for four patterns:

1. **One long span** - a single slow dependency. Go there.
2. **Many short spans in sequence** - the classic **N+1**: a service calling another once per item in a loop. 200 sequential calls at 4 ms is 800 ms of pure round trips. Fix with batch endpoints, a join at the data layer, or `DataLoader`-style coalescing.
3. **A long parent with short children** - the time is _inside_ the service: CPU, garbage collection, serialisation, lock contention, or a thread pool that is full.
4. **Gaps between spans** - queueing. The request was waiting for a worker, a connection from the pool, or a scheduler. This is the pattern people miss most often, because nothing is "slow" - everything is waiting.

If you have no tracing, that is the finding: instrument the boundaries first (OpenTelemetry auto-instrumentation gets you most of the way in a day) rather than debugging blind. See [what is tracing in observability](../advanced-devops-cloud/what-is-tracing-in-observability.md) and [what is observability](../advanced-devops-cloud/what-is-observability.md).

### Step 3: the recurring causes and their fixes

- **Fan-out amplification.** One user request becoming 40 internal calls means the slowest of 40 determines your latency, and p99 of the whole is far worse than p99 of any part. Reduce the fan-out, parallelise independent calls, cache aggressively, or introduce a read model / API composition layer.
- **Synchronous chains.** A → B → C → D adds latency and failure probability at every hop. Ask whether the call must be synchronous: an event, a queue, or a materialised read model converts request-time latency into background work. This is usually the highest-leverage change and the one interviewers most want to hear.
- **Database time.** Missing index, plan regression, lock contention, or connection-pool exhaustion in the calling service. Note the two very different shapes: slow queries (fix the query) versus pool waits (fix the pool). See [how do you troubleshoot a database that is slow or timing out under load](../database-management-in-devops/how-do-you-troubleshoot-a-database-that-is-slow-or-timing-out-under-load.md).
- **Retries and timeouts misconfigured.** A downstream slowdown plus 3 retries at every layer produces exponential load and turns a blip into an outage. Use retry **budgets**, jittered backoff, retry only idempotent calls, and set timeouts that _decrease_ as you go deeper (if the edge times out at 2 s, an inner call must not wait 5 s). Add circuit breakers so a failing dependency fails fast rather than consuming your threads.
- **Tail latency from one bad instance.** A single Pod with a full heap, a noisy neighbour, or a cold cache can own your p99. Look at latency **per instance** - and use least-outstanding-requests load balancing, outlier detection (mesh-level ejection), and hedged requests where appropriate. See [how do you troubleshoot a load balancer returning 5xx errors or sending traffic unevenly](../scalability-and-high-availability/how-do-you-troubleshoot-a-load-balancer-returning-5xx-errors-or-sending-traffic-unevenly.md).
- **Cold starts and warm-up.** JIT compilation, cold caches, and lazy connection pools make the first requests after a deploy or scale-out slow, which shows as latency spikes correlated with rollouts.
- **Network and topology.** Cross-availability-zone or cross-region hops add milliseconds per call and multiply across fan-out; TLS handshakes without connection reuse add a round trip each time; DNS lookups without caching add another. Keep chatty services co-located and reuse connections.
- **Payload and serialisation.** Over-fetching whole objects to read one field, JSON parsing of megabyte responses, and missing compression are unglamorous but frequent.
- **Sidecar and mesh overhead.** A service mesh adds a small per-hop cost that becomes visible at high fan-out; measure it rather than assuming it is free or ruinous. See [how do you run a service mesh in production without the sidecar tax](../api-gateway-and-service-mesh/how-do-you-run-a-service-mesh-in-production-without-the-sidecar-tax.md).

### Step 4: prove the fix and keep it

Change one thing, measure the same percentile at the same place, and keep a **latency SLO** with an error budget so regressions are caught by policy rather than by a customer complaint. Load test with production-shaped data and concurrency, because latency problems are almost always emergent under load. Then add the guardrails that stop recurrence: a p99 alert per critical route, per-instance latency visibility, and a budget on total internal calls per user request - that last one is the metric that keeps fan-out from creeping back. See [how do you measure a latency SLI correctly](../slo-engineering/how-do-you-measure-a-latency-sli-correctly.md) and [how do you load test safely against production](../performance-testing/how-do-you-load-test-safely-against-production.md).

## Example

```text
Trace: GET /checkout   total 2 140 ms   (p99; p50 is 180 ms - percentiles matter)

  api-gateway                              2 140 ms
  └─ checkout-svc                          2 130 ms
     ├─ auth-svc          8 ms
     ├─ cart-svc         42 ms
     ├─ [gap]           310 ms   <- NO span: waiting for a connection from the pool
     ├─ pricing-svc  x 200      1 480 ms   <- N+1: one call PER cart item, sequential
     │    └─ each: 7 ms (fine individually - the loop is the bug)
     ├─ inventory-svc    95 ms
     └─ payment-svc     195 ms  (2 attempts: 1 timeout at 150ms + 1 retry)

Findings, in order of payoff:
  1. N+1 to pricing-svc      -> batch endpoint: 1 480 ms -> 30 ms
  2. 310 ms connection wait  -> pool 5 -> 25, and pre-warm on startup
  3. payment retry at 150ms  -> timeout is below p99 of the dependency; raise to 400ms
                                with 1 jittered retry, and a circuit breaker
  p99 2 140 ms -> 340 ms without making a single service "faster".
```

```promql
# Percentiles from histograms, per route - never average a percentile
histogram_quantile(0.99,
  sum by (le, route) (rate(http_request_duration_seconds_bucket{service="checkout"}[5m])))

# Is one instance owning the tail? (the single most useful latency query)
topk(5, histogram_quantile(0.99,
  sum by (le, pod) (rate(http_request_duration_seconds_bucket{service="checkout"}[5m]))))

# Fan-out budget: internal calls per inbound request - stops N+1 creeping back
sum(rate(http_client_requests_total{service="checkout"}[5m]))
  / sum(rate(http_server_requests_total{service="checkout"}[5m]))

# Queueing, not slowness: time waiting for a connection from the pool
histogram_quantile(0.99, sum by (le) (rate(db_pool_wait_seconds_bucket[5m])))
```

## Interview tips

- Say "localise with tracing before optimising anything" first. The instinct to profile the whole system, or to blame the database by default, is what this question tests.
- Name the four trace shapes - one long span, many short spans (N+1), long parent with short children, and **gaps** meaning queueing. The gap case is the one that impresses, because it means you have read real traces.
- Insist on percentiles and on where you measure. Client-observed versus server-observed latency, and the gap between them being the finding, is a strong point.
- N+1 across a network boundary is the most common architectural cause - give the arithmetic (200 calls × 4 ms) because concrete numbers land.
- Bring up timeout and retry configuration with the specific rule: timeouts must shrink as you go deeper, retries need budgets and jitter, and only idempotent calls may be retried.
- Mention tail latency owned by a single instance, and the per-pod percentile query that finds it. Few candidates think to break latency down by instance.
- The senior move is questioning the synchronous chain itself - events, queues, or a read model - rather than only making each hop faster.
- Close with how you keep it fixed: a latency SLO with an error budget, per-route p99 alerts, and a fan-out budget metric. See [what are microservices](./what-are-microservices.md) and [what is the difference between a monolith and microservices](./what-is-the-difference-between-a-monolith-and-microservices.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
