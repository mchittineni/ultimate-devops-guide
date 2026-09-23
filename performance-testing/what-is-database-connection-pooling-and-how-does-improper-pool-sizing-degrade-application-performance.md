---
title: "What is Database Connection Pooling and how does improper pool sizing degrade application performance?"
id: 613
category: "Performance Testing"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - performance-testing
  - databases
  - connection-pooling
  - hikari
  - postgres
  - performance
quiz:
  stem: "Why does setting an application's database connection pool size to 500 on an 8-core database server frequently cause query latency to skyrocket?"
  options:
    - "Database engines shut down when handling more than 50 connections"
    - "The 8 CPU cores become overwhelmed by thread context-switching overhead and disk I/O contention trying to execute 500 tasks simultaneously"
    - "Network routers drop TCP connections with pool numbers higher than 100"
    - "Connection poolers only work with single-threaded applications"
  answer: 2
  explanation: "Hardware CPUs can only execute as many threads simultaneously as physical cores exist. Over-allocating connections forces the kernel to spend CPU time thrashing between context switches."
---

# What is Database Connection Pooling and how does improper pool sizing degrade application performance?

**Short answer:** Connection pooling maintains a cache of pre-established, reusable database connections; setting pool sizes too large overwhelms the database with context switching and disk I/O contention, while setting them too small starves application threads.

## Detail

Creating a new database TCP connection is extraordinarily expensive:

- TCP 3-way handshake + TLS negotiation.
- The database authenticates the client and allocates per-connection memory; PostgreSQL goes further and forks a whole backend process per connection (MySQL uses a thread per connection), so idle connections still cost server memory.

### The Pool Sizing Paradox

Many engineers believe: _'We have 500 web threads, so we need a database pool size of 500!'_ **This is wrong and destructive.**

### The Starting-Point Formula (PostgreSQL wiki, popularised by HikariCP)

```text
connections = (core_count * 2) + effective_spindle_count
```

On an 8-core database server with SSD storage, that gives roughly `(8 * 2) + 1 = 17` active connections. It is a starting point for load testing, not a law - workloads that spend most of their time waiting on I/O or network tolerate more.

**The number is per database, not per application instance.** Twenty pods each with a pool of 20 is 400 connections at the database. That is why fleets put **PgBouncer** (or RDS Proxy) in transaction-pooling mode between many small application pools and a small number of real server connections.

### Why Smaller is Faster

If 500 queries execute concurrently on an 8-core CPU, only 8 can run at any instant; the rest add context switching, cache thrashing, and lock and buffer contention, so each query takes longer and throughput falls. Capping concurrency near the hardware's real parallelism means the excess requests wait briefly in the application's pool queue instead, which usually gives higher throughput and lower p99 latency.

**Too small is also a failure mode.** If the pool is smaller than genuine concurrent demand (or connections are held during slow external calls), requests queue for a connection and time out - watch pool wait time and pending-connection metrics, not just database CPU.

## Example

HikariCP settings for one application instance, sized with the whole fleet in mind:

```yaml
# Spring Boot application.yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10        # x 6 replicas = 60 server connections in total
      minimum-idle: 10             # fixed-size pool: HikariCP recommends min = max
      connection-timeout: 2000     # ms to wait for a free connection before failing fast
      max-lifetime: 1800000        # recycle before any proxy/LB idle timeout
```

```ini
; pgbouncer.ini - many client connections, few server connections
[pgbouncer]
pool_mode = transaction
max_client_conn = 2000
default_pool_size = 20
```

## Interview tips

- Connection creation overhead (handshakes, TLS, process forking, buffer allocation).
- The counter-intuitive reality that small pools outperform massive pools.
- CPU context switching and disk lock contention on oversized pools.
- Connection poolers like PgBouncer or HikariCP.
- Multiply pool size by replica count and compare it with `max_connections` - it is the most common real outage in this area, especially during a deploy when old and new pods overlap.
- Transaction pooling breaks session state (session-level prepared statements, `SET`, advisory locks), so mention that trade-off when you recommend PgBouncer.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
