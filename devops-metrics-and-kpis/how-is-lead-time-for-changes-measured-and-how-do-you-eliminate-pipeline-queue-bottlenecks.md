---
title: "How is Lead Time for Changes measured and how do you eliminate pipeline queue bottlenecks?"
id: 650
category: "DevOps Metrics and KPIs"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - devops-metrics-and-kpis
  - metrics
  - dora
  - lead-time
  - value-stream
quiz:
  stem: "According to DORA research, what impact do manual Change Advisory Boards (CABs) have on software delivery performance?"
  options:
    - "They decrease change failure rates by 50%"
    - "They significantly worsen lead time for changes without providing any measurable improvement to production stability"
    - "They are legally required by all cloud providers"
    - "They speed up continuous integration build times"
  answer: 2
  explanation: "Rigorous empirical research by DORA found that manual CAB approvals introduce massive delays (lead time inflation) with zero statistical correlation with improved system reliability."
---

# How is Lead Time for Changes measured and how do you eliminate pipeline queue bottlenecks?

**Short answer:** Lead Time for Changes measures the clock time from when a developer commits code to when that commit runs in production; bottlenecks are eliminated by auto-scaling CI runners, parallelizing test suites, and abolishing manual Change Advisory Boards (CABs).

## Detail

Lead time quantifies engineering agility and response time:

```text
lead time = (commit -> PR opened) + review wait + CI duration + (merge -> deploy) + deploy & verification
```

Measure each segment separately from timestamps in Git, the CI system, and the deploy tool, and report the median and p85 rather than the mean - a few long-lived branches skew the average badly.

### The Three Biggest Bottlenecks

1. **Pull Request Review Delays**: PRs sitting unreviewed for 4 days. Solution: Enforce small PR sizes (< 200 lines) and pair programming.
2. **Slow CI Pipelines**: 60-minute test runs. Solution:
   - Shard test suites across 20 parallel runner jobs.
   - Cache lockfile dependencies.
   - Build container image once and promote digest.
3. **Manual Approval Gates (CABs)**: DORA research (from the 2019 report onwards) found that heavyweight external change approval was associated with worse delivery performance and **no improvement in change failure rate**, while adding days or weeks of waiting. Replace manual CABs with peer review plus automated policy-as-code gates in CI, keeping a lightweight human approval only for genuinely high-risk changes - regulated environments usually accept this if the automated controls are auditable.

**CI queue time is its own bottleneck.** Time a job waits for a free runner is invisible in "pipeline duration" dashboards; track it separately and fix it with autoscaled ephemeral runners (for example Actions Runner Controller on Kubernetes) and by cancelling superseded runs.

## Example

Review wait is usually the biggest segment. Median hours from PR opened to merged, with the GitHub CLI and jq:

```bash
gh pr list --state merged --limit 200 --json createdAt,mergedAt \
  | jq '[.[] | ((.mergedAt | fromdateiso8601) - (.createdAt | fromdateiso8601)) / 3600]
        | sort | .[length/2|floor] | "median_hours_open=\(. * 10 | round / 10)"'
```

## Interview tips

- Measurement: commit timestamp to production deployment timestamp.
- Value stream mapping to locate waiting bottlenecks (PR review, CI queues, manual approvals).
- Eliminating manual Change Advisory Boards (CABs) in favor of automated gates.
- Sharding and caching in CI pipelines.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
