---
title: "What is Change Failure Rate?"
id: 103
category: "DevOps Metrics and KPIs"
difficulty: "Intermediate"
tags:
  - devops
  - devops-metrics-and-kpis
  - interview-questions
---

# What is Change Failure Rate?

**Short answer:** Change failure rate is the percentage of deployments to production that cause a degraded service requiring remediation - a rollback, hotfix, or patch. It is DORA's primary quality metric.

## Detail

**Calculation:** `failed changes / total changes × 100`. Elite teams sit between 0 and 15%; low performers can exceed 40%.

**Defining "failure" is the hard part** - and it must be defined once, written down, and applied consistently:

- Requires a rollback, or
- Requires an unplanned hotfix within a defined window, or
- Causes an incident of a given severity, or
- Breaches an SLO.

A deployment that fails in the pipeline and never reaches production is _not_ a change failure - that is the pipeline working. Counting those punishes teams for having good gates.

**What reduces it**

- **Smaller changes.** The strongest correlation in the DORA data. A ten-line change fails far less often than a ten-thousand-line one.
- **Better automated testing**, especially integration and contract tests that catch cross-service breakage.
- **Progressive delivery.** Canary releases limit a bad change to a fraction of users, and automated analysis catches it before full rollout.
- **Feature flags** - decouple deploy from release so a bad feature is disabled without a deployment.
- **Consistent environments** through IaC, so staging genuinely predicts production.
- **Post-incident learning** that produces systemic fixes rather than "be more careful."

**Beware the perverse incentive.** Optimising change failure rate alone encourages deploying less often - which is exactly wrong. Always read it alongside deployment frequency and lead time.

## Interview tips

- Insist on a written definition of failure; ambiguity makes the metric meaningless.
- "Smaller batches" is the single highest-impact lever - say it with the reason.
- Pair it with throughput metrics explicitly to show you understand balanced measurement.

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
