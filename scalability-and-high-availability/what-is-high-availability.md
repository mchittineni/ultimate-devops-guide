---
title: "What is High Availability?"
id: 57
category: "Scalability and High Availability"
difficulty: "Beginner"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
---

# What is High Availability?

**Short answer:** High availability is designing a system to remain operational despite component failures, by removing single points of failure, adding redundancy, and detecting and routing around failures automatically.

## Detail

**Availability targets** and what they permit per year:

| Target                 | Downtime/year | Downtime/month |
| ---------------------- | ------------- | -------------- |
| 99%                    | 3.65 days     | 7.2 hours      |
| 99.9% ("three nines")  | 8.77 hours    | 43.8 minutes   |
| 99.95%                 | 4.38 hours    | 21.9 minutes   |
| 99.99% ("four nines")  | 52.6 minutes  | 4.4 minutes    |
| 99.999% ("five nines") | 5.26 minutes  | 26 seconds     |

Each nine costs materially more. The right target comes from what the business loses per minute of downtime, not from ambition.

**Techniques**

- **Redundancy** — N+1 or N+2 instances, across availability zones. Active-active (all serving) or active-passive (standby ready).
- **Load balancing with health checks** — unhealthy instances are removed from rotation automatically.
- **Failover** — automatic promotion of a replica when a primary fails; database managed services do this in tens of seconds.
- **Graceful degradation** — shed non-essential features rather than failing entirely (serve cached content, disable recommendations).
- **Resilience patterns** — timeouts, retries with exponential backoff and jitter, circuit breakers, bulkheads.
- **No single points of failure** — including in the "boring" layers: DNS, certificates, the deployment pipeline, and the monitoring system itself.

**HA is not DR.** High availability handles component failure within an environment, typically automatically and in seconds. Disaster recovery handles the loss of an entire site or region, typically with a documented procedure and a much longer RTO.

## Interview tips

- Know the nines table well enough to reason about it out loud.
- Always mention that dependencies (DNS, certs, third-party APIs) are part of your availability.
- Distinguish HA from DR clearly — it is a frequently tested distinction.

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
