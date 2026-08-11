---
title: "How do you speed up a slow CI/CD pipeline?"
id: 396
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - docker
  - cloud-cost-optimization
  - devops-metrics-and-kpis
---

# How do you speed up a slow CI/CD pipeline?

**Short answer:** Measure before you optimise - break the wall-clock time into queue time, checkout, dependency resolution, build, test, and publish, and fix the largest bar first. The five changes that recover the most time in practice: **cache dependencies** keyed on the lockfile hash, **build the artefact once** and promote it instead of rebuilding per stage, **parallelise and shard the test suite**, **use BuildKit layer and cache mounts** for image builds, and **scale the agent pool** so jobs stop waiting. The target that matters is pull-request feedback under 10 minutes.

## Detail

### 1. Profile the pipeline before changing anything

Get per-stage durations from the CI tool's own timing view (Jenkins Pipeline Steps / Blue Ocean, GitLab job trace, GitHub Actions timing summary) and record two numbers separately:

- **Queue time** - how long a job waited for an executor. If this dominates, no amount of build optimisation helps; you need more or bigger agents.
- **Execution time** per stage, at p50 and p95. Optimise the widest bar, and re-measure after each change so you can prove the win.

A pipeline that regressed from 10 minutes to 30 has a _cause_, not a general slowness: look for a cache that stopped hitting (lockfile churn or a changed cache key), a test suite that grew, a plugin upgrade, a full-clone instead of a shallow one, or a workspace that is never cleaned so the disk is thrashing.

### 2. Cache the things that are expensive to fetch

Cache the dependency directory (`~/.m2`, `~/.gradle/caches`, `node_modules` or the npm/pnpm store, `~/.cache/pip`, `~/.cargo`), keyed on a hash of the lockfile with a looser fallback key. Two rules keep caches honest: the key must change when the lockfile changes, or you ship stale dependencies; and the cache must be measured, because a cache with a 20% hit rate is a slow network copy plus a rebuild.

### 3. Build once, promote the same artefact

The most common structural waste is rebuilding the application in the deploy stage for each environment. Build and tag one immutable artefact with the Git SHA, push it to the registry, and have every later stage pull that exact digest and change only configuration. This removes whole build stages _and_ removes the class of bug where production runs something that was never tested.

### 4. Parallelise, shard, and order for fail-fast

Run independent stages concurrently (lint, unit tests, SAST, image build). Shard slow suites across N agents by timing data rather than by file count, so the shards finish together. Order stages cheapest-first so a formatting error fails in 30 seconds instead of after the 12-minute integration suite. For large repositories add **test impact analysis** or an incremental build tool (Bazel, Gradle build cache, Nx, Turborepo) so unchanged modules are neither rebuilt nor retested - this is the single biggest win on a monolith, where "one line changed" should not mean "rebuild everything".

### 5. Make image builds and artefact transfers fast

Enable BuildKit with a registry-backed cache (`--cache-to`/`--cache-from`), order Dockerfile layers so dependency installation precedes the source copy, use cache mounts for package managers, and keep the build context small with `.dockerignore`. For slow artefact uploads, publish to a regional registry or proxy mirror, compress before transfer, and stop re-uploading unchanged artefacts.

### 6. Fix capacity and cost together

Autoscale ephemeral agents (Kubernetes agents, EC2 spot fleets, self-hosted runner autoscaling) so queue time collapses at peak while off-peak cost drops to near zero. Use spot or preemptible capacity for non-release jobs, cap concurrency per repository so one noisy pipeline cannot starve the rest, cancel superseded runs on the same branch, and expire old artefacts and logs on a lifecycle policy. Faster pipelines usually cost _less_, because most of the bill is idle capacity and repeated work.

## Example

```text
Pipeline: checkout-api          before -> after
  queue                  4m10s -> 0m20s   autoscaled k8s agents, 3 -> 12 executors
  checkout               1m05s -> 0m10s   shallow clone (depth=1), no submodules
  dependency resolve     6m40s -> 0m35s   cache key: hash(pnpm-lock.yaml)
  unit tests             9m20s -> 2m30s   sharded 4 ways by recorded timings
  integration tests     11m00s -> 4m00s   parallel with image build, not after it
  image build            5m30s -> 1m10s   BuildKit + registry cache, reordered layers
  deploy to dev          2m15s -> 0m45s   promote existing digest, no rebuild
  ------------------------------------------------------------------
  total (wall clock)       40m -> 7m      PR feedback now inside the 10m target
```

```yaml
# GitHub Actions: cache keyed on the lockfile, with a fallback, plus sharding
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 1 }
      - uses: actions/cache@v4
        with:
          path: ~/.pnpm-store
          key: pnpm-${{ hashFiles('pnpm-lock.yaml') }}
          restore-keys: pnpm-
      - run: pnpm install --frozen-lockfile
      - run: pnpm test --shard=${{ matrix.shard }}/4
```

## Interview tips

- Lead with measurement. "I would look at the stage timings and split queue time from execution time" is the answer that separates an engineer from someone reciting a list of optimisations.
- Separate the _regression_ case from the _always been slow_ case. A pipeline that doubled overnight is a broken cache, a full clone, or a plugin change - not a reason to redesign.
- Say "build once, promote the artefact" explicitly, and add the correctness argument: rebuilding per environment means you never tested what you shipped. See [what a CI/CD pipeline is](./what-is-ci-cd-pipeline.md).
- Mention sharding _by recorded test duration_, not by file count. It shows you have actually balanced a matrix.
- Name a concrete target - PR feedback under 10 minutes, main-branch pipeline under 30 - because "faster" without a number is not an engineering goal. Tie it to [lead time for changes](../devops-metrics-and-kpis/what-is-lead-time-for-changes.md).
- Flag the anti-pattern of fixing slowness by retrying or deleting tests, and handle flakiness as its own problem: see [how do you deal with flaky tests in a CI pipeline](./how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md).
- Close on cost: autoscaled ephemeral agents plus artefact expiry usually cut both the wait and the bill. See [how do you cut a cloud bill without hurting reliability](../cloud-cost-optimization/how-do-you-cut-a-cloud-bill-without-hurting-reliability.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
