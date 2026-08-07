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
- **Runners** - shared, group, or project-specific executors using the Docker, Kubernetes, shell, or Docker Machine executor.
- **Artifacts and cache** - artifacts pass build outputs between jobs and are exposed in the UI; cache speeds up dependency installation.
- **Rules** - `rules:if` / `changes` control when a job runs, replacing the older `only/except`.
- **Environments** - track what version is deployed where, with review apps per merge request and one-click rollback.
- **CI/CD variables** - masked and protected, optionally sourced from an external secrets manager via OIDC.
- **Templates** - `include:` remote or project templates for reuse; built-in templates cover SAST, dependency scanning, DAST, and container scanning.

## Example

```yaml
stages: [test, build, deploy]

variables:
  IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  image: node:20
  cache:
    key: { files: [package-lock.json] }
    paths: [node_modules/]
  script:
    - npm ci
    - npm test -- --coverage
  artifacts:
    reports: { junit: junit.xml }

build:
  stage: build
  image: docker:27
  services: [docker:27-dind]
  script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
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

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
