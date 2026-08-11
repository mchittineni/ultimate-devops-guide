---
title: "What is CI/CD Pipeline?"
id: 16
category: "CI/CD"
difficulty: "Beginner"
tags:
  - devops
  - cicd
  - interview-questions
---

# What is CI/CD Pipeline?

**Short answer:** A CI/CD pipeline is the automated path from a commit to running software: a sequence of stages that build, test, scan, package, and deploy a change, failing fast and giving the team a single verdict on whether the change is safe.

## Detail

The pipeline encodes your definition of "ready to ship" in executable form. A typical shape:

1. **Source** - a push or pull request triggers the run.
2. **Build** - compile, resolve dependencies, produce an artifact.
3. **Test** - unit tests first (seconds), then integration and contract tests.
4. **Static analysis and security** - linting, SAST, dependency CVE scanning, secret detection, IaC policy checks.
5. **Package** - build a container image or archive, tag it with the commit SHA, push to a registry.
6. **Deploy to staging** - using the same automation as production.
7. **Acceptance / performance tests** - end-to-end and load checks.
8. **Deploy to production** - automatically, or after approval.
9. **Post-deploy verification** - smoke tests and error-rate monitoring, with automatic rollback.

Design principles that separate good pipelines from slow ones: fail fast (cheap checks first), build the artifact once and promote it, keep total feedback under ten minutes for CI, make every run reproducible, and never let secrets live in the pipeline definition.

## Example

```yaml
# .github/workflows/pipeline.yml
name: pipeline
on:
  push: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make lint test

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write, id-token: write }
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ghcr.io/org/app:${{ github.sha }} .
      - run: docker push ghcr.io/org/app:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production # gated approval lives here
    steps:
      - run: ./deploy.sh ghcr.io/org/app:${{ github.sha }}
```

## Interview tips

- Describe a pipeline you actually built, stage by stage, with the runtime of each stage.
- Mention what fails the build and what only warns - that distinction shows operational judgement.
- Have an answer for pipeline speed: caching, parallel jobs, test splitting, and selective builds in a monorepo.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
