---
title: "What are the main caching strategies and how do you keep a cache consistent with the database?"
id: 773
category: "Scalability and High Availability"
difficulty: "Intermediate"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - caching
  - redis
  - performance
---

# What are the main caching strategies and how do you keep a cache consistent with the database?

**Short answer:** The common patterns are **cache-aside** (the application reads the cache, and on a miss loads from the database and populates it), **read-through** (the cache layer loads misses itself), **write-through** (every write goes to the cache and the database synchronously), **write-behind** (writes land in the cache and are flushed to the database asynchronously), and **write-around** (writes skip the cache entirely). Consistency comes from a deliberate invalidation rule - usually "write the database, then **delete** the key", backed by a TTL so any missed invalidation heals itself - plus protection against stampedes and hot keys. A cache is always a trade of freshness for latency and load, so state how stale each piece of data is allowed to be.

## Detail

### The patterns

| Pattern       | Read path                          | Write path                                 | Strength                                    | Weakness                                                      |
| ------------- | ---------------------------------- | ------------------------------------------ | ------------------------------------------- | ------------------------------------------------------------- |
| Cache-aside   | App checks cache, loads DB on miss | App writes DB, then deletes the cache key  | Simple, cache failure is not fatal          | First read after a miss is slow; race windows on invalidation |
| Read-through  | Cache library/provider loads DB    | Usually combined with write-through        | Loading logic in one place                  | Cache layer must understand your data source                  |
| Write-through | Always warm for written keys       | Cache and DB updated in the same operation | Reads after writes are fresh                | Write latency of both stores; caches data nobody reads        |
| Write-behind  | Always warm                        | Cache acknowledges, flushes to DB later    | Fastest writes, absorbs bursts              | Data loss if the cache dies before flushing; ordering is hard |
| Write-around  | Cache-aside reads                  | Writes go only to the DB                   | Does not pollute the cache with cold writes | Recently written data is a guaranteed miss                    |

Cache-aside with Redis or Valkey is the default for most web services. Write-behind is rare outside specialised systems, because a cache node failure becomes data loss.

### Keeping it consistent

- **Delete, do not update, on write.** If two writers both `SET` new values into the cache, their updates can land in the wrong order and leave the old value cached indefinitely. Deleting the key means the next reader repopulates it from the source of truth.
- **Order matters: database first, then delete.** Deleting first lets a concurrent reader load the _old_ value from the database and re-cache it before your write commits.
- **A race remains, so keep a TTL.** A reader that missed, read the old row, and is slow to `SET` can still write a stale value after your delete. Short TTLs bound how long that lasts. Some teams add a second, delayed delete, or version keys (`user:42:v17`) so that stale writes land on a key nobody reads.
- **Invalidate from the change stream for many writers.** When several services write the same data, publish invalidations from the database's change stream (CDC via Debezium, DynamoDB Streams) rather than trusting every code path to remember.
- **Read-your-own-writes.** If a user must see their own change immediately, bypass the cache for that user for a few seconds, or write-through for that key.

### Failure modes interviewers probe

- **Stampede (dog-pile).** A hot key expires and thousands of requests recompute it at once. Add TTL jitter, single-flight locking, and stale-while-revalidate. See [the thundering herd problem](./what-is-the-thundering-herd-problem-and-how-do-jitter-and-exponential-backoff-prevent-it.md).
- **Hot keys.** One key gets more traffic than one cache shard can serve. Use a small in-process cache (milliseconds of TTL) in front of Redis, or replicate the key across shards with a random suffix.
- **Cache as a hidden dependency.** If the database cannot survive the uncached load, a cache flush or cluster restart is an outage. Know your cold-cache capacity, and warm the cache before you shift traffic onto a new cluster.
- **Eviction policy.** Set `maxmemory` and an eviction policy deliberately (`allkeys-lfu` for popularity-skewed data, `volatile-lru` if only TTL'd keys may be evicted). The default `noeviction` turns a full cache into write errors.
- **Penetration.** Repeated lookups for keys that do not exist hit the database every time. Cache negative results briefly, or put a Bloom filter in front.

**Tooling note.** Redis changed licence in 2024 and the Linux Foundation fork **Valkey** became the default engine on several managed services (ElastiCache and MemoryDB offer it at a lower price). Redis 8 then added an AGPL option in 2025. The client protocol and these patterns are the same for both.

## Example

```python
# Cache-aside with safe invalidation (redis-py; works against Redis or Valkey).
import json, random
import redis

r = redis.Redis(host="cache", port=6379, decode_responses=True)
TTL = 300  # seconds: the upper bound on staleness if an invalidation is missed

def get_user(db, user_id: int) -> dict:
    key = f"user:{user_id}"
    cached = r.get(key)
    if cached is not None:
        return json.loads(cached)
    row = db.fetch_user(user_id)                     # source of truth
    # jittered TTL so keys written together do not all expire together
    r.set(key, json.dumps(row), ex=TTL + random.randint(0, 60))
    return row

def update_user_email(db, user_id: int, email: str) -> None:
    db.update_user_email(user_id, email)             # 1. commit to the database first
    r.delete(f"user:{user_id}")                      # 2. then delete - never SET here
```

```bash
# Production settings that decide what happens when the cache fills up.
redis-cli CONFIG SET maxmemory 6gb
redis-cli CONFIG SET maxmemory-policy allkeys-lfu
redis-cli INFO stats | grep -E 'keyspace_(hits|misses)|evicted_keys'   # hit ratio and eviction
```

## Interview tips

- Name the patterns, then say cache-aside is the usual default and explain why: it is simple, and a cache outage degrades performance rather than correctness.
- Give the invalidation rule precisely: write the database, then delete the key, with a TTL as the safety net. Explain why delete beats update (out-of-order writes).
- Admit the remaining race and how you bound it (TTL, versioned keys, CDC-driven invalidation). Saying "the cache is always consistent" is a red flag.
- Bring up stampedes, hot keys, and the cold-cache capacity question - "can the database survive a cache flush?" is a senior-level point.
- Mention measuring the hit ratio and the eviction count, and setting an explicit eviction policy.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[How does Docker BuildKit work and what caching and build features does it unlock?]] (`#515`): [How does Docker BuildKit work and what caching and build features does it unlock?](../docker/how-does-docker-buildkit-work-and-what-caching-and-build-features-does-it-unlock.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
