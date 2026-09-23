---
title: "What is the difference between Continuous Delivery and Continuous Deployment?"
id: 511
category: "Core DevOps Concepts"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - core-devops-concepts
  - cicd
  - continuous-delivery
  - continuous-deployment
quiz:
  stem: "What distinguishes Continuous Deployment from Continuous Delivery?"
  options:
    - "Continuous Deployment only works with microservices architecture"
    - "Continuous Deployment releases every passing change directly to production without human intervention"
    - "Continuous Delivery does not require automated testing in CI pipelines"
    - "Continuous Delivery builds container images while Continuous Deployment deploys virtual machines"
  answer: 2
  explanation: "Continuous Delivery guarantees software is always releasable but retains a manual approval step, whereas Continuous Deployment pushes directly to production automatically."
---

# What is the difference between Continuous Delivery and Continuous Deployment?

**Short answer:** In Continuous Delivery, every commit passing automated tests is packaged and ready for release, but promotion to production requires manual business approval; in Continuous Deployment, every passing commit automatically deploys directly to production with no human intervention.

## Detail

Both practices require an automated pipeline of linting, unit tests, integration tests, and environment staging.

```text
Commit -> Build -> Test -> Staging -> [Manual Gate] -> Production  (Continuous Delivery)
Commit -> Build -> Test -> Staging -------------------> Production  (Continuous Deployment)
```

Continuous Deployment requires sophisticated automated safety nets:

- High unit and end-to-end test coverage with zero tolerance for flaky tests.
- Automated health checks, canaries, and automated rollback mechanisms.
- Comprehensive observability detecting latency spikes, 5xx errors, and business metric drops.

**Choosing between them.** Continuous deployment gives the smallest batches and fastest feedback, but it is not always the right call: mobile apps go through app-store review, on-premises software ships on customer schedules, and some regulated change processes require a recorded human approval. In those cases continuous delivery - always releasable, released on a decision - is the goal, and feature flags let even continuous deployment keep a human in control of _release_.

## Example

The difference in a GitHub Actions workflow is one setting: a protected environment with required reviewers turns continuous deployment into continuous delivery.

```yaml
jobs:
  deploy-production:
    needs: [test, deploy-staging]
    runs-on: ubuntu-latest
    # Continuous delivery: the "production" environment has required reviewers,
    # so the job waits for a human approval. Remove the reviewers rule and the
    # same workflow becomes continuous deployment.
    environment: production
    steps:
      - run: ./scripts/deploy.sh production "$GITHUB_SHA"
```

## Interview tips

- The human gate: Continuous Delivery stops at a manual trigger; Continuous Deployment is fully automated to production.
- Prerequisites for Continuous Deployment (canaries, rock-solid tests, automated rollback).
- Business vs technical readiness.
- Point out that feature flags separate deploy from release, so you can deploy continuously and still release on a business decision.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[What are Jenkins Pipelines?]] (`#18`): [What are Jenkins Pipelines?](../cicd/what-are-jenkins-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
