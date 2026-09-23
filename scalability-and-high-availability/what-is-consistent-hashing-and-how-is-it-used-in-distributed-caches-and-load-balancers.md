---
title: "What is Consistent Hashing and how is it used in distributed caches and load balancers?"
id: 592
category: "Scalability and High Availability"
difficulty: "Advanced"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - consistent-hashing
  - caching
  - distributed-systems
  - dynamo
quiz:
  stem: "Why does consistent hashing use 'Virtual Nodes' (vnodes) for each physical server on the hash ring?"
  options:
    - "To reduce memory usage in the caching client"
    - "To distribute keys uniformly across all physical nodes and prevent data hotspots"
    - "To convert HTTP requests into TCP sockets"
    - "To allow physical servers to reboot without downtime"
  answer: 2
  explanation: "Without virtual nodes, random hash placement can leave large gaps on the ring, causing some physical servers to store significantly more keys than others. Vnodes ensure statistical uniformity."
---

# What is Consistent Hashing and how is it used in distributed caches and load balancers?

**Short answer:** Consistent hashing maps both keys and server nodes onto a circular hash ring ($0$ to $2^{32}-1$); adding or removing a node only remaps $K/N$ keys on average, avoiding the catastrophic full-cache invalidation caused by naive modulo hashing.

## Detail

It matters wherever the _same key must keep landing on the same node_: client-side sharding of Memcached, Cassandra and DynamoDB-style partitioning, and "sticky" load balancing for cache locality (Envoy's `RING_HASH` and `MAGLEV` policies, NGINX `hash ... consistent`).

### Why modulo hashing fails

With naive modulo hashing:

$$\text{server} = \text{hash}(\text{key}) \pmod N$$

If you have 10 cache nodes ($N=10$) and 1 node dies ($N=9$), roughly 90% of keys now map to a different server. The cache hit rate collapses and the misses land on the primary database all at once - a cache stampede triggered by a single node failure.

### How consistent hashing works

1. **The hash ring**: nodes and keys are hashed with the same function (MurmurHash3, xxHash, or MD5/SHA for placement only - cryptographic strength is not needed) onto a circular range, e.g. $0$ to $2^{32}-1$.
2. **Key placement**: walk clockwise from the key's position to the first node; that node owns the key.
3. **Adding or removing a node**: when node $C$ is added between $A$ and $B$, only the keys between $A$ and $C$ move to $C$. Every other key stays put - about $K/N$ keys move instead of nearly all of them.
4. **Virtual nodes (vnodes)**: with one position per server, random placement leaves some arcs far larger than others. Giving each physical server 100-200 positions evens out the load statistically, lets you weight bigger servers with more vnodes, and spreads a failed node's keys across _all_ survivors rather than dumping them on one neighbour.

**Alternatives worth knowing.** **Rendezvous (highest-random-weight) hashing** needs no ring - each key picks the node with the highest `hash(key, node)` - and gives perfect minimal movement at $O(N)$ cost per lookup. **Jump consistent hash** is tiny and fast but only supports numbered buckets added or removed at the end. **Maglev** (Google, used by Envoy) builds a lookup table for $O(1)$ lookups and very even spread. And **Redis Cluster does not use a ring at all**: it has 16,384 fixed hash slots (`CRC16(key) mod 16384`) assigned to nodes, and resharding moves whole slots.

**Limitations.** Consistent hashing balances _keys_, not _load_: one hot key still lands on one node, so hot-key handling (local caching, key splitting, replicas for reads) is separate work. Membership changes must be agreed by every client, or two clients will route the same key to different nodes. And "bounded-load" variants are needed if you use it for request routing, so a popular node can overflow to the next one on the ring.

## Example

```python
import bisect
import hashlib


class HashRing:
    def __init__(self, nodes, vnodes=160):
        self.vnodes = vnodes
        self.ring = []  # sorted list of (hash, node)
        for node in nodes:
            self.add(node)

    @staticmethod
    def _hash(value: str) -> int:
        return int.from_bytes(hashlib.md5(value.encode()).digest()[:4], "big")

    def add(self, node):
        for i in range(self.vnodes):
            bisect.insort(self.ring, (self._hash(f"{node}#{i}"), node))

    def remove(self, node):
        self.ring = [(h, n) for h, n in self.ring if n != node]

    def get(self, key: str):
        idx = bisect.bisect(self.ring, (self._hash(key), "")) % len(self.ring)
        return self.ring[idx][1]


ring = HashRing(["cache-a", "cache-b", "cache-c"])
keys = [f"user:{i}" for i in range(10_000)]
before = {k: ring.get(k) for k in keys}
ring.add("cache-d")
moved = sum(before[k] != ring.get(k) for k in keys)
print(f"moved {moved / len(keys):.0%} of keys")  # ~25%, not ~75% as with modulo
```

```nginx
# NGINX: consistent (ketama) hashing so the same URL keeps hitting the same cache node.
upstream cache_tier {
    hash $request_uri consistent;
    server 10.0.2.10:8080;
    server 10.0.2.11:8080;
    server 10.0.2.12:8080;
}
```

## Interview tips

- Start with the modulo failure: changing $N$ remaps almost every key and turns one node failure into a database stampede.
- Explain the ring walk and why only the neighbouring arc moves - roughly $K/N$ keys.
- Vnodes solve two problems: uneven arcs and a failed node's load landing on a single neighbour.
- Correct the common myth: Redis Cluster uses 16,384 hash slots, not a consistent-hash ring.
- Mention rendezvous hashing or Maglev to show breadth, and that consistent hashing does not solve hot keys.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
