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

**Short answer:** Reserved Instances are a billing commitment - you agree to a specific amount of compute for one or three years in exchange for a discount of roughly 30–70% versus on-demand pricing. They are a financial arrangement, not a different kind of server.

## Detail

**Dimensions**

- **Term** - one or three years; three years discounts more.
- **Payment** - all upfront (largest discount), partial upfront, or no upfront.
- **Scope** - regional (flexible across availability zones, no capacity reservation) or zonal (capacity reservation in one AZ).
- **Type** - _standard_ RIs discount most but can only be modified within limits; _convertible_ RIs allow exchange for different instance families at a smaller discount.

**Savings Plans** are the more flexible modern alternative on AWS: you commit to a dollar amount per hour rather than to specific instances. Compute Savings Plans apply across instance families, regions, and even Lambda and Fargate. For most organisations they are the better default for compute; zonal RIs are the legacy way to combine a discount with a capacity reservation (On-Demand Capacity Reservations plus a Savings Plan is the more flexible modern equivalent). RIs remain the main commitment for services Savings Plans do not cover, such as OpenSearch and Redshift, although Database Savings Plans (December 2025) now cover RDS, Aurora, DynamoDB, ElastiCache, and several other database services on one-year terms. Azure has Reserved VM Instances and savings plans; GCP has committed use discounts and applies sustained-use discounts automatically.

**How to buy well**

- Analyse at least 30–90 days of steady-state usage first; commit only to the baseline that will genuinely persist.
- Ladder purchases over time rather than committing everything at once, so you are not locked into one architecture.
- Start with one-year, no-upfront commitments while your usage pattern is still changing.
- Monitor utilisation and coverage continuously; an unused commitment is pure loss.
- Combine layers: commitments for the baseline, on-demand for variability, spot for interruptible work.

**Trade-off.** The discount is paid for with lock-in: a three-year standard RI on an instance family you migrate away from (to Graviton, to containers, to serverless) keeps billing for its full term. That is why flexibility often matters more than the last few percentage points.

## Example

```bash
# What would a commitment cover, and how well are existing ones used?
aws ce get-reservation-purchase-recommendation --service "Amazon Elastic Compute Cloud - Compute" \
  --term-in-years ONE_YEAR --payment-option NO_UPFRONT --lookback-period-in-days SIXTY_DAYS

aws ce get-reservation-utilization --time-period Start=2026-08-01,End=2026-09-01 \
  --query 'Total.UtilizationPercentage'     # below ~95%: you are paying for idle reservations
aws ce get-reservation-coverage --time-period Start=2026-08-01,End=2026-09-01 \
  --query 'Total.CoverageHours.CoverageHoursPercentage'
```

## Interview tips

- Say explicitly that it is a billing construct - some candidates think a reservation changes the instance.
- Recommend Savings Plans over RIs for most cases, and explain the flexibility trade-off.
- Mention monitoring commitment utilisation; buying is the easy part, keeping coverage right is the ongoing work.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
