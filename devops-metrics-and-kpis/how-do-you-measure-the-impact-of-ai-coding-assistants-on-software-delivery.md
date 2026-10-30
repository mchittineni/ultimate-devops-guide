---
title: "How do you measure the impact of AI coding assistants on software delivery?"
id: 787
category: "DevOps Metrics and KPIs"
difficulty: "Advanced"
tags:
  - devops
  - devops-metrics-and-kpis
  - interview-questions
  - ai-assisted-development
  - dora
  - developer-productivity
---

# How do you measure the impact of AI coding assistants on software delivery?

**Short answer:** Measure the delivery system, not the tool. Track adoption, then the DORA metrics (throughput _and_ instability, especially change failure rate and rework rate), then developer-experience survey data and code-review load, compared against a baseline or a non-adopting cohort. Self-reported speed-ups and vendor metrics such as "acceptance rate" or "percentage of code written by AI" are inputs, not outcomes - DORA's research shows AI can raise throughput while also raising instability.

## Detail

**What the research says.** DORA's 2024 report found that more AI adoption was associated with slightly lower delivery throughput and noticeably lower delivery stability (an estimated -1.5% and -7.2% for every 25% increase in adoption), even as individuals reported more productivity and better documentation and code quality. The 2025 report (_State of AI-assisted Software Development_, around 90% adoption) found throughput now rising with AI use, but instability still rising - and framed AI as an **amplifier** of whatever the organisation already does well or badly. Its DORA AI Capabilities Model names the conditions that turn adoption into benefit: a clear AI stance, healthy data ecosystems, AI-accessible internal data, strong version control practices, working in small batches, a user-centric focus, and quality internal platforms. Separately, a 2025 randomised controlled trial by METR found experienced open-source developers took about 19% _longer_ on tasks with AI tools while believing they were faster - the clearest evidence that perception is not measurement.

**A layered measurement model**

1. **Adoption and usage** - active users, frequency, which tasks (code generation, tests, review, incident analysis). Explains the denominator; says nothing about value.
2. **Delivery outcomes (DORA)** - lead time, deployment frequency, change failure rate, failed deployment recovery time, rework rate. The instability pair is where AI-generated code usually shows its cost.
3. **Leading quality signals** - PR size, review time per PR, reverts, escaped defects, code churn (code rewritten within a few weeks), security findings per change.
4. **Developer experience** - DevEx-style survey: time saved, cognitive load, trust in AI output, toil reduced. DORA found trust in AI output remains low even as usage is high.
5. **Business impact** - share of time on new capabilities versus maintenance, cost per change (including licence and inference spend).

**Method.** Baseline before rollout; compare adopting versus non-adopting teams (or staged rollouts) rather than before/after alone, because everything else changes too; hold PR size and review norms constant, or larger AI-generated PRs will quietly inflate review wait and change failure rate.

**Trade-offs and traps.** "Lines of AI-generated code" rewards volume, which is a cost. Faster code generation shifts the bottleneck to review, testing, and integration - if those do not scale, lead time does not improve. And never use AI usage metrics to evaluate individuals.

## Example

Comparing change failure rate, rework rate, and PR size for AI-assisted versus other changes, assuming PRs are labelled by the tooling:

```sql
SELECT p.ai_assisted,
       count(DISTINCT d.id)                                                   AS deploys,
       round(100.0 * avg((d.caused_incident OR d.rolled_back)::int), 1)       AS cfr_pct,
       round(100.0 * avg(d.is_unplanned_fix::int), 1)                         AS rework_rate_pct,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY p.lines_changed)          AS median_pr_lines,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY p.merged_at - p.opened_at) AS median_review_time
  FROM deployments d
  JOIN pull_requests p ON p.merge_sha = d.commit_sha
 WHERE d.environment = 'production'
   AND d.deployed_at >= now() - interval '90 days'
 GROUP BY p.ai_assisted;
```

## Interview tips

- Open with "measure the system, not the tool" and name instability (CFR, rework rate) as the metric most likely to move the wrong way.
- Quote DORA's "AI is an amplifier" framing and one or two AI Capabilities Model items such as small batches and quality internal platforms.
- Mention the perception gap (METR's 2025 study) to justify why surveys alone are insufficient - and why system data alone misses trust and cognitive load.
- Expect the follow-up "what would you change if CFR rose after rollout?" - smaller PRs, stronger automated tests, and review guidelines for AI-generated code.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
