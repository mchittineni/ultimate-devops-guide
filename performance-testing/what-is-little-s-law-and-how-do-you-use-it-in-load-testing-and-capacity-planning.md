---
title: "What is Little's Law and how do you use it in load testing and capacity planning?"
id: 771
category: "Performance Testing"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - performance-testing
  - capacity-planning
  - queueing-theory
quiz:
  stem: "A service handles 400 requests per second with an average response time of 250 ms. By Little's Law, how many requests are in flight on average?"
  options:
    - "16"
    - "100"
    - "1,600"
    - "400"
  answer: 2
  explanation: "Little's Law says L = lambda x W: 400 requests per second x 0.25 seconds = 100 concurrent requests. That figure sizes thread pools, connection pools, and the virtual users a closed-model load test needs."
---

# What is Little's Law and how do you use it in load testing and capacity planning?

**Short answer:** Little's Law states that in a stable system, **L = λ × W**: the average number of items in the system (concurrency) equals the average arrival rate (throughput) times the average time each item spends in the system (latency). It holds for any stable system regardless of the arrival distribution, which makes it the quickest sanity check in performance work: 2,000 requests per second at 50 ms means about 100 requests in flight, so a pool of 20 workers cannot possibly keep up. Use it to size thread and connection pools, to work out how many virtual users a load test needs, and to check that a test's numbers are internally consistent.

## Detail

**The three quantities.** λ is throughput (requests per second actually completed - in steady state, arrivals equal departures). W is the average time in the system, including queueing. L is the average number concurrently in the system. Know any two and the third follows.

**Sizing concurrency limits.** A database pool serving 500 queries per second at 20 ms each holds on average 500 × 0.02 = **10** connections busy. Average is not peak, so add headroom for variance (often 1.5-2x), but a pool of 200 for that workload is not "safe", it is just a bigger queue at the database. The same arithmetic sizes worker threads, consumer counts for a queue, and in-flight limits on a client.

**Sizing a closed-model load test.** With virtual users that each wait for a response and then think, every VU cycles through response time plus think time, so: **VUs = target RPS × (response time + think time)**. To drive 2,000 RPS with 200 ms responses and 3 s think time you need 2,000 × 3.2 = **6,400 VUs**. If you run 1,000 VUs and see 300 RPS, Little's Law tells you the cycle time is about 3.3 s - and if response time then rises, throughput falls automatically, which is the closed model hiding saturation (coordinated omission).

**Sizing an open-model test.** With an arrival-rate executor, concurrency is an output: at 2,000 RPS and 200 ms, about 400 requests are in flight. Pre-allocate VUs for the bad case: if latency degrades to 2 s, the generator needs 4,000 concurrent VUs to keep the rate, or it starts dropping iterations.

**Validating results.** Measured throughput x measured latency should roughly equal measured concurrency (active VUs, open connections, in-flight requests). When it does not, something is wrong with the measurement: the load generator is saturated, latency is measured at a different point than concurrency, or the system was not in steady state.

**Limitations.** Little's Law is about **averages in steady state**. It says nothing about percentiles or variance, and it does not predict how latency grows with load. For that, queueing models help: in a simple single-server (M/M/1) queue, response time is R = S / (1 - U), where S is service time and U is utilisation - at 50% utilisation latency is 2x service time, at 90% it is 10x. That non-linearity is why capacity plans target utilisation well below 100% and why the latency "knee" appears.

## Example

```python
# Back-of-envelope sizing with Little's Law: L = throughput x time_in_system
def concurrency(rps: float, seconds: float) -> float:
    return rps * seconds

print(concurrency(500, 0.020))        # 10.0  DB connections busy on average
print(concurrency(2000, 0.2 + 3.0))   # 6400  closed-model VUs for 2,000 RPS with 3 s think time
print(concurrency(2000, 2.0))         # 4000  VUs an open-model test needs if latency degrades to 2 s

# M/M/1 response time: how fast latency grows as utilisation rises (service time 20 ms)
for u in (0.5, 0.8, 0.9, 0.95):
    print(u, round(0.020 / (1 - u) * 1000), "ms")   # 40, 100, 200, 400 ms
```

```javascript
// k6 open-model test sized with Little's Law: 2,000 RPS x up to 2 s latency => up to 4,000 VUs
import http from "k6/http";

export const options = {
  scenarios: {
    steady: {
      executor: "constant-arrival-rate",
      rate: 2000,
      timeUnit: "1s",
      duration: "10m",
      preAllocatedVUs: 500, // ~2,000 x 0.2 s expected, plus headroom
      maxVUs: 4000, // enough to hold the rate if latency degrades to 2 s
    },
  },
  thresholds: { dropped_iterations: ["count<1"], http_req_duration: ["p(99)<500"] },
};

export default function () {
  http.get(`${__ENV.BASE_URL}/api/products`);
}
```

## Interview tips

- State it precisely - L = λW, averages, steady state - and do one calculation out loud; interviewers usually ask for the arithmetic.
- Apply it to pools: concurrency needed = throughput x latency, so oversized pools only move the queue; tie it to database connection limits.
- Use it for load-test design: closed-model VUs = RPS x (response time + think time); open-model tests need enough VUs to absorb latency spikes, watched via `dropped_iterations`.
- Use it as a lie detector on results: if throughput x latency does not match observed concurrency, the measurement is broken.
- Name the limits and the follow-up: it says nothing about tails; queueing behaviour such as R = S / (1 - U) explains why latency explodes near full utilisation.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
