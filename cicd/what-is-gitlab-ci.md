---
title: "What is GitLab CI?"
id: 19
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
---

# What is GitLab CI?

**Short answer:** GitLab CI/CD is the pipeline engine built into GitLab, configured by a `.gitlab-ci.yml` file in the repository and executed by GitLab Runners, with the registry, environments, and security scanning integrated into the same product.

## Detail

Its advantage is integration: source control, merge requests, container registry, package registry, environments, secret variables, and security scanning all live in one place, so a pipeline needs very little glue.

Core concepts:

- **Stages and jobs** - jobs in the same stage run in parallel; stages run in order. `needs:` creates a directed acyclic graph so a job starts as soon as its own dependencies finish rather than waiting for the whole stage.
- **Runners** - instance, group, or project runners using the Docker, Kubernetes, shell, or instance/Docker Autoscaler executors (the Docker Machine executor is deprecated in favour of the GitLab Runner Autoscaler).
- **Artifacts and cache** - artifacts pass build outputs between jobs and are exposed in the UI; cache speeds up dependency installation.
- **Rules** - `rules:if` / `changes` control when a job runs, replacing the older `only/except`.
- **Environments** - track what version is deployed where, with review apps per merge request and one-click rollback.
- **CI/CD variables** - masked and protected, optionally sourced from an external secrets manager via OIDC.
- **Templates and components** - `include:` remote or project templates for reuse, and versioned **CI/CD components** published to the CI/CD Catalog (`include: - component: gitlab.com/org/proj/name@1.2.0`); built-in templates and components cover SAST, dependency scanning, secret detection, DAST, and container scanning.

## Example

```yaml
stages: [test, build, deploy]

variables:
  IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  image: node:24
  cache:
    key: { files: [package-lock.json] }
    paths: [.npm/] # the npm download cache, not node_modules
  script:
    - npm ci --cache .npm --prefer-offline
    - npm test -- --coverage # jest-junit reporter writes junit.xml
  artifacts:
    reports: { junit: junit.xml }

build:
  stage: build
  image: docker:29
  services: [docker:29-dind]
  variables:
    DOCKER_TLS_CERTDIR: "/certs" # TLS between the job and the dind service
  script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
    - docker build -t "$IMAGE" .
    - docker push "$IMAGE"

deploy:prod:
  stage: deploy
  environment: { name: production, url: https://example.com }
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual
  script: ./deploy.sh "$IMAGE"

include:
  - template: Security/SAST.gitlab-ci.yml
```

## Interview tips

- `needs:` for DAG pipelines is the modern answer to speeding up GitLab CI.
- Review apps - a live environment per merge request - are a strong differentiator worth naming.
- Know how to avoid long-lived cloud credentials by using GitLab's OIDC token with AWS/GCP.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
