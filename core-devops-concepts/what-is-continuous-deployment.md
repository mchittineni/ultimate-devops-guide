---
title: "What is Continuous Deployment?"
id: 5
category: "Core DevOps Concepts"
difficulty: "Intermediate"
tags:
  - devops
  - core-devops-concepts
  - interview-questions
---

# What is Continuous Deployment?

**Short answer:** Continuous Deployment removes the manual approval from continuous delivery: every change that passes the automated pipeline goes to production automatically, with no human in the loop.

## Detail

Continuous Deployment is the same pipeline as continuous delivery, minus the button. That single difference raises the bar on everything upstream, because the automated tests are now the _only_ thing standing between a commit and customers.

What it demands:

- **Comprehensive automated testing** - unit, integration, contract, and smoke tests you genuinely trust.
- **Progressive delivery** - canary releases or blue/green deployments so a bad change reaches 1% of traffic, not 100%.
- **Automated verification and rollback** - the pipeline watches error rate and latency after deploy and reverts on its own if the release fails its health criteria.
- **Feature flags** - decoupling _deploy_ from _release_ so unfinished work can ship dark and be enabled separately.
- **Strong observability** - you cannot auto-rollback on signals you do not collect.

It is not right for everyone. Regulated environments, on-premises software shipped to customers, and mobile app store releases often stop at continuous delivery deliberately.

## Example

```yaml
# Argo Rollouts canary: 10% → analysis → 50% → analysis → 100%
strategy:
  canary:
    steps:
      - setWeight: 10
      - analysis:
          templates:
            - templateName: success-rate # aborts + rolls back below threshold
      - setWeight: 50
      - pause: { duration: 10m }
      - setWeight: 100
```

## Interview tips

- Say plainly that the prerequisite is test and observability maturity, not a tool.
- Feature flags are the answer to "how do you ship unfinished work continuously?"
- Have a view on when _not_ to use it - that judgement reads as senior.

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
