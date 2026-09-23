---
title: "What are Team Topologies patterns and how do Stream-Aligned and Platform teams interact?"
id: 683
category: "DevOps Culture and Practices"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - devops-culture-and-practices
  - culture
  - team-topologies
  - organization
  - conways-law
quiz:
  stem: "In the Team Topologies framework, what is the primary relationship between a Stream-Aligned team and a Platform team?"
  options:
    - "Stream-Aligned teams submit JIRA tickets for the Platform team to deploy their code manually"
    - "The Platform team provides an internal product of self-service tools and APIs that enables Stream-Aligned teams to deliver features autonomously"
    - "The Platform team writes all application business logic"
    - "Stream-Aligned teams report directly to Platform managers"
  answer: 2
  explanation: "Platform teams build and treat their developer platform as an internal product, empowering Stream-Aligned teams to provision infrastructure and ship code autonomously via self-service."
---

# What are Team Topologies patterns and how do Stream-Aligned and Platform teams interact?

**Short answer:** Team Topologies defines four fundamental team types (Stream-Aligned, Enabling, Complicated-Subsystem, Platform) to optimize for fast flow; Stream-Aligned teams deliver direct business value, while Platform teams build self-service Internal Developer Platforms to reduce their cognitive load.

## Detail

Conway's Law states that organizations design systems that mirror their communication structures. Team Topologies organizes teams intentionally around software flow:

### The Four Fundamental Team Types

1. **Stream-Aligned Team**: Focused on a continuous flow of work for a single business capability (e.g. Checkout team, Search team).
2. **Platform Team**: Provides internal services, APIs, and infrastructure as an **internal product** so stream-aligned teams can build and deploy autonomously without ticket requests.
3. **Enabling Team**: Specialists (security, QA, performance) that parachute into stream-aligned teams temporarily to teach modern skills and patterns, then leave.
4. **Complicated-Subsystem Team**: Deep specialists managing mathematical or esoteric domains (e.g. 3D physics engine, custom cryptography).

### Interaction Modes

- **X-as-a-Service**: Platform team provides self-service APIs (Backstage templates, Terraform modules) consumed with minimal coordination.
- **Collaborating**: Two teams work closely together temporarily to discover a new approach.
- **Facilitating**: Enabling team coaching another team.

**How stream-aligned and platform teams interact over time.** A new platform capability typically starts in **collaboration** mode with one or two stream-aligned teams (discovering what they actually need), then moves to **X-as-a-Service** once the interface is stable. Staying in collaboration forever means the platform is not self-service; jumping straight to X-as-a-Service means it is built on guesses.

**Limitations.** The patterns describe a target, not an org chart to copy. A platform team without product management becomes a ticket queue with a new name, and a thinnest viable platform (sometimes just documentation and a few templates) is often better than a large one.

## Example

A team API, kept in the platform catalog so interaction modes are explicit rather than implied:

```yaml
# team-api/checkout.yaml
team: checkout
type: stream-aligned
owns: [checkout-api, basket-service]
interactions:
  - team: developer-platform
    mode: x-as-a-service        # uses golden-path templates and the deploy API
  - team: payments-platform
    mode: collaboration         # until 2026-12-31: designing the new 3DS flow together
    review_on: 2026-12-31
  - team: security-enablement
    mode: facilitating          # threat-modelling coaching this quarter
support_channel: "#team-checkout"
on_call: pagerduty:checkout-primary
```

## Interview tips

- Conway's Law driving team organization.
- Four team types: Stream-Aligned, Platform, Enabling, Complicated-Subsystem.
- Platform team treating internal infrastructure as a product consumed via self-service.
- Reducing cognitive load on stream-aligned teams.
- Say that interaction modes are meant to change over time - collaboration should be time-boxed and evolve into X-as-a-Service.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Culture and Practices](./README.md) · [All topics](../README.md)
