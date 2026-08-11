---
title: "What is Configuration Management?"
id: 51
category: "Configuration Management"
difficulty: "Beginner"
tags:
  - devops
  - configuration-management
  - interview-questions
---

# What is Configuration Management?

**Short answer:** Configuration management is the practice of defining, applying, and continuously enforcing the desired state of systems - packages, files, services, users - from version-controlled definitions, so every machine is consistent and drift is corrected automatically.

## Detail

Without it, servers become snowflakes: each hand-tuned differently, none reproducible, and nobody sure why production behaves differently from staging. Configuration management makes the desired state explicit and executable.

**Core concepts**

- **Desired state** - declared in code (playbooks, manifests, recipes), stored in Git.
- **Idempotency** - applying the definition repeatedly produces the same result; only actual differences cause change.
- **Convergence** - each run moves the system towards the desired state and reports what it changed.
- **Drift detection** - a dry run (`--check`, `--noop`) shows where reality has diverged, whether from manual change or failed automation.
- **Inventory and classification** - which nodes get which roles.

**Push vs pull.** Push tools (Ansible) connect out to nodes on demand - simple, no agent, good for orchestrated sequences. Pull tools (Puppet, Chef, Salt with minions) run an agent that periodically fetches and applies its catalogue - better for continuous enforcement at large scale.

**Where it is heading.** Immutable infrastructure has absorbed much of this work: instead of converging a long-lived server, you bake an image (Packer) or build a container and replace the instance entirely. Configuration management remains essential for the estates that cannot be made immutable, and for golden-image builds themselves.

## Interview tips

- Idempotency is the concept to define precisely - it is what separates configuration management from scripting.
- Explain drift and how you detect it before you are asked.
- Show awareness that containers and immutable infrastructure change the role of these tools rather than eliminating it.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
