---
title: "What is the difference between AWS Savings Plans, Reserved Instances, and On-Demand pricing?"
id: 636
category: "Cloud Cost Optimization"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
  - aws
  - finops
  - savings-plans
  - reserved-instances
  - cost
quiz:
  stem: "Why do cloud architects prefer AWS Compute Savings Plans over Standard Reserved Instances when modernizing microservices?"
  options:
    - "Savings Plans do not require financial commitments"
    - "Compute Savings Plans automatically apply discounts across EC2, AWS Fargate, and AWS Lambda, even if teams switch instance families, operating systems, or regions"
    - "Reserved Instances only function in European regions"
    - "Savings Plans provide free data egress"
  answer: 2
  explanation: "Standard RIs lock teams into specific instance families in specific regions. Compute Savings Plans apply discounts automatically across EC2, Fargate, and Lambda regardless of family or region."
---

# What is the difference between AWS Savings Plans, Reserved Instances, and On-Demand pricing?

**Short answer:** On-Demand is pay-as-you-go with zero commitment at highest cost; Reserved Instances commit to specific instance types in specific regions for 1 or 3 years (up to 72% savings); Savings Plans commit to a consistent dollar spend per hour ($/hr), offering comparable savings with much greater architectural flexibility.

## Detail

AWS offers three ways to pay for the same compute: no commitment (on-demand), a commitment to specific capacity (Reserved Instances), or a commitment to a level of spend (Savings Plans).

### Comparison

| Pricing model                     | Commitment                                                                                                                                             | Flexibility                                                                 | Maximum discount | Risk                                  |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- | ---------------- | ------------------------------------- |
| **On-Demand**                     | None; per-second billing for most Linux instances                                                                                                      | Maximum                                                                     | 0% (baseline)    | No commitment risk; highest unit cost |
| **Standard Reserved Instance**    | 1 or 3 years for an instance family, platform, and tenancy in a region (regional RIs flex across sizes in the family; zonal RIs also reserve capacity) | Low: can modify some attributes, not change family or OS                    | Up to ~72%       | High if the architecture changes      |
| **Convertible Reserved Instance** | 1 or 3 years, exchangeable for other RIs of equal or greater value                                                                                     | Medium                                                                      | Up to ~66%       | Moderate                              |
| **Compute Savings Plan**          | 1 or 3 years of $/hour spend                                                                                                                           | High: any EC2 family, size, OS, tenancy, or region, plus Fargate and Lambda | Up to ~66%       | Low                                   |
| **EC2 Instance Savings Plan**     | 1 or 3 years of $/hour for one instance family in one region                                                                                           | Medium: any size, OS, or tenancy in that family                             | Up to ~72%       | Moderate                              |

The discounts are maxima for three-year, all-upfront terms; one-year, no-upfront commitments save noticeably less.

### How Savings Plans apply

Each hour, AWS applies your committed $/hour to eligible usage at the discounted rates, highest-discount usage first; anything above the commitment is billed at on-demand rates, and any unused commitment in that hour is lost. So a Savings Plan is sized to your **minimum steady usage**, not your average.

### Modern best practice

- **Compute Savings Plans are the default** for EC2, Fargate, and Lambda, because they survive changes of instance family, region, and architecture (x86 to Graviton, EC2 to containers).
- **RIs still matter** for services Savings Plans do not cover - such as OpenSearch and Redshift - and zonal RIs are one way to combine a discount with guaranteed capacity (On-Demand Capacity Reservations plus a Savings Plan is the more flexible alternative).
- **Database Savings Plans** (announced December 2025) extend the $/hour model to RDS, Aurora, DynamoDB, ElastiCache, DocumentDB, Neptune, and others, on one-year terms with smaller discounts than compute - reducing the need for per-engine RIs.
- **Ladder purchases** (buy in tranches over months), start with one-year terms while usage is changing, and review coverage and utilisation monthly.
- **Spot** covers interruptible work on top; commitments should never be sized to include it.

## Example

```bash
# How much should we commit? Recommendation based on the last 30 days of usage.
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT --lookback-period-in-days THIRTY_DAYS \
  --query 'SavingsPlansPurchaseRecommendation.SavingsPlansPurchaseRecommendationSummary.
           {commit:HourlyCommitmentToPurchase,monthlySavings:EstimatedMonthlySavingsAmount,
            utilisation:EstimatedAverageUtilization}'

# Are the plans we already own fully used, and how much usage do they cover?
aws ce get-savings-plans-utilization --time-period Start=2026-08-01,End=2026-09-01 \
  --query 'Total.Utilization.UtilizationPercentage'
aws ce get-savings-plans-coverage --time-period Start=2026-08-01,End=2026-09-01 \
  --query 'SavingsPlansCoverages[].Coverage.CoveragePercentage'
```

## Interview tips

- One line each: on-demand is no commitment; RIs commit to capacity attributes; Savings Plans commit to $/hour.
- Explain how a Savings Plan is applied hourly and why you size it to the usage floor.
- Compute Savings Plans are the flexible default; name where RIs still matter and mention Database Savings Plans.
- Give the buying discipline: ladder purchases, start with one-year terms, and watch utilisation and coverage.
- Tie it to architecture change: flexible commitments protect savings when moving to Graviton, containers, or serverless.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
