---
title: "How do you design CI/CD for a microservices architecture?"
id: 400
category: "CI/CD"
difficulty: "Advanced"
tags:
  - devops
  - cicd
  - interview-questions
  - cloud-native-architecture
  - container-orchestration-advanced
  - devops-tools-and-automation
---

# How do you design CI/CD for a microservices architecture?

**Short answer:** One independently triggered pipeline per service, one shared template so the fifty pipelines are not fifty snowflakes. Each service builds its own immutable image tagged with the Git SHA, publishes to a shared registry, and deploys on its own cadence without waiting for anyone else. The hard parts are not the pipelines - they are **change detection** in a monorepo, **contract testing** so you can deploy one service without integration-testing all forty, **version compatibility** so old and new run side by side during a rollout, and **preventing the release train** from re-forming as a shared staging bottleneck.

## Detail

### Pipeline topology

- **One pipeline per deployable service**, owned by the team that owns the service. Independent deployability is the entire point of microservices; a pipeline that must deploy everything at once has recreated the monolith with more moving parts.
- **Shared pipeline templates,** not copy-paste: reusable workflows in GitHub Actions, `include:` in GitLab CI, or a Jenkins shared library. Teams then supply parameters (language, test command, chart values) rather than 400 lines of YAML. See [how do you use Jenkins shared libraries](./how-do-you-use-jenkins-shared-libraries.md).
- **Monorepo or many repositories** both work; the choice changes only where the complexity sits. In a monorepo you must solve **change detection** - build and deploy only the services whose files (or shared libraries) changed, using path filters, `git diff` against the merge base, or a build graph tool (Bazel, Nx, Turborepo). With many repositories you get isolation free but must solve discovery, template distribution, and cross-repository dependency bumps.

### Testing without a full-system integration gate

This is what separates a working microservices pipeline from a slow one:

- **Unit and component tests** in the service pipeline, with dependencies stubbed.
- **Contract tests** (Pact or the equivalent) as the real safety net: the consumer publishes the interactions it relies on, the provider's pipeline verifies it has not broken them. This is what lets you deploy one service without booting the other thirty-nine.
- **A thin end-to-end suite** - a handful of critical user journeys, run in staging, kept deliberately small because full end-to-end coverage across N services grows unmaintainable and flaky.
- **Test in production carefully**: synthetic checks on the critical journeys, plus progressive delivery with automatic rollback, catches what pre-production cannot.

### Versioning and compatibility

During any rolling deployment, two versions of a service run at once, and its callers were built against the old one. So:

- APIs and events must be **backward compatible** for at least one release - additive changes, no field removals or type changes without a deprecation window. Enforce it in CI with schema linting (`buf breaking` for protobuf, OpenAPI diff, Avro compatibility checks against the registry).
- Database migrations follow expand/contract, decoupled from the code deploy. See [how do you change a production database schema without downtime](../database-management-in-devops/how-do-you-change-a-production-database-schema-without-downtime.md).
- Use **feature flags** to separate deploy from release, so a cross-service feature can be shipped in pieces and enabled once all parts are live. See [what is feature flagging](../advanced-devops-cloud/what-is-feature-flagging.md).

### Deployment and promotion

Build once per service, tag with the SHA, and promote the digest through environments; GitOps makes the promotion an auditable pull request against an environment repository, and ArgoCD ApplicationSets or Flux Kustomizations keep fifty services declarative without fifty bespoke deploy scripts. Each service rolls out progressively (canary or blue/green) with automatic rollback on error-budget burn. See [how do you promote a release across dev, staging, and production](./how-do-you-promote-a-release-across-dev-staging-and-production.md) and [what is GitOps](../devops-tools-and-automation/what-is-gitops.md).

### The failure modes to name

- **A shared staging environment that everyone must queue for** - the release train reborn. Fix with ephemeral per-pull-request environments and contract tests instead of a shared integration gate.
- **A shared library that forces a fleet-wide rebuild.** Version it and let services adopt on their own schedule; automate the bump with a dependency bot.
- **Pipeline sprawl** - every team's snowflake. Fix with templates owned by the platform team, and a golden path that is genuinely easier than rolling your own. See [what is a golden path](../platform-engineering/what-is-a-golden-path.md).
- **Cost and queue contention.** Fifty pipelines on shared runners will collide: cap concurrency per repository, cancel superseded runs, use autoscaled ephemeral agents on spot capacity, and expire artefacts on a lifecycle policy.

## Example

```yaml
# Monorepo change detection: build and deploy only what actually changed
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.filter.outputs.changes }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            checkout: ['services/checkout/**', 'libs/payments/**']
            orders:   ['services/orders/**',   'libs/payments/**']
            search:   ['services/search/**']

  build:
    needs: changes
    if: needs.changes.outputs.services != '[]'
    strategy:
      matrix:
        service: ${{ fromJSON(needs.changes.outputs.services) }}
    uses: ./.github/workflows/service-template.yml # one template, every service
    with:
      service: ${{ matrix.service }}
      image_tag: ${{ github.sha }}
```

```text
Per-service pipeline (the same shape for all 50, from one template)

  lint + unit ............. 90s
  contract verify ......... 40s   provider side: Pact broker "can-i-deploy"
  build image ............. 70s   tag: checkout:abc1234  (digest promoted later)
  scan image .............. 30s   fail on fixable criticals only
  deploy dev .............. 25s   auto
  smoke ................... 20s
  ------------------------------------------------
  gate to prod: contract broker says every consumer of checkout
  is compatible with abc1234 -> canary 5% -> 100%, auto-rollback on burn rate
```

## Interview tips

- Lead with independent deployability, then immediately name the two things that make it real: contract testing and backward-compatible APIs. Candidates who stop at "a pipeline per service" have described the easy half.
- Say the words "build once, tag with the Git SHA, promote the digest" - it is the line interviewers wait for.
- Volunteer the monorepo trade-off with the actual mechanism (path filters or a build graph), because "monorepo vs polyrepo" without change detection is a slogan.
- Explain why a full end-to-end gate does not scale: N services means combinatorial coupling, so the suite becomes slow and flaky and stops blocking anything real.
- Mention the shared-staging bottleneck as the anti-pattern you have seen. It is the most common real failure and shows operational experience.
- If asked about fifty pipelines' maintenance, answer with templates plus a platform team owning the golden path, and mention concurrency caps and artefact expiry for cost.
- Have the compatibility story ready for the follow-up "what breaks during a rollout?" - two versions live at once, so schema and event changes must be additive. See [what are microservices](../cloud-native-architecture/what-are-microservices.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What is Infrastructure Automation?]] (`#86`): [What is Infrastructure Automation?](../devops-tools-and-automation/what-is-infrastructure-automation.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
