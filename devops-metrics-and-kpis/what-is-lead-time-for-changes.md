---
title: "What is Lead Time for Changes?"
id: 105
category: "DevOps Metrics and KPIs"
difficulty: "Intermediate"
tags:
  - devops
  - devops-metrics-and-kpis
  - interview-questions
---

# What is Lead Time for Changes?

**Short answer:** Lead time for changes is the elapsed time from code commit to that code running successfully in production. It measures the efficiency of the delivery pipeline, and the strongest teams keep it under a day.

## Detail

**The DORA bands, and the health warning that goes with them.** In the reports that published performance tiers, the top band was less than one day, high was one day to one week, medium was one week to one month, and low was more than one month. Quote them as a rough scale, not gospel: the cut-offs moved between report years (the top band was under one hour in the 2021–22 reports and under one day from 2023), and the 2025 State of DevOps report **dropped the elite/high/medium/low ranking altogether** in favour of seven team archetypes that combine delivery performance with human factors like burnout and friction. An interviewer who tracks DORA will be more impressed that you know the tiers were retired than that you can recite a threshold.

Treat your own trend as the real benchmark - lead time falling quarter over quarter beats hitting somebody else's number once.

**Note the boundaries.** DORA measures commit → production, deliberately excluding the time a request spent in the backlog. The broader business measure - idea to production - is usually called _cycle time_ or _time to value_, and is worth tracking separately; a one-hour lead time behind a three-month backlog queue is not fast delivery.

**Where the time actually goes.** Break the interval into stages and measure each:

```text
commit → CI complete → PR reviewed → merged → deployed to staging → approved → in production
```

In most organisations, the dominant components are **waiting for code review** and **waiting for an approval or release window** - not build or test execution. Teams often optimise the pipeline by two minutes while a pull request sits for two days.

**What reduces it**

- Small pull requests and a team norm on review turnaround.
- Fast pipelines: caching, parallel jobs, test splitting, and selective builds in monorepos.
- Removing approval steps that no longer add information, or replacing them with automated policy checks.
- Continuous deployment for low-risk changes.
- Trunk-based development - long-lived branches inflate lead time enormously.

**Flow efficiency** - active work time divided by total elapsed time - is the diagnostic that reveals how much of your lead time is pure queueing. Typical values under 15% are common and eye-opening.

## Interview tips

- Distinguish lead time from cycle time explicitly; it is a frequent point of confusion.
- "Measure each stage - the bottleneck is usually review or approval, not the build" is a strong, experience-based answer.
- Flow efficiency is an excellent metric to raise if you want to show depth.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
