---
title: "What is the Thundering Herd problem and how do jitter and exponential backoff prevent it?"
id: 590
category: "Scalability and High Availability"
difficulty: "Intermediate"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - resilience
  - thundering-herd
  - jitter
  - caching
  - backoff
quiz:
  stem: "How does adding randomized 'Full Jitter' to exponential backoff algorithms protect recovering backend databases?"
  options:
    - "It compresses TCP packets by 50%"
    - "It randomizes retry timestamps across clients, desynchronizing request spikes into a smooth, manageable stream of traffic"
    - "It forces all clients to disconnect permanently after two retries"
    - "It redirects failing traffic to an in-memory Redis cache"
  answer: 2
  explanation: "Without jitter, all clients retry at identical mathematical intervals, creating destructive traffic waves. Jitter spreads retries randomly across the time window."
---

# What is the Thundering Herd problem and how do jitter and exponential backoff prevent it?

**Short answer:** The Thundering Herd problem occurs when hundreds or thousands of waiting clients or processes awaken simultaneously on an event (cache expiry, service restart) and overwhelm backend resources; adding randomized jitter to exponential retry intervals spreads the load over time.

## Detail

When an outage occurs or a hot cache key expires, naive client behaviour turns a minor blip into a cascading failure. The common triggers: a dependency recovers and every client reconnects at once, a popular cache key expires, a fleet restarts together, or cron jobs on every host fire at `00:00`.

### The problem without jitter

If 10,000 clients fail a request at `t=0` and all retry with plain exponential backoff:

- $t=1$: 10,000 requests hit simultaneously.
- $t=2$: 10,000 requests hit simultaneously.
- $t=4$: 10,000 requests hit simultaneously.

Backoff reduces the _number_ of retries per client but not their _synchronisation_. The recovering backend is knocked over by each wave, so it never gets back to health.

### The fix: exponential backoff with full jitter

Pick the sleep uniformly at random between zero and the exponential cap:

$$\text{sleep} = \text{random}(0,\ \min(\text{cap},\ \text{base} \times 2^{\text{attempt}}))$$

The 10,000 retries are now spread across the whole window, so the backend sees a smooth stream it can work through. AWS's analysis of the variants ("full", "equal", and "decorrelated" jitter) found full jitter does the least total work; decorrelated jitter is a good alternative. Always combine it with a **maximum number of attempts** and a **retry budget** (e.g. retries capped at 10% of requests), and only retry idempotent operations.

### Cache stampede (dog-piling)

When a hot key expires, every request misses at once and recomputes the same value against the database. Mitigations:

- **TTL jitter**: `ttl = 3600 + random(0, 300)` so keys written together do not expire together.
- **Request coalescing / single-flight**: only one caller recomputes a missing key; the others wait for its result (Go's `singleflight`, NGINX `proxy_cache_lock`, a short Redis lock).
- **Stale-while-revalidate / early refresh**: serve the old value while one worker refreshes it, or refresh probabilistically shortly before expiry.

**Limitations.** Jitter spreads load but does not reduce it - if total demand exceeds capacity, you still need load shedding and circuit breakers. And jitter only works if _every_ client uses it; one unjittered SDK can still produce waves.

## Example

```python
import random
import time


def call_with_backoff(fn, attempts=5, base=0.1, cap=10.0):
    """Exponential backoff with full jitter; only wrap idempotent calls."""
    for attempt in range(attempts):
        try:
            return fn()
        except (ConnectionError, TimeoutError):
            if attempt == attempts - 1:
                raise
            time.sleep(random.uniform(0, min(cap, base * 2 ** attempt)))
```

```nginx
# NGINX: collapse concurrent misses for the same key into one upstream request,
# and keep serving the stale copy while it is refreshed.
proxy_cache_path /var/cache/nginx keys_zone=api:50m inactive=10m;

location /api/ {
    proxy_cache api;
    proxy_cache_lock on;                       # single-flight per cache key
    proxy_cache_lock_timeout 5s;
    proxy_cache_use_stale updating error timeout;
    proxy_cache_background_update on;          # refresh in the background
    proxy_pass http://api_backend;
}
```

## Interview tips

- Explain why backoff alone fails: it reduces retries but leaves them synchronised.
- Give the full-jitter formula and pair it with max attempts, a retry budget, and idempotency.
- Treat cache stampede as the other half of the question: TTL jitter, single-flight, and stale-while-revalidate.
- Note that jitter spreads load but does not remove it - circuit breakers and load shedding handle genuine overload.
- A real example (every pod reconnecting to a restarted database, or cron at midnight on every host) makes the answer land.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
