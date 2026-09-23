---
title: "What is Rate Limiting and how do Token Bucket and Leaky Bucket algorithms differ?"
id: 595
category: "Scalability and High Availability"
difficulty: "Intermediate"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - rate-limiting
  - algorithms
  - redis
  - api-gateway
quiz:
  stem: "What is the primary operational difference between the Token Bucket and Leaky Bucket rate limiting algorithms?"
  options:
    - "Token Bucket can only be implemented in Python, while Leaky Bucket is written in C"
    - "Token Bucket accommodates traffic bursts up to its token capacity, whereas Leaky Bucket forces requests to leave at a strictly uniform rate"
    - "Leaky Bucket does not reject requests when full"
    - "Token Bucket requires dedicated hardware appliances"
  answer: 2
  explanation: "Token Bucket permits momentary traffic bursts as long as tokens have accumulated. Leaky Bucket processes requests at a constant, fixed rate, smoothing out all bursts."
---

# What is Rate Limiting and how do Token Bucket and Leaky Bucket algorithms differ?

**Short answer:** Rate limiting protects APIs from abuse and overload; Token Bucket allows bursts of traffic up to the bucket capacity while replenishing tokens at a constant rate; Leaky Bucket processes requests at a strictly constant rate, smoothing out bursts into a steady output stream.

## Detail

Choosing the right algorithm depends on whether bursts of traffic are acceptable to the thing you are protecting.

### Token bucket

- A bucket holds up to $b$ tokens (the burst size).
- Tokens are added at a constant fill rate $r$ (e.g. 10 tokens/s), capped at $b$.
- When a request arrives, if a token is available it is consumed and the request proceeds immediately; if the bucket is empty the request is rejected with `429 Too Many Requests`.
- **Property**: allows bursts. A client that has been idle can send $b$ requests at once, then is held to $r$ per second on average. Implementation needs only two values per key - token count and last-refill timestamp - with refill computed lazily on each request.

### Leaky bucket

- Requests enter a FIFO queue (the bucket) of fixed size.
- They leave for the backend at a **strictly constant rate**, however fast they arrive.
- If the queue is full, new requests are dropped.
- **Property**: smooths traffic. The backend never sees a spike, at the cost of added queueing latency for bursty but legitimate clients. (The "leaky bucket as a meter" variant rejects instead of queueing, and is mathematically equivalent to a token bucket.)

### Window-based alternatives

- **Fixed window** (count per calendar minute): trivial, but allows $2\times$ the limit across a window boundary.
- **Sliding window log / sliding window counter**: removes the boundary burst; the counter version approximates it by weighting the previous window's count.

### Distributed rate limiting

With many gateway replicas, a per-instance limit multiplies by the replica count. A shared store fixes that: Redis with a Lua script (or a function) that reads, refills, and decrements in one atomic step, avoiding read-modify-write races without distributed locks. The trade-off is a network hop per request and a dependency - decide in advance whether the limiter **fails open** (allow traffic if Redis is down) or **fails closed**. Envoy's global rate limit service and most API gateways implement exactly this pattern.

**Where it is used.** Token bucket is the common choice for public APIs because it tolerates normal client burstiness - AWS API Gateway throttling and Stripe's API limiter are token-bucket based. NGINX's `limit_req` is a leaky bucket; with `burst` and `nodelay` it behaves like a token bucket.

**Always tell the client.** Return `429` with `Retry-After`, and ideally the `RateLimit`/`RateLimit-Policy` headers (an IETF draft) or the widely used `X-RateLimit-*` headers, so well-behaved clients back off instead of retrying blindly.

## Example

```lua
-- Redis token bucket, atomic. KEYS[1] = bucket key; ARGV = rate/s, burst, cost.
-- EVALSHA <sha> 1 rl:user:42 10 50 1  -> 1 allowed, 0 rejected
local rate, burst, cost = tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3])
local t = redis.call("TIME")                      -- server clock, not client clocks
local now = tonumber(t[1]) + tonumber(t[2]) / 1e6

local state = redis.call("HMGET", KEYS[1], "tokens", "ts")
local tokens = tonumber(state[1]) or burst
local ts = tonumber(state[2]) or now

tokens = math.min(burst, tokens + (now - ts) * rate)  -- lazy refill
local allowed = tokens >= cost
if allowed then tokens = tokens - cost end

redis.call("HSET", KEYS[1], "tokens", tokens, "ts", now)
redis.call("EXPIRE", KEYS[1], math.ceil(burst / rate) * 2)  -- idle keys clean up
return allowed and 1 or 0
```

```nginx
# NGINX leaky bucket: 10 r/s per client IP, queue up to 20, reject the rest with 429.
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_status 429;

server {
    location /api/ {
        limit_req zone=api burst=20 nodelay; # nodelay: serve the burst now, token-bucket style
        proxy_pass http://api_backend;
    }
}
```

## Interview tips

- One line each: token bucket permits bursts up to $b$ then averages $r$; leaky bucket enforces a constant output rate.
- Explain the storage cost - token bucket needs only a count and a timestamp per key, refilled lazily.
- For multiple gateway replicas, say "shared store with an atomic script" and state the fail-open versus fail-closed decision.
- Mention the fixed-window boundary problem and sliding windows as the fix.
- Return `429` with `Retry-After` so clients can back off; rate limiting without client cooperation just converts load into retries.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
