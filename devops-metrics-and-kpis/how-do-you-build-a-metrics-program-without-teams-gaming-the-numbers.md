---
title: "How do you build a metrics program without teams gaming the numbers?"
id: 288
category: "DevOps Metrics and KPIs"
difficulty: "Advanced"
tags:
  - devops
  - devops-metrics-and-kpis
  - interview-questions
---

# How do you build a metrics program without teams gaming the numbers?

**Short answer:** Instrument metrics from systems of record rather than self-reporting, always pair a throughput metric with a stability metric so one cannot be improved by wrecking the other, keep them out of individual performance reviews, and use them to prompt conversations rather than to rank teams. Every metric you can be rewarded for is a metric you will be optimised for - so design the pair, define the terms precisely, and expect to revise the definitions when someone finds the loophole.

## Detail

**Goodhart's law is the whole problem.** "When a measure becomes a target, it ceases to be a good measure." Deployment frequency rises when teams split one change into five commits. MTTR falls when incidents are closed early and reopened under a new ticket. Test coverage hits 90% with assertion-free tests. Story points inflate. None of these require bad intent - people respond rationally to what is rewarded.

**Design metrics in pairs.** This is the strongest structural defence, because it makes gaming visibly self-defeating:

| Throughput / speed     | Paired with (stability / quality)       | The gaming it blocks                   |
| ---------------------- | --------------------------------------- | -------------------------------------- |
| Deployment frequency   | Change failure rate                     | Trivial deploys to inflate the count   |
| Lead time for changes  | Change failure rate, escaped defects    | Merging half-finished work             |
| Time to restore (MTTR) | Incident count, customer-impact minutes | Closing incidents early, reclassifying |
| Test coverage          | Mutation score or escaped defect rate   | Tests with no assertions               |
| Story points delivered | Cycle time and rework rate              | Point inflation                        |
| Platform adoption      | Developer satisfaction survey           | Forced migration nobody wanted         |

**Instrument from systems of record.** Derive deployment frequency from the deployment system, lead time from commit and merge timestamps in Git, change failure rate from linked incidents and rollbacks, and restore time from the incident tool's own state transitions. A metric a human types into a spreadsheet is a metric you have asked to be gamed. Where a judgement call is unavoidable (was this a change failure?), make it in a blameless review with a written definition, and accept the residual noise.

**Definitions are the real work.** "Deployment" - production only, per service, or per environment? Does a config change count? "Lead time" - first commit to production, or PR merge to production? "Incident" - customer-impacting only, or every page? Write these down, version them, and publish the query. Most metric arguments are definition arguments in disguise, and two teams computing lead time differently makes any comparison worthless.

**Use them at the right altitude.** DORA metrics are **team-level, trend-oriented** signals. That means:

- **Never in individual performance reviews.** This is the fastest way to destroy data quality permanently, and it is very hard to undo.
- **No cross-team league tables.** A team maintaining a regulated payments core will never match a team shipping an internal dashboard, and pretending otherwise teaches everyone that the numbers are political.
- **Trends over absolutes.** "Our lead time went from 9 days to 2" is the useful statement; "we are at 2.1 days and they are at 1.8" is not.
- **As a prompt, not a verdict.** The metric says "look here"; the conversation with the team finds the cause. A rising change failure rate might be a flaky test suite, an understaffed team, or a genuinely riskier domain.

**Round it out with the things DORA misses.** Add **reliability** (SLO attainment and error budget burn - the fifth DORA metric), **operational load** (pages per person per week, toil hours), and **developer experience** (DevEx / SPACE-style surveys: time to first commit, build wait time, self-reported friction). Qualitative survey data is harder to game than system metrics precisely because it measures perception, and it catches the case where throughput is great because everyone is working weekends.

**Expect to iterate.** Assume every definition has a loophole and that someone will find it. When they do, that is information about your incentives, not a disciplinary matter - fix the metric pair. Review the metric set itself once or twice a year and retire what nobody acts on; an unread dashboard is pure cost.

## Example

```sql
-- Derived from systems of record, with the definition written into the query.
-- Lead time: PR merge -> production deploy, per service, weekly p50/p85.
WITH deploys AS (
  SELECT service, commit_sha, deployed_at
    FROM deployments
   WHERE environment = 'production' AND status = 'succeeded'
), merged AS (
  SELECT service, commit_sha, merged_at FROM pull_requests WHERE merged_at IS NOT NULL
)
SELECT d.service,
       date_trunc('week', d.deployed_at)                                        AS week,
       percentile_cont(0.5)  WITHIN GROUP (ORDER BY d.deployed_at - m.merged_at) AS p50,
       percentile_cont(0.85) WITHIN GROUP (ORDER BY d.deployed_at - m.merged_at) AS p85,
       count(*)                                                                 AS deploys
  FROM deploys d JOIN merged m USING (service, commit_sha)
 GROUP BY 1, 2 ORDER BY 2 DESC;
```

```promql
# The pair, always on the same dashboard panel row.
sum by (service) (increase(deployments_total{env="prod",status="succeeded"}[7d]))
sum by (service) (increase(deployments_total{env="prod",rolled_back="true"}[30d]))
  / sum by (service) (increase(deployments_total{env="prod"}[30d]))

# Reliability and load, so speed is never the only story.
1 - (sum_over_time(slo_error_budget_burn[30d]) / 30)   # SLO attainment
sum by (team) (increase(pages_total[7d])) / sum by (team) (oncall_engineers)
```

```yaml
# Publish the definitions as code, next to the queries. Version them.
metrics:
  deployment_frequency:
    definition: "Successful production deployments per service per week"
    source: deployments table, environment=production, status=succeeded
    excludes: [config-only changes, non-production environments]
    paired_with: change_failure_rate
    usage: team-level trend only; not for individual review or cross-team ranking
```

## Interview tips

- Name Goodhart's law and then immediately give the pairing structure. The pairing is the answer; the law is just the framing.
- Have two concrete gaming examples ready (splitting deploys, closing incidents early) and the specific counter-metric for each.
- "Instrument from systems of record, never self-reported" is a short, high-signal sentence. Say it.
- Be firm that these are team-level trend metrics and never individual performance inputs. Interviewers often ask this as a trap.
- Mention the fifth DORA metric (reliability) and add operational load plus a DevEx survey. It shows you know throughput metrics alone hide burnout.
- Say that definitions are the hard part and that you publish the query. Anyone who has run a metrics program has had the "our lead time is different from yours" argument.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
