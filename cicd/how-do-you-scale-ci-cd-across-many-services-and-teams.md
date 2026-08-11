---
title: "How do you scale CI/CD across many services and teams?"
id: 459
category: "CI/CD"
difficulty: "Advanced"
tags:
  - devops
  - cicd
  - interview-questions
  - platform-engineering
  - devops-metrics-and-kpis
---

# How do you scale CI/CD across many services and teams?

**Short answer:** Stop writing pipelines per repository and start shipping **one templated pipeline that many repositories consume**. Concretely: pipeline definitions as versioned, semver-tagged templates (GitHub Actions reusable workflows, GitLab CI `include`, Azure DevOps templates, Jenkins shared libraries) that a service opts into with a handful of parameters; **change detection** so a monorepo builds only affected services and a polyrepo does not rebuild the world; an **elastic, ephemeral runner fleet** (one clean container or Pod per job) sized by queue-wait rather than by guesswork; **shared caches and an artefact repository** so dependency downloads happen once; **ephemeral preview environments** provisioned from the pipeline and destroyed on merge; and central **guardrails** - required checks, OIDC instead of stored keys, signed artefacts - enforced by the template rather than by asking people. The measure of success is not that pipelines exist but that a new service reaches production on day one with a five-line config, and that p50 pipeline duration and queue wait stay flat as the number of services grows.

## Detail

### Templates over copies

The failure mode at scale is 200 near-identical `Jenkinsfile`s that have all drifted. The fix is a platform-owned template with a small parameter surface:

| System         | Mechanism                                                                  | Notes                                                                 |
| -------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| GitHub Actions | Reusable workflows (`workflow_call`) + composite actions                   | Reusable workflow = whole jobs; composite action = steps inside a job |
| GitLab CI      | `include:` (project/remote/template) + `extends:` + CI/CD components       | Components are versioned and catalogued                               |
| Azure DevOps   | Template files in a shared repository, `extends:` with template parameters | `extends` templates can _enforce_ steps a consumer cannot remove      |
| Jenkins        | Shared library exposing a `buildService()` step                            | The `Jenkinsfile` becomes a call with parameters                      |

Rules that make this work: **version the templates** (`@v3`, and consumers pin a tag or SHA), practise **semver discipline** because a breaking template change breaks every consumer at once, roll changes out **canary-style** to a few repositories before all, and keep the parameter surface small - if a consumer needs twenty inputs, the abstraction is wrong. Provide extension points (a pre-build hook, extra steps) so teams do not have to fork the template to do something unusual.

Treat the template as a product: it has a changelog, a deprecation policy, and a support channel. See [how do you treat a platform as a product](../platform-engineering/how-do-you-treat-a-platform-as-a-product.md).

### Build only what changed

In a monorepo, the naive pipeline rebuilds everything on every commit and gets slower every quarter.

- **Path filters** are the cheap 80%: `paths:` in Actions, `rules: changes:` in GitLab, `when { changeset }` in Jenkins.
- **A build graph** is the real answer at scale: Bazel, Nx, Turborepo, Pants, or Gradle with build caching compute the affected targets from the dependency graph and reuse cached outputs for everything untouched. That is how a monorepo with 500 modules keeps a 6-minute PR build.
- **Content-addressed caching** (remote build cache) means a target already built by someone else is downloaded, not rebuilt - the single biggest lever on monorepo CI time.
- In a **polyrepo**, the equivalent problem is fan-out on a shared library change: publish the library as a versioned artefact and let consumers upgrade (with automated dependency PRs) rather than triggering 60 downstream builds on every commit.

### Runner and agent capacity

- **Ephemeral, one job per runner**: a fresh container or Pod per job so no state leaks between builds and no "works on agent 3 only" mysteries. Kubernetes-based executors (Jenkins Kubernetes plugin, Actions Runner Controller, GitLab Kubernetes executor) are the standard shape.
- **Autoscale on queue depth and wait time**, not CPU. The metric that matters to developers is **time from push to first log line**; alert on p95 queue wait.
- **Right-size by workload class**: small runners for lint, large for compile, GPU only where needed, ARM where it is cheaper. Labels let the template pick.
- **Spot/preemptible instances** for retryable stages with on-demand for deploys, plus scale-to-zero out of hours - CI is one of the easiest places to cut cloud spend without touching reliability.
- **Cache locality**: put the runner fleet, the artefact repository, and the registry in the same region; cross-region dependency pulls dominate many slow pipelines.

### Shared caching and artefacts

One artefact repository (Nexus, Artifactory, or the cloud registry) acting as a **pull-through proxy** for public registries gives you three things at once: faster and more reliable builds (no rate limits, no upstream outages), an audit trail of what you actually consumed, and a place to enforce policy. Layer on a remote build cache and a container-layer cache so cold runners are not cold. Immutable, digest-addressed artefacts promoted between environments - built once, deployed many times - is the other half; rebuilding per environment is how "it worked in staging" happens.

### Ephemeral environments and promotion

Provision a namespace or a lightweight stack per pull request from the pipeline, seed it with anonymised data, run integration tests against it, post the URL on the PR, and destroy it on merge or after a TTL (a garbage-collector job for orphans, or you will pay for hundreds of them). Then promote **the same artefact** through dev → staging → prod with environment-specific configuration, gated by required checks and, for production, an audited approval. See [how do you promote a release across dev, staging, and production](./how-do-you-promote-a-release-across-dev-staging-and-production.md).

### Guardrails that scale

Put policy in the template and in the platform, not in a wiki:

- **Required status checks** and protected branches, defined centrally (Terraform for repository settings, or an org-level ruleset) so every repository is consistent.
- **OIDC federation** to the cloud so no repository stores long-lived credentials, with trust policies scoped per repository and ref.
- **Pinned, allowlisted actions/images** and provenance: SBOM plus signature at build, verified at admission.
- **Policy as code** (OPA/Conftest on rendered manifests, Kyverno at admission) so a non-compliant deployment cannot happen even if a team edits their pipeline.
- **Least-privilege tokens** by default in the template.

### Measure it

Track the four DORA metrics per service (deployment frequency, lead time, change failure rate, MTTR) and the platform's own: p50/p95 pipeline duration, queue wait, flaky-test rate, cache hit rate, cost per build, and onboarding time for a new service. Publish them per team. Without numbers, "scaling CI/CD" is a vibe; with them, you can show that adding 50 services did not slow anyone down - and you can find the one pipeline that consumes 30% of the fleet.

### Consolidating a mixed estate

Real answer to "we have Jenkins, GitLab CI, and Actions": do not big-bang migrate. Pick the target, express the target as templates, migrate the highest-value or newest services first to prove the path, run both in parallel with the old system read-only, and set a deprecation date with support. Keep a registry of which service is on which system so the migration has an end. See [how do you consolidate a sprawling DevOps toolchain](../devops-tools-and-automation/how-do-you-consolidate-a-sprawling-devops-toolchain.md).

## Example

```yaml
# Platform-owned reusable workflow: acme/.github/.github/workflows/service.yml
on:
  workflow_call:
    inputs:
      service: { required: true, type: string }
      runner: { required: false, type: string, default: ubuntu-24.04 }
      deploy_environments:
        { required: false, type: string, default: '["dev","staging"]' }
    secrets:
      SONAR_TOKEN: { required: false }

permissions: { contents: read } # least privilege by default, for every consumer

jobs:
  build:
    runs-on: ${{ inputs.runner }}
    permissions: { contents: read, packages: write, id-token: write }
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
      - uses: docker/build-push-action@5cd11c3a4ced054e52742c5fd54dca954e0edd85 # v6.7.0
        with:
          push: true
          tags: ghcr.io/acme/${{ inputs.service }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - run: cosign sign --yes ghcr.io/acme/${{ inputs.service }}:${{ github.sha }}

  deploy:
    needs: build
    strategy: { matrix: { env: ${{ fromJSON(inputs.deploy_environments) }} } }
    environment: ${{ matrix.env }} # approvals and scoped secrets live here
    runs-on: ${{ inputs.runner }}
    steps:
      - run: ./deploy.sh ${{ inputs.service }} ${{ matrix.env }} ${{ github.sha }}
```

```yaml
# What a service repository has to write. Five lines, and it inherits every guardrail.
name: ci
on: { push: { branches: [main] }, pull_request: {} }
jobs:
  pipeline:
    uses: acme/.github/.github/workflows/service.yml@v3 # pinned, versioned template
    with: { service: payments, runner: ubuntu-24.04-8core }
    secrets: inherit
```

```bash
# Monorepo: build only what the change affects
CHANGED=$(git diff --name-only "origin/main...HEAD")
AFFECTED=$(npx nx show projects --affected --base=origin/main)   # or: bazel query
echo "$AFFECTED" | xargs -P4 -I{} npx nx run {}:build            # graph-driven, cached

# Bazel with a remote cache: unchanged targets are downloaded, not rebuilt
bazel build //... --remote_cache=grpcs://cache.example.com --remote_upload_local_results=true
```

```text
Platform metrics that prove it is scaling, reviewed monthly

  push -> first log line (p95 queue wait)      target < 30s     <- the developer's felt latency
  PR pipeline duration (p50 / p95)             target < 10m / 20m
  cache hit rate (deps + layers + build graph) target > 85%
  flaky-test rate                              target < 1% of runs
  cost per build, and cost per team            watch the top 5 consumers
  new service -> first production deploy       target < 1 day    <- the onboarding metric
  template version spread across repos         >90% on the latest minor
```

## Interview tips

- Lead with the structural answer - one versioned template consumed by many repositories - and name the mechanism for the system you know best (reusable workflows, `include`, Azure templates, Jenkins shared libraries). Then add semver discipline and canary rollout, because a breaking template change breaks every team simultaneously.
- For monorepos, distinguish path filters (cheap, gets you far) from a real build graph with remote caching (Bazel/Nx/Turborepo, what you need at 500 modules). Interviewers ask "how do you build only affected services?" and expect both tiers.
- Say ephemeral one-job-per-runner and **autoscale on queue wait, not CPU**. Naming the right autoscaling signal is a strong differentiator.
- Talk about building the artefact once and promoting the same digest through environments - rebuilding per environment is the root of "it worked in staging".
- Cover ephemeral preview environments including the part people forget: a TTL and a garbage collector, or you pay for orphans forever.
- Put guardrails in the template and the platform - required checks defined as code, OIDC instead of stored keys, pinned actions, signed images verified at admission - so compliance is the default rather than a request.
- Finish with metrics: DORA per service plus platform metrics (queue wait, p95 duration, cache hit rate, cost per build, onboarding time). Being able to say what you would measure is what makes this a senior answer.
- If asked about consolidating three CI systems, refuse the big-bang: template the target, migrate high-value services first, run in parallel, set a deprecation date. See [designing CI/CD for a microservices architecture](./how-do-you-design-ci-cd-for-a-microservices-architecture.md), [speeding up a slow pipeline](./how-do-you-speed-up-a-slow-ci-cd-pipeline.md), [what is an Internal Developer Platform](../platform-engineering/what-is-an-internal-developer-platform-idp.md), and [managing build artefacts with Nexus or Artifactory](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
