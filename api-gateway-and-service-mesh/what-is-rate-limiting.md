---
title: "What is Rate Limiting?"
id: 79
category: "API Gateway and Service Mesh"
difficulty: "Beginner"
tags:
  - devops
  - api-gateway-and-service-mesh
  - interview-questions
---

# What is Rate Limiting?

**Short answer:** Rate limiting caps how many requests a client may make in a time window, protecting backends from overload and abuse, ensuring fair use, and controlling cost.

## Detail

**Algorithms**

- **Fixed window** - count per calendar minute. Simple, but allows a burst of 2× the limit across a window boundary.
- **Sliding window log** - exact, stores timestamps, memory-hungry.
- **Sliding window counter** - weighted blend of the current and previous window; the common production compromise.
- **Token bucket** - tokens refill at a steady rate up to a bucket size; permits controlled bursts. The most widely used.
- **Leaky bucket** - requests drain at a fixed rate, smoothing traffic entirely.

**Dimensions to limit by:** API key or user, IP address, endpoint (an expensive report endpoint deserves a tighter limit than a health check), and tenant or plan tier.

**Distributed enforcement.** With multiple gateway instances, counters must be shared - usually Redis with atomic increments, or a local counter with periodic synchronisation for higher throughput and slightly softer accuracy.

**Client contract.** Communicate limits so clients can behave well:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 42
RateLimit-Policy: "default";q=1000;w=3600
RateLimit: "default";r=0;t=42
```

`Retry-After` is the standardised header every client understands. The `RateLimit-Policy` / `RateLimit` pair comes from the IETF httpapi working-group draft, which is still a draft and replaced the older `RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset` trio that many APIs (and the `X-RateLimit-*` convention) still send - document whichever you emit.

**Related controls:** quotas (longer-period totals, often billing-linked), concurrency limits (in-flight requests rather than rate), and load shedding (dropping low-priority work when the system is saturated).

## Example

```lua
-- Token bucket in Redis, run atomically with EVAL/EVALSHA.
-- KEYS[1] = bucket key (e.g. "rl:{api-key}"), ARGV[1] = capacity, ARGV[2] = refill tokens/second
local capacity = tonumber(ARGV[1])
local rate     = tonumber(ARGV[2])
local t        = redis.call('TIME')                       -- server clock, not the client's
local now      = tonumber(t[1]) + tonumber(t[2]) / 1000000
local bucket   = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
local tokens   = tonumber(bucket[1]) or capacity
local ts       = tonumber(bucket[2]) or now

tokens = math.min(capacity, tokens + (now - ts) * rate)   -- refill for elapsed time
local allowed = 0
if tokens >= 1 then
  tokens = tokens - 1
  allowed = 1
end
redis.call('HSET', KEYS[1], 'tokens', tokens, 'ts', now)
redis.call('EXPIRE', KEYS[1], math.ceil(capacity / rate) * 2)  -- idle buckets disappear
return allowed                                             -- 1 = allow, 0 = reject with 429
```

## Interview tips

- Token bucket versus fixed window, and the boundary-burst problem, is the algorithm question interviewers ask.
- Returning `Retry-After` and rate-limit headers shows API design maturity.
- Mention that clients should implement exponential backoff with jitter in response.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
