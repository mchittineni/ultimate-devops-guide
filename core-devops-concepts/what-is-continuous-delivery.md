---
title: "What is Continuous Delivery?"
id: 4
category: "Core DevOps Concepts"
difficulty: "Beginner"
tags:
  - devops
  - core-devops-concepts
  - interview-questions
---

# What is Continuous Delivery?

**Short answer:** Continuous Delivery extends CI so that every build that passes the pipeline is a release candidate - deployable to production at any moment by pressing a button. The decision to release stays with a human.

## Detail

Continuous Delivery means the software is _always_ in a releasable state. The pipeline proves it: after CI, the artifact moves through automated deployment to production-like environments, integration tests, security scanning, and performance checks. What emerges is a versioned, tested artifact plus the automation to deploy it anywhere.

Key elements:

- **Deployment pipeline** - successive stages of increasing confidence and cost. Fast unit tests first, expensive end-to-end tests later, so failures surface cheaply.
- **Build once, deploy many** - the same immutable artifact goes to staging and production. Configuration is injected per environment; nothing is rebuilt for prod.
- **Automated deployment** - the mechanics of deploying are identical in every environment, so they are well-rehearsed by the time production comes.
- **Production-like environments** - provisioned by the same IaC as production so tests mean something.

The human gate exists for business reasons - marketing timing, regulated change windows, customer communication - not technical ones.

## Example

```text
commit → build & unit tests → package artifact → deploy to staging
       → integration + contract tests → security scan → performance test
       → [manual approval] → deploy to production → smoke tests
```

## Interview tips

- The one-line distinction: continuous delivery is _able_ to deploy every change; continuous deployment _does_.
- Emphasise the immutable artifact - rebuilding per environment is a classic anti-pattern.
- Mention database migrations, which are usually the hardest part of making delivery truly continuous.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[What are Jenkins Pipelines?]] (`#18`): [What are Jenkins Pipelines?](../cicd/what-are-jenkins-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
