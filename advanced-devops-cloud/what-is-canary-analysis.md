---
title: "What is Canary Analysis?"
id: 159
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is Canary Analysis?

**Short answer:** Canary analysis is the automated evaluation of a canary release — statistically comparing the new version's metrics against the current version's over a defined period, and promoting or rolling back based on the result rather than on human judgement.

## Detail

**How it fits into a canary release.** A small share of traffic goes to the new version. Canary analysis is the decision step: it collects metrics from both the canary and the baseline, compares them, and returns pass or fail. On pass, traffic increases and the process repeats; on fail, traffic is withdrawn and the release rolls back automatically.

**What is compared**

- **Error rate** — the primary signal, compared as a ratio rather than an absolute count, since the canary serves less traffic.
- **Latency percentiles** — p50, p95, p99.
- **Resource use** — CPU and memory, to catch leaks and regressions.
- **Business metrics** — conversion rate, orders per minute. These catch failures that are invisible to technical metrics.
- **Log-based signals** — exception rates, specific error patterns.

**Doing the comparison properly**

- Compare against a **concurrently running baseline** of the old version, not against yesterday's data — that controls for time-of-day and traffic-mix effects.
- Use statistical comparison (Mann-Whitney U or Kruskal-Wallis, as Kayenta does) rather than raw thresholds, so normal variance does not trigger false rollbacks.
- Allow a **warm-up period** — JIT compilation, cache filling, and connection pool establishment make the first minutes unrepresentative.
- Ensure sufficient traffic volume for the result to mean anything; a canary at 1% of a low-traffic service may never reach significance.

**Tools:** Argo Rollouts with AnalysisTemplates, Flagger, and Spinnaker's Kayenta.

## Example

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: success-rate }
spec:
  metrics:
    - name: success-rate
      interval: 1m
      count: 5
      successCondition: result[0] >= 0.99
      failureLimit: 2 # two failed intervals aborts the rollout
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{job="api",version="canary",status!~"5.."}[2m]))
            / sum(rate(http_requests_total{job="api",version="canary"}[2m]))
```

## Interview tips

- Concurrent baseline comparison rather than historical is the methodological point that matters.
- Statistical significance and warm-up periods show you have tuned this, not just enabled it.
- Include a business metric in the analysis — it is what catches the failures monitoring misses.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
