---
title: "What is Change Failure Rate (CFR) and how is it distinguished from internal test failures?"
id: 651
category: "DevOps Metrics and KPIs"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - devops-metrics-and-kpis
  - metrics
  - dora
  - change-failure-rate
quiz:
  stem: "Which event counts toward an organization's DORA Change Failure Rate (CFR)?"
  options:
    - "A unit test failing on a developer's feature branch pull request"
    - "A production release that causes a 5xx error spike requiring an emergency rollback or hotfix"
    - "A linter flagging formatting errors during a local pre-commit hook"
    - "A staging environment deployment that fails an end-to-end test"
  answer: 2
  explanation: "CFR measures only changes deployed to production that result in degraded service, rollbacks, or hotfixes. Pre-production test failures are healthy gates and are not counted."
---

# What is Change Failure Rate (CFR) and how is it distinguished from internal test failures?

**Short answer:** Change Failure Rate measures the percentage of changes released to production that result in degraded service, outages, or require immediate remediation (rollback, hotfix); it strictly excludes pre-production CI test failures, which are healthy and expected.

## Detail

CFR measures the quality and safety of releases reaching customers:

```text
CFR = deployments requiring a hotfix, rollback, or incident response / total production deployments x 100%
```

### Critical Distinction

- **CI Test Failures (Healthy)**: A unit test failing on a feature branch in CI is **not** a change failure! That is the CI safety net working as designed.
- **Change Failure (Production Impact)**: A change deployed to production that triggers an incident, burns an error budget, requires a rollback, or forces an emergency hotfix.

### Benchmarks

- The 0-15% "elite" band comes from older DORA reports; in the 2024 report the top cluster sat around **5%** and the lowest around **40%**.
- The 2025 DORA report retired the elite/high/medium/low tiers altogether, so quote these as a scale, not a grade.
- DORA added **rework rate** in 2024 as a companion instability metric: the share of deployments that are unplanned fixes for production issues. It catches failures that were quietly hotfixed and never labelled as incidents.

**Limitation.** CFR depends entirely on the definition of "failure" and on incidents being linked to the deploy that caused them. Without that linkage in the incident tool, the number is guesswork.

## Example

Keep CI failures out of the numerator by only counting production deployments and their linked incidents:

```sql
SELECT round(100.0 * count(DISTINCT d.id) FILTER (WHERE d.rolled_back OR i.id IS NOT NULL)
             / count(DISTINCT d.id), 1) AS cfr_pct
  FROM deployments d
  LEFT JOIN incidents i ON i.caused_by_deploy_id = d.id
 WHERE d.environment = 'production'           -- CI runs never appear in this table
   AND d.status = 'succeeded'                 -- a blocked deploy is the pipeline working
   AND d.deployed_at >= now() - interval '90 days';
```

## Interview tips

- CFR measures production failures, hotfixes, and rollbacks.
- Pre-production CI test failures are NOT counted in CFR (they represent positive safety nets).
- Benchmarks as a scale (top teams around 5%), and awareness that DORA retired the tiers in 2025.
- Pairing CFR with deployment frequency to measure speed + stability balance.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
