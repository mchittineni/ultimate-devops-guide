---
title: "What is Blue/Green Deployment?"
id: 145
category: "Advanced DevOps & Cloud"
difficulty: "Intermediate"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is Blue/Green Deployment?

**Short answer:** Blue/green deployment runs two identical production environments — one live (blue), one idle with the new version (green) — and switches all traffic at once after verification, giving instant rollback by switching back.

## Detail

**The sequence**

1. Blue serves 100% of production traffic.
2. Deploy the new version to green, which is identical in size and configuration.
3. Run smoke tests and validation against green while it takes no user traffic.
4. Switch traffic — via load balancer target group, DNS, or a Kubernetes Service selector change.
5. Monitor closely. If anything is wrong, switch back to blue immediately.
6. After a confidence period, blue becomes the environment for the next release.

**Strengths:** near-instant rollback (a traffic switch, not a redeploy), full testing in a genuine production environment before exposure, and zero downtime.

**Costs and complications**

- **Double the infrastructure** during the switch window, though only briefly with cloud elasticity.
- **The database is shared.** This is the real difficulty: both versions use the same data store, so schema changes must be backward compatible. Expand/contract migrations are mandatory.
- **In-flight state.** Sessions, long-running requests, and background jobs need to drain gracefully or be externalised.
- **All-or-nothing exposure.** Unlike a canary, the first real user traffic hits the new version at 100%. A problem only visible under real load affects everyone until you switch back.

**Blue/green versus canary:** blue/green gives the fastest rollback; canary gives the smallest blast radius. Many teams combine them — deploy green, shift a small percentage first, then complete the switch.

## Interview tips

- The shared database is the question behind the question — lead with backward-compatible migrations.
- Contrast with canary on rollback speed versus blast radius; that trade-off is the interesting part.
- Mention connection draining and background jobs; they are what actually break in practice.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
