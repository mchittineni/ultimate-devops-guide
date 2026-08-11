---
title: "What is Platform Engineering?"
id: 141
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is Platform Engineering?

**Short answer:** Platform engineering builds and runs an internal developer platform - a curated, self-service layer over infrastructure - treating developers as customers and the platform as a product with a roadmap, users, and success metrics.

## Detail

**The problem it solves.** "You build it, you run it" gave developers ownership but also handed them Kubernetes, Terraform, service meshes, observability stacks, and cloud IAM. That cognitive load is unsustainable for most product teams. Platform engineering pulls the shared complexity into a paved road.

**What an internal developer platform provides**

- **Self-service provisioning** - a new service with pipeline, repository, monitoring, and environments in minutes, without a ticket.
- **Golden paths** - opinionated, supported templates that encode security, observability, and deployment best practice by default.
- **Abstraction with escape hatches** - sensible defaults for the 80%, with the ability to drop to raw configuration when genuinely needed.
- **Standardised CI/CD, secrets management, and observability** wired in automatically.
- **A developer portal** (Backstage is the common choice) providing a service catalogue, documentation, scaffolding, and ownership information.

**What makes it succeed:** treating it as a product. Real user research, adoption measured rather than mandated, a roadmap, and support. A platform teams are forced to use but hate is a failed platform.

**Metrics:** time from idea to first deployment, adoption rate of golden paths, developer satisfaction survey scores, and the DORA metrics of teams using the platform versus those that are not.

**The anti-pattern** is the platform team as a gatekeeper - a ticket queue in front of infrastructure. That is the old operations silo with a new name.

## Interview tips

- "Platform as a product, developers as customers" is the sentence that captures the whole discipline.
- Cognitive load (from Team Topologies) is the theoretical grounding worth naming.
- Adoption as a voluntary metric, not a mandate, is the test of whether a platform is any good.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
