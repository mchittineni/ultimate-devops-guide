---
title: "What is the difference between Artifact Promotion and rebuilding binaries across environments?"
id: 534
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cicd
  - artifacts
  - build-once
  - docker
quiz:
  stem: "Why is rebuilding a Docker image for production instead of promoting the existing staging image considered dangerous?"
  options:
    - "Docker limits image builds to one per calendar day per organization"
    - "Upstream package dependencies or base image updates may silently introduce untested changes into the production build"
    - "Rebuilding images corrupts the host's Linux kernel modules"
    - "Production images cannot run on Linux servers if built from source"
  answer: 2
  explanation: "If an image is rebuilt, dynamic dependencies (`apt-get upgrade`, unlocked packages) can differ from the artifact tested in staging, breaking the guarantee of pre-production validation."
---

# What is the difference between Artifact Promotion and rebuilding binaries across environments?

**Short answer:** Artifact Promotion builds, tests, and signs an immutable binary or container image once in CI, and promotes that exact same artifact through Staging to Production, while rebuilding per environment risks deploying untested dependencies or compiler drift.

## Detail

The golden rule of continuous delivery is: **Build once, promote everywhere**.

### Why Rebuilding Per Environment Fails

If you run `docker build` in Dev, and then run `docker build` again a week later for Production:

- An upstream base image tag (`node:24-alpine`) or package dependency (`npm install` without strict lockfile) may have updated.
- A new sub-dependency with a security regression or bug gets pulled into production that was never tested in dev or staging.
- Build environments, timestamps, and commit hashes can diverge.

### The Promotion Pattern

1. **Build & Test**: Build the container image, tag it with the git SHA (`my-app:8f9a2c3`), run tests, and push to an internal container registry.
2. **Deploy to Dev/Staging**: Deploy image `my-app:8f9a2c3` using staging environment variables and secrets.
3. **Promote to Prod**: Deploy the exact same digest (`my-app@sha256:7b1e...`) to production. Only configuration (ConfigMaps, Secrets, environment variables) changes, never the code or dependencies.

Promotion itself is a metadata operation: copy or retag the digest into a production repository (or add a `prod` tag), record the approval, and let the deployment reference the digest. Signatures and attestations follow the digest, so a production admission policy can require "signed by our CI, from `main`" and reject anything that was rebuilt elsewhere.

### Requirements and trade-offs

- **Configuration must be external.** An image with an environment baked in (API URLs, feature flags compiled into a frontend bundle) cannot be promoted; move those to runtime config or build-time-once injection.
- **Registry layout and access.** Production pulls from a registry path that only the promotion job can write to, so nothing un-promoted can reach production.
- **Security patches.** Promotion does not mean never rebuilding: a base-image CVE requires a _new_ build, which then goes through the whole pipeline again. What is forbidden is rebuilding the same version for a later environment.

## Example

```bash
# Build once in CI and capture the immutable digest
docker buildx build -t registry.example.com/dev/my-app:8f9a2c3 --push .
DIGEST=$(crane digest registry.example.com/dev/my-app:8f9a2c3)   # sha256:7b1e...

# Promote: copy the same bytes to the prod repository - no rebuild
crane copy "registry.example.com/dev/my-app@${DIGEST}" registry.example.com/prod/my-app:8f9a2c3

# Deploy by digest, so a moved tag can never change what runs
kubectl set image deploy/my-app app="registry.example.com/prod/my-app@${DIGEST}"
```

## Interview tips

- Lead with "build once, promote everywhere", then give the reason: a rebuild produces a different artefact from the one you tested.
- Say "digest", not "tag" - tags are mutable pointers; the digest is the content.
- Separate artefact from configuration (12-factor): the only per-environment difference is config and secrets.
- Handle the follow-up "what about a security patch?" - that is a new build and a new promotion cycle, not a rebuild of the old version.
- Mention that signatures and provenance attach to the digest, which lets production enforce that only promoted, CI-built artefacts run.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
