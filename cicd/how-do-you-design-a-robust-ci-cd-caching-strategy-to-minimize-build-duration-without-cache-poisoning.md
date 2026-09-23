---
title: "How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?"
id: 541
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cicd
  - caching
  - performance
  - optimization
quiz:
  stem: "Why should CI dependency caches use the cryptographic hash of the package lockfile in their cache key?"
  options:
    - "Because package managers delete lockfiles if the hash is missing"
    - "To ensure the cache is invalidated and rebuilt only when dependencies actually change, maximizing cache hits otherwise"
    - "To automatically encrypt the node_modules directory with AES-256"
    - "Because CI platforms cannot store files without a hash in the filename"
  answer: 2
  explanation: "Hashing the lockfile guarantees that as long as dependencies remain identical, builds reuse the cache archive, but any dependency update produces a new cache key."
---

# How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?

**Short answer:** Robust CI caching keys cache archives on content hashes of lockfiles (e.g. `package-lock.json`, `go.sum`), isolates caches per branch with fallback to trunk, and ensures caches are read-only for pull requests to prevent cache poisoning.

## Detail

Pipeline speed depends heavily on caching dependency downloads (`npm`, `pip`, `maven`) and compilation caches (`ccache`, Go's build cache, Gradle/Bazel remote caches). A cache is only safe if two things hold: the key changes exactly when the content should change, and nobody untrusted can write an entry that a trusted build will later restore.

### Best practices for CI caching

1. **Exact lockfile content keys.** Key the cache on a hash of the lockfile plus anything else that changes the output (OS, architecture, toolchain version):

   ```yaml
   key: npm-deps-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
   restore-keys: |
     npm-deps-${{ runner.os }}-
   ```

   If dependencies do not change, the exact key hits. If a dependency updates, a new key is computed; `restore-keys` (a newline-separated list of prefixes, not a YAML sequence) lets the job start from the most recent partial match and then save a fresh entry.

2. **Cache the package manager's download store, not the installed tree.** Caching `~/.npm` and running `npm ci` is reproducible; caching `node_modules` directly skips the lockfile verification and can carry stale or platform-specific binaries between runs.
3. **Preventing cache poisoning.** An attacker who can write a cache entry that a privileged build restores gets code execution in that build. GitHub Actions scopes caches by ref: a `pull_request` run can read caches from its own branch and the base branch, but what it saves is scoped to the PR merge ref and is never restored by `main`. The dangerous cases are the ones that run untrusted code _in a trusted context_ - `pull_request_target` or `workflow_run` workflows that check out the PR head, or a self-hosted runner with a shared cache directory. Keep those workflows cache-read-only (`actions/cache/restore`), and never let a job that ran untrusted code save to a key that release builds use.
4. **Separate cache storage by purpose.** Never cache build outputs alongside dependencies. Dependency caches change infrequently; compiled outputs change on every commit, so bundling them destroys the hit rate and bloats the cache.
5. **Treat the cache as an optimisation, never as an input.** A build must succeed (slowly) with a cold cache, release builds should either skip caches or use ones written only by the default branch, and artefacts you ship come from the registry, not the cache.

### Limits worth knowing

Caches are evicted (GitHub Actions evicts least-recently-used entries once a repository exceeds its storage quota, and removes entries unused for 7 days), so hit rates drop on busy repositories with many keys. Caches are also immutable per key - you cannot update an entry in place, which is why the key must encode the content.

## Example

```yaml
# .github/workflows/ci.yml - lockfile-keyed dependency cache, safe for PRs
name: ci
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: 22
      - uses: actions/cache@v6
        with:
          path: ~/.npm # the download store, not node_modules
          key: npm-deps-${{ runner.os }}-node22-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            npm-deps-${{ runner.os }}-node22-
      - run: npm ci # verifies the lockfile; a poisoned or stale entry cannot change what is installed
      - run: npm test
```

`actions/setup-node` can do the same with `cache: npm`; the explicit form above shows the key design.

## Interview tips

- Say how the key is built - lockfile hash plus OS and toolchain - and why: the cache must change exactly when the inputs change.
- Explain `restore-keys` as a prefix fallback, and note that the fallback is why you should cache a download store and re-run the frozen install rather than restore an installed tree.
- Describe cache poisoning as a privilege problem, not a storage one: untrusted code writing an entry that a trusted build restores. Name `pull_request_target` and shared self-hosted runner caches as the realistic attack paths.
- Be clear that a build must pass with a cold cache; a cache that is load-bearing for correctness is a bug.
- Likely follow-up: "how do you cache Docker layers?" - BuildKit cache exports (`type=gha` or `type=registry`), with the same rule that PR builds should not write to the cache that release builds read.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
