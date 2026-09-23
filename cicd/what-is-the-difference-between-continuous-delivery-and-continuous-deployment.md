---
title: "What is the difference between Continuous Delivery and Continuous Deployment?"
id: 20
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
---

# What is the difference between Continuous Delivery and Continuous Deployment?

**Short answer:** Both keep every change production-ready through an automated pipeline. Continuous delivery stops at a manual approval before production; continuous deployment releases automatically with no human gate.

## Detail

|                        | Continuous Delivery                   | Continuous Deployment                |
| ---------------------- | ------------------------------------- | ------------------------------------ |
| Path to production     | Automated up to a manual approval     | Fully automated                      |
| Who decides to release | A human (product, release manager)    | The pipeline's test results          |
| Typical cadence        | On demand - daily, weekly, per sprint | Every merged commit                  |
| Test requirement       | Strong                                | Comprehensive and trusted absolutely |
| Risk control           | Human judgement plus automation       | Canary, feature flags, auto-rollback |
| Common fit             | Regulated, on-prem, mobile releases   | SaaS web services                    |

The shared foundation is identical: trunk-based development, an immutable artifact promoted through environments, automated tests at every stage, and infrastructure as code. The delta is one approval step.

Choosing continuous delivery is often a _business_ decision - coordinating a release with marketing, satisfying a change-advisory process, or shipping software customers must install. Choosing continuous deployment is a _technical maturity_ decision: it requires progressive rollout, automated verification, and observability good enough to detect a bad release without a human watching.

A useful middle ground many teams adopt: continuous deployment to staging automatically, continuous delivery to production, with the approval becoming a formality that is eventually removed.

The limitation of each: a manual gate batches changes while they wait, so each release is bigger and harder to diagnose, and the approver rarely has more information than the pipeline. Removing the gate moves all of that judgement into automation - if the tests or the rollback signal are weak, continuous deployment ships bad changes faster.

## Example

```yaml
# The same pipeline; one setting is the whole difference.
# In GitHub Actions the "production" environment either has required reviewers
# (continuous delivery) or does not (continuous deployment).
name: release
on:
  push:
    branches: [main]
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging # no reviewers: always automatic
    steps:
      - uses: actions/checkout@v7
      - run: ./deploy.sh staging "$GITHUB_SHA"
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production # add required reviewers here -> continuous delivery
    steps:
      - uses: actions/checkout@v7
      - run: ./deploy.sh production "$GITHUB_SHA" --canary 5 --auto-rollback
```

## Interview tips

- The crispest phrasing: "delivery means every change _could_ go to production; deployment means every change _does_."
- Note that both require deployment to be decoupled from release, via feature flags.
- Say which you would pick for a given context, and why - the judgement is what is being assessed.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
