---
title: "How do you design a system to degrade gracefully under overload?"
id: 300
category: "Scalability and High Availability"
difficulty: "Advanced"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
---

# How do you design a system to degrade gracefully under overload?

**Short answer:** Decide in advance what you will sacrifice, and enforce it with mechanisms rather than hope. The toolkit: **admission control and load shedding** (reject early, cheaply, by priority), **queues with bounded depth** so back pressure propagates instead of memory filling, **timeouts, retry budgets, and jitter** so clients cannot amplify the problem, **circuit breakers** to stop hammering a failing dependency, **caching and stale-while-revalidate** so degraded still means answering, and **feature-level fallbacks** that turn off expensive non-essential functionality. Serving 90% of users a slightly worse experience beats serving 0% a perfect one - and without these mechanisms overload becomes total failure, not partial.

## Detail

**Why overload turns into collapse.** Past saturation, throughput does not plateau - it _falls_. Queues grow, so latency rises, so clients time out and retry, which adds load, which grows queues further. Meanwhile the work already in the queue is stale: the server spends its capacity computing responses for clients that have already given up. This is the metastable failure state that makes recovery hard even after the original trigger has gone, and it is why autoscaling alone does not save you - new capacity takes tens of seconds while collapse takes a few.

**Admission control: reject early and cheaply.** The cheapest request is the one you refuse at the edge. Rate limit per client and per token at the load balancer or gateway, and inside the service use a concurrency limit rather than a request-per-second limit - concurrency tracks the resource you actually have. Adaptive approaches (Netflix's concurrency-limits, TCP-Vegas-style gradient algorithms, or a simple "reject when queue depth exceeds N") beat static thresholds because the right limit changes with request mix. Crucially: return `429`/`503` with `Retry-After` fast, so clients back off properly.

**Prioritise, because not all requests are equal.** Classify traffic into tiers - user-facing interactive, then paid or premium, then background jobs, then batch and analytics - and shed from the bottom. A checkout request should survive while a report generation is refused. Implement it with a priority attached at the edge and honoured in queues and admission decisions. **Criticality-aware shedding is the single most valuable thing in this answer**, because it converts "the site is down" into "reports are delayed".

**Bound every queue.** An unbounded queue is a memory leak with extra latency: it accepts work it will never complete in time. Bound the depth, reject or shed when full, and drop items whose deadline has passed (LIFO ordering during overload is counter-intuitively better than FIFO, because the newest request is the one most likely to still have a waiting client). Propagate deadlines from the caller so downstream services know when to stop bothering.

**Stop clients from amplifying.** Timeouts on every call, always shorter than the caller's remaining deadline. Retries with **exponential backoff and full jitter** - synchronised retries are a self-inflicted DDoS. A **retry budget** (retries capped at, say, 10% of requests) prevents a retry storm outright, which a per-request retry count cannot. Circuit breakers that open after a failure threshold, so a dead dependency gets a fast local failure instead of a thread pool full of waiting requests. And request hedging only for idempotent reads with a strict budget.

**Keep answering, worse.** Caching with **stale-while-revalidate** means a slow origin degrades to slightly stale data instead of an error. Fallbacks: default recommendations instead of personalised ones, cached search results instead of live, a static shell page instead of a dynamic one, a queued write acknowledged as "we'll process this" instead of a synchronous failure. Feature flags gate the expensive extras so an operator - or an automated policy - can turn them off in seconds.

**Protect the shared bottleneck.** The database is usually the thing that cannot scale in the moment. Connection pools sized so total connections stay under the limit, a pooler in front, read traffic on replicas with an explicit staleness contract, and per-tenant limits so one heavy customer cannot consume everything (bulkheads). Cache stampede protection - request coalescing plus jittered TTLs - matters most in the seconds after a cache flush or a cold start.

**Verify it, because untested degradation is a theory.** Load test past the knee to find where behaviour changes; inject dependency latency and failure in game days; test that shedding actually sheds the right tier; confirm the recovery path (does the system return to health when load drops, or does it need a restart?). Then instrument it: shed rate, queue depth, breaker state, and cache staleness need to be on the dashboard, and an alert on shedding starting is the earliest possible warning that capacity is short.

## Example

```yaml
# Edge: tiered rate limits, so shedding hits batch traffic before checkout.
# Priority is assigned by us, never by the caller: the gateway strips any inbound X-Priority
# and re-stamps it from the authenticated identity (service account / API-key tier) and the
# route itself. Without the strip, any client can label itself "interactive" and walk past
# the shedding tier - the header is a trust boundary, not a hint.
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: api }
spec:
  rules:
    - matches: [{ path: { value: /batch } }] # route metadata, not a client header
      filters:
        - type: RequestHeaderModifier
          requestHeaderModifier:
            set: [{ name: X-Priority, value: batch }] # overwrite whatever arrived
        - type: ExtensionRef
          extensionRef: { kind: RateLimitPolicy, name: batch-100rps } # shed first
    - matches: [{ path: { value: /checkout } }]
      filters:
        - type: RequestHeaderModifier
          requestHeaderModifier:
            set: [{ name: X-Priority, value: interactive }]
        - type: ExtensionRef
          extensionRef: { kind: RateLimitPolicy, name: interactive-5000rps } # protected
```

```yaml
# Envoy: reject at the door when concurrency is exceeded - cheaper than queueing.
circuit_breakers:
  thresholds:
    - priority: DEFAULT
      max_connections: 1000
      max_pending_requests: 100 # bounded queue, not unbounded
      max_requests: 1000
      max_retries: 30 # a retry budget, not per-request retries
outlier_detection: # eject failing hosts automatically
  consecutive_5xx: 5
  interval: 10s
  base_ejection_time: 30s
retry_policy:
  retry_on: "5xx,reset"
  num_retries: 2
  retry_back_off: { base_interval: 0.05s, max_interval: 1s } # with jitter
  per_try_timeout: 0.3s
```

```python
# Service: deadline propagation, bounded queue, LIFO under pressure, priority shedding.
MAX_INFLIGHT = 200          # concurrency, not rps - tracks the real resource
HARD_CEILING = int(MAX_INFLIGHT * 1.25)

# One semaphore is the admission controller. A read-then-act check on a counter races: under
# load, N coroutines all read "199 inflight" and all proceed. Acquire, or be rejected.
slots = asyncio.Semaphore(HARD_CEILING)

async def handle(req):
    deadline = req.deadline or (now() + 1.0)
    if now() > deadline:                      # already stale: do no work at all
        return Response(504)

    # Soft tier: advisory, so an approximate count is fine - shed the bottom priorities
    # well before the hard ceiling. The ceiling itself must not be advisory.
    if inflight() >= MAX_INFLIGHT and req.priority in ("batch", "analytics"):
        return Response(429, headers={"Retry-After": "30"})       # shed the bottom tier

    try:
        await asyncio.wait_for(slots.acquire(), timeout=0.005)    # non-blocking in practice
    except asyncio.TimeoutError:                                  # hard ceiling for everyone
        return Response(503, headers={"Retry-After": "2"})

    try:
        budget = deadline - now() - 0.02      # reserve 20 ms to write our own response
        if budget <= 0:                       # no time left: never start a doomed call
            return Response(504)
        # never let a downstream call outlive our own deadline - no floor, the budget is the cap
        return await downstream(req, timeout=budget)
    except (Timeout, CircuitOpen):
        # Degrading a READ to stale data is honest. Degrading a WRITE to a 200 is a lie:
        # the caller stops retrying and the mutation is simply lost.
        if req.is_read:
            cached = cache.get(req.key, allow_stale=True)
            return cached or Response(200, body=DEFAULT_FALLBACK)
        # For writes: check if downstream already committed before enqueueing.
        # The idempotency key (req.id) prevents replay: the queue consumer and downstream
        # both enforce it, and we check operation status before assuming failure.
        existing = check_operation_status(req.id)
        if existing:                          # downstream committed despite timeout
            return existing                   # return the actual result, do not enqueue
        if durable_queue.enqueue(req):        # only claim acceptance once it is persisted
            return Response(202, headers={"Location": f"/status/{req.id}"})
        return Response(503, headers={"Retry-After": "5"})        # nothing durable: say so
    finally:
        slots.release()                       # every path, including the 504 above
```

```promql
# The dashboard for degradation. Shedding starting is your earliest capacity alert.
sum(rate(requests_shed_total[1m])) by (priority)
max(queue_depth) by (service)
sum(circuit_breaker_open) by (dependency)
histogram_quantile(0.99, sum by (le) (rate(request_duration_seconds_bucket[5m])))

- alert: SheddingStarted
  expr: sum(rate(requests_shed_total{priority!="batch"}[5m])) > 0
  for: 2m
  annotations: { summary: "Shedding non-batch traffic - capacity is short" }
```

## Interview tips

- Open with "decide in advance what you will sacrifice". Graceful degradation is a design decision, not an emergency behaviour.
- Explain why throughput _falls_ past saturation and how retries create a metastable failure state. That mechanism is what the question is really about.
- Criticality-aware load shedding is the highest-value idea here. Give the tier list and a concrete example - checkout survives, report generation does not.
- Say concurrency limits rather than requests-per-second, and explain why concurrency tracks the actual resource.
- Retry budget plus full jitter, not just exponential backoff. The budget is the detail that distinguishes a strong answer.
- Bounded queues, deadline propagation, and dropping stale work (LIFO under load) are all worth naming - unbounded queues are the classic mistake.
- Finish with verification: load test past the knee, inject failure, and confirm the system recovers when load drops without a restart.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
