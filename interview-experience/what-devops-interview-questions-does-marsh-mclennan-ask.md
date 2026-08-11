---
title: "What DevOps interview questions does Marsh McLennan ask?"
id: 347
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - marsh-mclennan
  - docker
  - cicd
  - container-orchestration-advanced
  - devsecops
  - version-control
---

# What DevOps interview questions does Marsh McLennan ask?

## Questions

**Git**

- **What is the difference between `git merge` and `git rebase`?**
- **Explain merge and rebase with a worked example using a `main` and a `feature` branch.**

**Docker**

- **How do you reduce the size of a Docker image?**
- **What is a multi-stage build, and how does it reduce image size?**
- **What is Docker image layer caching?**
- **How do you implement layer caching, and do you use a tool for it? If so, which one?**

**GitHub Actions**

- **If one job depends on another in GitHub Actions, which key do you use?**
- **How do you prevent concurrent runs of a workflow?**
- **What is the difference between `needs` and `concurrency`?**

**Helm**

- **Walk me through the troubleshooting steps for a failed Helm deployment.**
- **A Helm release is partially deployed — some resources updated and others failed. How do you roll it back?**

**Secrets management**

- **Where do you store application credentials in your CI/CD pipeline?**
- **How do you manage credentials in Jenkins?**
- **Have you used HashiCorp Vault for secret management?**
- **How do you store and retrieve secrets from Vault?**
- **What authentication methods and injectors does Vault support?**

## Example

```text
Marsh McLennan — DevOps Engineer (3 YOE), reported round
16 questions

  Secrets management          5   pipeline credentials, Jenkins credentials,
                                  Vault usage, store/retrieve, auth methods
                                  + injectors
  Docker                      4   reduce image size, multi-stage, layer
                                  caching, caching tooling
  GitHub Actions              3   needs, concurrency, difference between them
  Helm                        2   failed deployment triage, partial-release
                                  rollback
  Git                         2   merge vs rebase, worked example

FOUR DEEPENING CHAINS
  Every topic is asked twice, each time one level deeper: image size ->
  multi-stage -> caching -> which tool; Vault -> how -> which auth methods.
  The second question in each pair is where the round is decided.
```

```yaml
# The GitHub Actions pair, side by side — they solve different problems.
concurrency: # ACROSS runs: cancel or queue
  group: deploy-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps: [{ run: make build }]

  deploy:
    needs: build # WITHIN a run: ordering + gating
    runs-on: ubuntu-latest
    steps: [{ run: make deploy }]
```

## Interview tips

- `needs` versus `concurrency` is the cleanest discriminator in the round, so make the distinction explicit: `needs` orders jobs _inside a single workflow run_ and creates a dependency, so `deploy` waits for `build` and is skipped if `build` fails. `concurrency` governs _separate runs_ of a workflow, grouping them by a key so only one runs at a time — with `cancel-in-progress: true` to abandon a superseded run, which is what you want for CI on a branch, or `false` to queue, which is what you want for production deploys where cancelling mid-apply would be dangerous. Say that last trade-off; it is the senior detail.
- The layer-caching chain deserves a proper answer at each depth. Caching works because each Dockerfile instruction produces a layer keyed by the instruction and its inputs — if nothing above changed, the layer is reused. You _implement_ it by ordering the Dockerfile so slow, rarely-changing steps come first: copy the dependency manifest and install dependencies, then copy source code, so a code change does not invalidate the dependency layer. For the tooling question, name BuildKit with `--mount=type=cache` for package caches, `docker buildx` with `--cache-from` and `--cache-to` against a registry so CI runners share a cache, and GitHub Actions' cache backend. Registry-backed cache is the answer that shows you have solved this on ephemeral runners. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- The partial-Helm-release rollback question is the trickiest here. Say `helm rollback <release> <revision>` returns the release to a previous known-good revision, and add the details that matter: `helm history` shows you which revision to target, a release stuck in `pending-upgrade` may need `--force` or `helm rollback` to the last deployed revision, and resources Helm no longer tracks can be orphaned so you may have to clean them up manually. The real prevention is `helm upgrade --install --atomic --timeout 5m`, which rolls back automatically on failure rather than leaving a half-applied release. Naming `--atomic` is the strongest single point. See [what Helm is](../container-orchestration-advanced/what-is-helm.md).
- For failed Helm deployment triage, give an ordered method: `helm status` and `helm history` for the release state, then `helm get manifest` to see what was actually rendered, then drop to Kubernetes — `kubectl get events`, `describe` the failing object, and `logs --previous` on a crashing Pod. Distinguish the three failure classes out loud: a template rendering error (nothing reached the cluster), an API rejection such as a schema or admission-webhook failure, and a successful apply where the workload will not become Ready. Different classes, different fixes.
- The Vault chain wants concrete mechanics. Storage and retrieval: enable a secrets engine (KV version 2 for static secrets, or the database engine for dynamic credentials), write with `vault kv put`, read with `vault kv get`, and every read is governed by a policy and returns a lease. For the auth-methods question, name several and group them: human methods such as OIDC, LDAP, and userpass; machine methods such as AppRole, Kubernetes, AWS IAM, and JWT with GitHub Actions; and tokens underneath all of them. For injectors, name the Vault Agent Injector, which mutates a Pod to add an init and sidecar container that renders secrets to a shared volume, and the Vault Secrets Operator or CSI provider as alternatives. Say that the whole point is short-lived, auditable credentials rather than static ones. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- Jenkins credentials specifically: the Credentials plugin storing them in `JENKINS_HOME/credentials.xml` encrypted with the controller's key, scoped globally or per folder, and consumed with `withCredentials` or the `credentials()` helper so they are masked in logs. Add the failure mode that interviewers listen for — interpolating a secret inside a double-quoted Groovy string leaks it into the build log, so use single quotes and let the shell expand it. See [preventing and handling secret leaks in CI/CD](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).
- On where pipeline credentials belong, give the hierarchy rather than one answer: best is no stored credential at all — OIDC federation to the cloud provider issuing short-lived tokens; next best is a dedicated secret manager the pipeline reads at runtime; acceptable is the CI system's own encrypted secret store; never in the repository, in plain environment files, or in image layers.
- The merge-versus-rebase worked example is a whiteboard question, so structure it: with `main` at commits A-B-C and `feature` branched at B with commits D-E, a merge creates a new commit M with two parents, preserving the true history and the branch shape; a rebase replays D and E as new commits D' and E' on top of C, giving a linear history but different commit hashes. Then say the rule — never rebase a branch other people have pulled — and when you would choose each: rebase to tidy your own feature branch before review, merge to integrate into a shared branch. See [git merge, rebase, and cherry-pick](../version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md).
- Image size reduction should be prioritised, not listed: multi-stage build so compilers and dev dependencies never ship, a minimal base image such as Alpine or distroless, cleaning package caches within the same `RUN` layer, a `.dockerignore` to keep the build context small, and copying only the built artefact. Say you would run `docker history` to find the fat layer before guessing.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
