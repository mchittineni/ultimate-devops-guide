---
title: "What is Git Branching Strategy?"
id: 47
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - version-control
  - interview-questions
---

# What is Git Branching Strategy?

**Short answer:** A branching strategy is the team's agreement on how branches are created, merged, and released - the main options being trunk-based development, GitHub Flow, Git Flow, and release branching, chosen to match release cadence and risk.

## Detail

**Trunk-based development.** Everyone commits to `main` (or via very short-lived branches merged within a day). Incomplete work hides behind feature flags. This is the model that makes CI genuine and is strongly associated with elite DORA performance. It requires good tests and flag discipline.

**GitHub Flow.** A branch per change, a pull request for review, merge to `main`, deploy. Simple, well suited to web services with continuous deployment. Effectively trunk-based if branches stay short.

**Git Flow.** Long-lived `main` and `develop`, plus `feature/*`, `release/*`, and `hotfix/*` branches. Designed for versioned software with scheduled releases and multiple supported versions. Heavy for continuous delivery - the author himself now suggests it is overkill for web apps.

**Release branching.** `main` plus a `release/x.y` branch per version, with fixes cherry-picked back. Standard for software shipped to customers who upgrade at their own pace.

**Choosing:** how often do you release, do you support multiple versions in the field, and how good is your test automation? Continuous deployment of a SaaS product → trunk-based. Quarterly on-premises releases with three supported versions → release branching.

Whatever the model, the practices that matter more than the diagram are: short-lived branches, small pull requests, protected `main` with required checks, and a linear, readable history.

## Interview tips

- The strongest answer explains the _criteria_ for choosing, not just the diagrams.
- Long-lived branches are the real enemy - name merge hell and delayed integration feedback.
- Feature flags are what let trunk-based development work with unfinished features.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
