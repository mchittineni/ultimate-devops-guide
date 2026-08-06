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

- **Fixed window** — count per calendar minute. Simple, but allows a burst of 2× the limit across a window boundary.
- **Sliding window log** — exact, stores timestamps, memory-hungry.
- **Sliding window counter** — weighted blend of the current and previous window; the common production compromise.
- **Token bucket** — tokens refill at a steady rate up to a bucket size; permits controlled bursts. The most widely used.
- **Leaky bucket** — requests drain at a fixed rate, smoothing traffic entirely.

**Dimensions to limit by:** API key or user, IP address, endpoint (an expensive report endpoint deserves a tighter limit than a health check), and tenant or plan tier.

**Distributed enforcement.** With multiple gateway instances, counters must be shared — usually Redis with atomic increments, or a local counter with periodic synchronisation for higher throughput and slightly softer accuracy.

**Client contract.** Communicate limits so clients can behave well:

```http
HTTP/1.1 429 Too Many Requests
RateLimit-Limit: 1000
RateLimit-Remaining: 0
RateLimit-Reset: 42
Retry-After: 42
```

**Related controls:** quotas (longer-period totals, often billing-linked), concurrency limits (in-flight requests rather than rate), and load shedding (dropping low-priority work when the system is saturated).

## Example

```lua
-- Token bucket in Redis: atomic check-and-consume
local tokens = tonumber(redis.call('get', KEYS[1]) or ARGV[1])
if tokens < 1 then return 0 end
redis.call('decr', KEYS[1])
return 1
```

## Interview tips

- Token bucket versus fixed window, and the boundary-burst problem, is the algorithm question interviewers ask.
- Returning `Retry-After` and rate-limit headers shows API design maturity.
- Mention that clients should implement exponential backoff with jitter in response.

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
