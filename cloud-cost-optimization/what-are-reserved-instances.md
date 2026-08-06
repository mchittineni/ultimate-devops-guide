---
title: "What are Reserved Instances?"
id: 92
category: "Cloud Cost Optimization"
difficulty: "Beginner"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
---

# What are Reserved Instances?

**Short answer:** Reserved Instances are a billing commitment — you agree to a specific amount of compute for one or three years in exchange for a discount of roughly 30–70% versus on-demand pricing. They are a financial arrangement, not a different kind of server.

## Detail

**Dimensions**

- **Term** — one or three years; three years discounts more.
- **Payment** — all upfront (largest discount), partial upfront, or no upfront.
- **Scope** — regional (flexible across availability zones, no capacity reservation) or zonal (capacity reservation in one AZ).
- **Type** — _standard_ RIs discount most but can only be modified within limits; _convertible_ RIs allow exchange for different instance families at a smaller discount.

**Savings Plans** are the more flexible modern alternative on AWS: you commit to a dollar amount per hour rather than to specific instances. Compute Savings Plans apply across instance families, regions, and even Lambda and Fargate. For most organisations they are the better default; RIs still win where you need a zonal capacity reservation. Azure has Reserved VM Instances and savings plans; GCP has committed use discounts and applies sustained-use discounts automatically.

**How to buy well**

- Analyse at least 30–90 days of steady-state usage first; commit only to the baseline that will genuinely persist.
- Ladder purchases over time rather than committing everything at once, so you are not locked into one architecture.
- Start with one-year, no-upfront commitments while your usage pattern is still changing.
- Monitor utilisation and coverage continuously; an unused commitment is pure loss.
- Combine layers: commitments for the baseline, on-demand for variability, spot for interruptible work.

## Interview tips

- Say explicitly that it is a billing construct — some candidates think a reservation changes the instance.
- Recommend Savings Plans over RIs for most cases, and explain the flexibility trade-off.
- Mention monitoring commitment utilisation; buying is the easy part, keeping coverage right is the ongoing work.

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
