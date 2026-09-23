---
title: "How is Deployment Frequency calculated and what engineering practices increase it safely?"
id: 649
category: "DevOps Metrics and KPIs"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - devops-metrics-and-kpis
  - metrics
  - dora
  - deployment-frequency
quiz:
  stem: "What is the primary counter-intuitive finding of DORA research regarding high deployment frequency?"
  options:
    - "Teams that deploy multiple times per day have lower change failure rates than teams deploying once a month"
    - "High deployment frequency requires quadrupling the QA testing team"
    - "Deploying frequently is only possible for static websites"
    - "Frequent deployments make software development more expensive"
  answer: 1
  explanation: "DORA research proved that elite teams achieve both higher deployment frequency AND lower change failure rates simultaneously, because small batches are easier to review, test, and debug."
---

# How is Deployment Frequency calculated and what engineering practices increase it safely?

**Short answer:** Deployment Frequency measures how often code is deployed to production (or released to app stores); teams increase it safely by shrinking batch sizes, using automated testing in CI, adopting trunk-based development, and decoupling deployment from release via feature flags.

## Detail

Deployment frequency is the primary throughput metric in the DORA framework:

### DORA Performance Tiers (2024 benchmarks)

- **Elite**: Multiple deploys per day on-demand.
- **High**: Between once per day and once per week.
- **Medium**: Between once per week and once per month.
- **Low**: Between once per month and once every six months.

The 2025 DORA report dropped these tiers in favour of seven team archetypes that combine delivery metrics with well-being and friction, so use them as a rough scale rather than a grade.

**Calculation.** Count successful deployments to production per service (or per team) per period, from the deployment system rather than self-reporting. Many teams also report "deployment days" (the share of working days with at least one deploy), which is harder to inflate by splitting one change into five deploys.

### How to Increase Frequency Without Causing Outages

Low-performing organizations bundle 200 features into a massive monthly release, resulting in high-risk deployments that require weekend war rooms.

- **Small Batch Sizes**: Deploying 5-line pull requests multiple times a day reduces blast radius. If a bug occurs, identifying the culprit commit is trivial.
- **Automated CI Safety Net**: Fast (< 10 min) comprehensive unit and integration tests.
- **Feature Flags**: Merging incomplete features disabled behind flags avoids holding long-lived feature branches.
- **Progressive delivery and automated rollback**: canaries with automated analysis keep a bad deploy's blast radius small, so more deploys do not mean more incidents.

**Trade-off.** Frequency without the safety net just ships bugs faster, and flags carry their own debt (stale flags, untested combinations), so frequency is only meaningful next to change failure rate.

## Example

Deploy count and deployment days per service per week:

```sql
SELECT service,
       date_trunc('week', deployed_at)        AS week,
       count(*)                               AS deploys,
       count(DISTINCT deployed_at::date)      AS deployment_days
  FROM deployments
 WHERE environment = 'production' AND status = 'succeeded'
 GROUP BY 1, 2
 ORDER BY 2 DESC, 3 DESC;
```

## Interview tips

- DORA benchmark: Elite teams deploy multiple times per day.
- Reducing batch size as the primary catalyst for safe frequency increases.
- Feature flags decoupling code merging from feature activation.
- Fast, reliable CI automated testing.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
