---
title: "How do you load test safely against production?"
id: 298
category: "Performance Testing"
difficulty: "Advanced"
tags:
  - devops
  - performance-testing
  - interview-questions
---

# How do you load test safely against production?

**Short answer:** Only with an abort mechanism you have tested, and never as a first step. Get authorisation and a window, tag synthetic traffic so it is identifiable and excluded from business data, start from a tiny fraction of production volume and ramp, define automatic kill conditions tied to real user SLOs, isolate side effects (no real payments, no real emails, no polluted analytics), and have one person whose only job is to stop the test. The reason to do it at all is that staging never reproduces production's data volume, cache state, noisy neighbours, or dependency behaviour - so some questions can only be answered there.

## Detail

**Earn the right first.** Before touching production: a load test in a production-shaped environment, capacity headroom measured, an incident channel open, on-call informed, a rollback and abort plan, and written sign-off from the service owner. Testing in production without authorisation is indistinguishable from an attack, and cloud providers may require notification for high-volume tests.

**Tag everything synthetic.** A header (`X-Synthetic: true`) or a dedicated tenant that propagates through every hop and shows up in logs, metrics, and traces. Downstream systems use it to route to sandboxes, analytics uses it to exclude the traffic, and your dashboards use it to separate synthetic from real p99. Without this tag, you cannot tell whose latency you are looking at, and your business metrics are corrupted for the day.

**Isolate the side effects.** Enumerate every write and external call the tested path makes, then decide for each: writes go to a synthetic tenant whose rows are cleaned up afterwards; payment providers get their sandbox credentials; emails and SMS are dropped at the gateway; webhooks to customers are suppressed; recommendation and ML training pipelines exclude the synthetic tenant. Missed items in this list are how a load test sends 40,000 real order-confirmation emails.

**Ramp, with automatic kill conditions.** Never start at target load. A staircase - 1%, 5%, 10%, 25%, 50% of production volume, holding each step long enough for autoscaling and caches to settle - lets you find the knee before you cross it. The kill conditions must be evaluated automatically and phrased in terms of _real users_, not test results: real-user error rate above baseline, real-user p99 latency past the SLO, error budget burn rate above a threshold, database replication lag, saturation of a shared dependency. And the abort must be genuinely one action - kill the load generator, and if the test used a canary or shadow route, remove the route.

**Choose the technique that matches the question.**

| Technique                             | What it does                                                  | Risk                                        |
| ------------------------------------- | ------------------------------------------------------------- | ------------------------------------------- |
| **Synthetic canary**                  | Small constant probe traffic, always on                       | Minimal                                     |
| **Shadow / mirror**                   | Duplicate real traffic to a parallel stack, discard responses | Low - but downstream writes must be stubbed |
| **Canary load**                       | Extra load onto one canary instance or cell only              | Low, bounded blast radius                   |
| **Load on a spare cell**              | Full-scale test on production infra with no real users        | Low, needs cell architecture                |
| **Full production load**              | Extra traffic onto the live fleet                             | High - the option of last resort            |
| **Load shedding / failure injection** | Reduce capacity instead of adding traffic                     | Medium - fast, and very informative         |

Reducing capacity is underrated: taking one AZ or a fraction of the fleet out of service tells you the same thing about headroom as adding traffic, is easier to reverse, and simultaneously validates your failover path.

**Measure the right things.** Compare _real user_ SLIs before, during, and after - that is the safety signal. Compare synthetic p50/p95/p99 for the performance answer, along with saturation of each tier (CPU, connection pools, queue depth, thread pools, database locks) so you find which resource is the actual limit. Watch autoscaling behaviour: how long a scale-up takes end to end is often the most valuable output of the whole exercise, because it is the number that determines whether a real traffic spike becomes an incident.

**Write it up.** The deliverables are the breaking point, the first bottleneck, the scale-up latency, and any bug the test surfaced (connection leaks, unbounded queues, missing timeouts, cache stampedes on cold start). Then feed the numbers back into capacity planning and the autoscaling configuration - a load test whose results do not change a configuration was an expensive way to feel reassured.

## Example

```javascript
// k6: tagged synthetic traffic, staircase ramp, thresholds that abort the test.
import http from "k6/http";
import { check } from "k6";

export const options = {
  stages: [
    { duration: "5m", target: 50 }, // ~1% of production rps
    { duration: "10m", target: 250 },
    { duration: "10m", target: 500 },
    { duration: "10m", target: 1000 }, // stop here unless everything is clean
  ],
  thresholds: {
    // abortOnFail stops the generator the moment the system is in trouble
    http_req_failed: [{ threshold: "rate<0.01", abortOnFail: true, delayAbortEval: "30s" }],
    http_req_duration: [{ threshold: "p(99)<800", abortOnFail: true, delayAbortEval: "1m" }],
  },
};

export default function () {
  const res = http.get("https://api.example.com/orders", {
    headers: {
      "X-Synthetic": "true", // propagated through every hop
      "X-Tenant-Id": "synthetic-loadtest", // sandboxed writes
      Authorization: `Bearer ${__ENV.SYNTHETIC_TOKEN}`,
    },
    tags: { test: "orders-ramp-2026-08-07" },
  });
  check(res, { "status 200": (r) => r.status === 200 });
}
```

```promql
# The real kill switch: real-user impact, not test metrics. Page and abort on these.
- alert: LoadTestHarmingRealUsers
  expr: |
    (
      sum(rate(http_requests_total{synthetic!="true",status=~"5.."}[2m]))
        / sum(rate(http_requests_total{synthetic!="true"}[2m])) > 0.005
    )
    or histogram_quantile(0.99,
         sum by (le) (rate(http_request_duration_seconds_bucket{synthetic!="true"}[2m]))) > 0.5
    or max(pg_replication_lag_seconds) > 30
  for: 1m
  labels: { severity: page, action: abort_load_test }
```

```bash
# Abort must be one action, and rehearsed before the test starts.
kubectl delete job/loadtest-orders               # stop generation
kubectl argo rollouts abort api                  # controller-level abort: traffic back to stable
# An annotation would only change metadata - the traffic controller ignores it. Use the
# rollout's own abort verb, then confirm the split actually moved before you believe it:
kubectl argo rollouts get rollout api            # canary weight must read 0 / stable 100
# Then confirm recovery on real-user SLIs before declaring the test over.

# The alternative test: remove capacity instead of adding traffic.
kubectl scale deploy/api --replicas=6            # from 10 - measures headroom, easily undone
aws elbv2 deregister-targets --target-group-arn $TG --targets Id=i-0abc  # one AZ out
```

## Interview tips

- Say "not as a first step" and list the prerequisites - a staging test, authorisation, on-call informed, a rehearsed abort. Enthusiasm without governance is the wrong answer here.
- Tagging synthetic traffic end to end is the detail that shows you have actually done it. Explain both uses: downstream routing and clean dashboards.
- Enumerate the side effects (payments, emails, webhooks, analytics, ML training). The order-confirmation-email disaster is a story every interviewer recognises.
- Kill conditions must be expressed in real-user SLIs, not test results. That distinction is the core safety insight.
- Offer capacity reduction as a lower-risk alternative that also tests failover. It is a strong, slightly unexpected answer.
- Name the reason production testing exists at all: data volume, cache state, real dependency behaviour, noisy neighbours - things staging cannot fake.
- Finish with the deliverables, especially autoscaling scale-up latency, and say that results must change a configuration to have been worth it.

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
