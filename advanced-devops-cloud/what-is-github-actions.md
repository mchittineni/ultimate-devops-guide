---
title: "What is GitHub Actions?"
id: 157
category: "Advanced DevOps & Cloud"
difficulty: "Beginner"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is GitHub Actions?

**Short answer:** GitHub Actions is GitHub's built-in CI/CD and automation platform. Workflows defined in YAML in `.github/workflows/` respond to repository events, running jobs on GitHub-hosted or self-hosted runners.

## Detail

**Structure**

- **Workflow** - a YAML file triggered by events (`push`, `pull_request`, `schedule`, `workflow_dispatch`, `release`, or a repository dispatch).
- **Job** - a set of steps running on one runner. Jobs run in parallel by default; `needs:` creates dependencies.
- **Step** - a shell command (`run`) or a reusable **action** (`uses`).
- **Runner** - GitHub-hosted (Linux, Windows, macOS, and larger runners) or self-hosted for private networks and specialised hardware.

**Features that matter in practice**

- **Matrix builds** - the same job across versions, operating systems, or architectures.
- **Reusable workflows and composite actions** - factor shared logic out across repositories.
- **Environments** - deployment targets with required reviewers, wait timers, and scoped secrets. This is how you implement approval gates.
- **OIDC** - exchange a short-lived GitHub token for cloud credentials, eliminating stored long-lived cloud keys. This is the single most important security practice on the platform.
- **Caching and artifacts** - speed up builds and pass outputs between jobs.
- **Concurrency groups** - cancel superseded runs and serialise deployments.

**Security.** Set `permissions:` explicitly at the minimum required (the default token is broad). Pin third-party actions to a commit SHA, not a mutable tag. Be extremely careful with `pull_request_target`, which runs with write access in the context of a fork's code. Restrict which actions are allowed at the organisation level.

## Example

```yaml
name: deploy
on:
  push: { branches: [main] }

permissions:
  contents: read
  id-token: write # for OIDC only

concurrency:
  group: deploy-production
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production # required reviewers configured in repo settings
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: eu-west-1
      - run: ./deploy.sh
```

## Interview tips

- OIDC instead of stored cloud keys is the security answer interviewers are listening for.
- Pinning actions to a SHA is a supply-chain detail that distinguishes serious users.
- Environments with required reviewers is how approval gates are done properly - not a manual step in a script.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
