---
title: "What is Deployment Frequency?"
id: 104
category: "DevOps Metrics and KPIs"
difficulty: "Beginner"
tags:
  - devops
  - devops-metrics-and-kpis
  - interview-questions
---

# What is Deployment Frequency?

**Short answer:** Deployment frequency is how often an organisation successfully releases to production. It is the headline throughput metric, and a proxy for batch size — frequent deployment means small, low-risk changes.

## Detail

**The DORA bands**

| Performance level | Deployment frequency                     |
| ----------------- | ---------------------------------------- |
| Elite             | On demand — multiple deploys per day     |
| High              | Between once per day and once per week   |
| Medium            | Between once per week and once per month |
| Low               | Fewer than once per month                |

**Why it matters beyond speed.** Deployment frequency is really a measure of batch size and of how much friction sits between a developer and production. High frequency requires automated testing, automated deployment, trunk-based development, and low-risk release mechanics — so a high number is evidence that all of those exist.

**What increases it**

- Trunk-based development with short-lived branches.
- A fast, reliable pipeline (under ten minutes for CI).
- Automated deployment with automated rollback.
- Feature flags, so a deploy does not have to wait for a feature to be finished.
- Removing manual approval gates that add delay without adding information.
- Decoupled services that can be released independently.

**Measure it honestly.** Count deployments that actually reach production and serve users. Exclude configuration-only no-ops if they inflate the number, and measure per service or per team rather than as one company-wide total, which averages away the signal.

**The trap:** chasing the number by splitting one release into five deployments. Because it is easily gamed, it is only meaningful next to change failure rate and lead time.

## Interview tips

- Frame it as a proxy for batch size and delivery friction, not as a vanity number.
- Name the practices that unlock it rather than just the target.
- Mention measuring per service — aggregate figures hide the teams that are stuck.

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
