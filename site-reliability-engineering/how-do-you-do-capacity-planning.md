---
title: "How do you do capacity planning?"
id: 230
category: "Site Reliability Engineering (SRE)"
difficulty: "Advanced"
tags:
  - devops
  - site-reliability-engineering
  - interview-questions
---

# How do you do capacity planning?

**Short answer:** Establish the unit of demand (requests, orders, active users), measure how much resource one unit consumes through load testing, project demand from organic growth plus known events, then provision for peak with headroom for failure domains and lead times. Autoscaling handles the shape of a normal day; capacity planning handles whether the ceiling is high enough at all.

## Detail

**Find the demand-to-resource ratio empirically.** Load test until latency degrades to find the per-instance saturation point, then express capacity as "one instance serves N requests per second at p99 < 300ms". Without that number, capacity planning is guesswork dressed in spreadsheets. Re-measure after significant releases, because efficiency changes.

**Provision for peak, not average.** Daily peak-to-mean ratios of 3–5× are typical; seasonal businesses see far more. Then add headroom on top: enough to lose a failure domain (with three AZs, each must be able to absorb 50% more load), plus growth during your provisioning lead time. GPU capacity, dedicated circuits, and reserved database classes have lead times measured in weeks - quota increases are the version of this that catches people out most often.

**Quotas are capacity.** Cloud accounts have per-region limits on instances, IP addresses, load balancers, and API rate. A scaling event that hits a quota fails exactly like a shortage of hardware. Capacity planning must include a quota review with headroom, requested well before the traffic event.

**Autoscaling is not a plan.** It reacts within a range you configured, at a speed limited by instance or Pod start-up. It cannot exceed `max`, cannot beat provisioning latency during a sudden spike, and cannot help if a dependency (a database with a fixed connection limit, a third-party API rate limit) is the actual constraint. Plan the `max`, pre-warm before known events, and know which dependency saturates first.

**Model the whole chain.** Extra application instances often just move the bottleneck to database connections, a queue's consumer throughput, or a NAT gateway's port allocation. A capacity model that covers only compute is why "we scaled up and it got worse" happens.

**Tie it to cost and to the error budget.** Headroom costs money; too little costs reliability. State the trade-off explicitly - "we hold 40% headroom, which costs $X per month and covers an AZ loss at peak" - and revisit quarterly with actual traffic. Load-test results plus a documented model are also what let you answer a product launch question in minutes rather than weeks.

## Example

```text
Capacity model - checkout, Black Friday

Measured (load test, 2026-09)
  1 pod  = 850 rps at p99 240 ms   (saturates ~1,000 rps)
  1 pod  = 12 DB connections       pool max 400 -> DB ceiling ≈ 33 pods

Demand projection
  current peak            9,400 rps
  organic growth (12%)   10,500 rps
  event multiplier (2.8x) 29,400 rps  <- planning target
  marketing spike buffer  +15%        33,800 rps

Required
  pods for target         33,800 / 850  = 40 pods
  AZ-loss headroom (3 AZ) 40 x 1.5      = 60 pods
  DB ceiling              33 pods       <-- BINDING CONSTRAINT, not compute
  action                  add read replicas + pgbouncer -> pool to 900 (75 pods)
  quotas                  check vCPU, IPs, NAT ports, ALB rules for 75-pod peak
  pre-warm                scale min replicas to 45 the night before

Verify: replay 33,800 rps against staging with production-shaped data before the event.
```

## Interview tips

- Start from the measured demand-per-resource ratio; anyone can multiply, the measurement is the skill.
- "Autoscaling is not capacity planning" plus the quota point are the two things interviewers listen for.
- Expect: "you scaled the app and it got slower" - the bottleneck moved downstream; describe modelling the whole chain.

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
