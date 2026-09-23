---
title: "What are DevOps Best Practices?"
id: 127
category: "DevOps Culture and Practices"
difficulty: "Beginner"
tags:
  - devops
  - devops-culture-and-practices
  - interview-questions
---

# What are DevOps Best Practices?

**Short answer:** Version everything, automate the path to production, integrate continuously in small batches, test automatically at every stage, build infrastructure as code, monitor comprehensively, and review incidents blamelessly.

## Detail

**Delivery**

- Trunk-based development with short-lived branches and small pull requests.
- Continuous integration with a fast, trustworthy build - under ten minutes.
- Build the artifact once, promote the same artifact through environments.
- Automated deployment with automated rollback, and progressive delivery for risky changes.
- Feature flags to separate deploy from release.

**Infrastructure**

- Everything in version control: application code, infrastructure, pipeline definitions, dashboards, alerts, and runbooks.
- Infrastructure as code with peer-reviewed plans and policy scanning.
- Immutable infrastructure - replace rather than patch.
- Environment parity so staging predicts production.

**Quality and security**

- The test pyramid: many fast unit tests, fewer integration tests, a small number of end-to-end tests. Fix or delete flaky tests.
- Security scanning in the pipeline (SAST, dependency, secrets, IaC) with sensible failure thresholds.
- No secrets in code; short-lived credentials via OIDC.
- Supply-chain hygiene: pin third-party CI actions to a full commit SHA, generate an SBOM, and sign artifacts with provenance (for example Sigstore and SLSA build provenance).

**Operations**

- SLOs with error budgets, and alerts that fire on user-visible symptoms.
- Structured logs, metrics, and traces with correlation IDs.
- Blameless post-mortems with tracked actions.
- Sustainable on-call with alert hygiene reviewed weekly.

**Ways of working**

- Shared ownership: you build it, you run it.
- Documentation kept close to the code and updated as part of the change.
- Measure with DORA metrics and act on the trend, not the number.

## Example

A GitHub Actions job showing several practices at once - SHA-pinned actions, OIDC instead of stored keys, and one artifact built and promoted by digest:

```yaml
name: build
on:
  push:
    branches: [main]
permissions:
  contents: read
  id-token: write          # OIDC token for AWS - no long-lived secrets
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd # v6.3.0
        with:
          role-to-assume: arn:aws:iam::123456789012:role/ci-build
          aws-region: eu-west-1
      - name: Test, build once, push
        run: |
          make test
          IMAGE=123456789012.dkr.ecr.eu-west-1.amazonaws.com/app
          aws ecr get-login-password | docker login --username AWS --password-stdin "${IMAGE%%/*}"
          docker build -t "$IMAGE:$GITHUB_SHA" .
          docker push "$IMAGE:$GITHUB_SHA"
          # Later stages deploy this exact digest to staging, then production
          docker inspect --format '{{index .RepoDigests 0}}' "$IMAGE:$GITHUB_SHA" > digest.txt
```

## Interview tips

- Group practices into themes rather than reciting a flat list - it reads as structured thinking.
- If asked to pick the highest-leverage practice, small batches with automated testing is a defensible answer.
- Have one example of a practice you introduced, and what measurably changed.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Culture and Practices](./README.md) · [All topics](../README.md)
