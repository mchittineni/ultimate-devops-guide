---
title: "What are the core capabilities measured by DORA metrics and why do they correlate with high performance?"
id: 512
category: "Core DevOps Concepts"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - core-devops-concepts
  - dora
  - metrics
  - performance
quiz:
  stem: "According to DORA research, what is the relationship between software delivery speed and production stability?"
  options:
    - "Faster delivery frequency inevitably causes higher change failure rates"
    - "Elite teams achieve both higher deployment frequency and lower change failure rates simultaneously"
    - "Stability can only be maintained by enforcing monthly release change advisory boards"
    - "Lead time for changes has no measurable correlation with mean time to recovery"
  answer: 2
  explanation: "DORA findings conclusively demonstrate that elite organizations do not compromise stability for speed; small, frequent deployments minimize blast radius and accelerate recovery."
---

# What are the core capabilities measured by DORA metrics and why do they correlate with high performance?

**Short answer:** DORA's delivery metrics measure throughput (Deployment Frequency, Lead Time for Changes, Failed Deployment Recovery Time) and instability (Change Failure Rate, Rework Rate), and its research consistently finds that the best teams achieve high speed AND high stability together. The metrics are outcomes; the _capabilities_ - technical, process, and cultural practices such as trunk-based development, continuous delivery, loosely coupled architecture, and a generative culture - are what drive them.

## Detail

The DevOps Research and Assessment (DORA) team established four key metrics, added **rework rate** as a fifth in 2024, and tracks operational **reliability** alongside them:

1. **Deployment Frequency**: How often code is successfully deployed to production (top teams: on demand, multiple times per day).
2. **Lead Time for Changes**: Time from code commit to code running in production (top band: less than one day in recent reports; it was less than one hour in 2021).
3. **Change Failure Rate (CFR)**: Percentage of deployments causing a degradation or outage requiring remediation (top cluster around 5% in 2024; older reports quoted 0-15%).
4. **Failed Deployment Recovery Time** (formerly Time to Restore Service / MTTR, renamed in 2023): Time taken to recover from a deployment that impaired production (top band: less than one hour).
5. **Rework Rate** (2024): Share of deployments that are unplanned fixes for production issues.

The 2025 DORA report retired the elite/high/medium/low tiers in favour of seven team archetypes that also weigh burnout and friction, so quote the bands as a scale, not a grade.

### Capabilities, not just metrics

DORA's research model links roughly thirty capabilities to delivery performance, for example:

- **Technical**: version control, trunk-based development, continuous integration, test automation, deployment automation, loosely coupled architecture, database change management.
- **Process**: small batches, streamlined change approval (peer review over change advisory boards), visibility of work, customer feedback.
- **Cultural**: generative (Westrum) culture, learning climate, job satisfaction, transformational leadership.
- **AI era (2025)**: the DORA AI Capabilities Model adds items such as a clear AI stance, healthy data ecosystems, and strong version control practices, finding that AI amplifies whatever the team already does well or badly.

The crucial insight is that speed and reliability are not trade-offs. Small batch sizes reduce blast radius, make code reviews faster, and make debugging easier - so the same capabilities improve both.

**Limitation.** DORA's findings come from large annual surveys: they show strong, repeated correlations, not controlled proof of causation, and the benchmark numbers are self-reported. Use the metrics to track your own trend, not to rank teams.

## Example

Grouping the five delivery metrics as DORA's 2024 model does, from a deployments table:

```sql
SELECT service,
       count(*) / 13.0                                             AS deploys_per_week,     -- throughput
       percentile_cont(0.5) WITHIN GROUP (ORDER BY deployed_at - first_commit_at) AS median_lead_time, -- throughput
       percentile_cont(0.5) WITHIN GROUP (ORDER BY recovered_at - deployed_at)
         FILTER (WHERE caused_failure)                             AS median_recovery_time, -- throughput
       avg(caused_failure::int)                                    AS change_failure_rate,  -- instability
       avg(is_unplanned_fix::int)                                  AS rework_rate           -- instability
  FROM deployments
 WHERE environment = 'production' AND deployed_at >= now() - interval '13 weeks'
 GROUP BY service;
```

## Interview tips

- Naming the metrics (Deployment Frequency, Lead Time, Change Failure Rate, Failed Deployment Recovery Time) plus Rework Rate added in 2024.
- The synergy between throughput and stability (not a zero-sum game).
- Small batch sizes as the root enabler of high performance.
- Distinguishing metrics (outcomes) from capabilities (what you change to move them).
- Knowing the tiers were retired in 2025 and the data is correlational.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
