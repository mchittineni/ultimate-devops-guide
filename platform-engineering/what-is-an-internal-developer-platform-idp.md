---
title: "What is an Internal Developer Platform (IDP)?"
id: 222
category: "Platform Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# What is an Internal Developer Platform (IDP)?

**Short answer:** An IDP is the curated set of self-service capabilities a product team uses to build, deploy, and run software without filing tickets: scaffolding, CI/CD, environments, infrastructure provisioning, secrets, observability, and the guardrails around them. It is a product built by a platform team for internal users, not a collection of tools with a wiki page.

## Detail

**The planes it is usually described in:**

| Plane                    | Contains                                                            |
| ------------------------ | ------------------------------------------------------------------- |
| Developer control        | portal, CLI, or Git as the interface developers actually use        |
| Integration and delivery | CI/CD, image build, GitOps reconciliation, environment provisioning |
| Resource                 | Kubernetes, cloud accounts, databases, queues                       |
| Monitoring               | metrics, logs, traces, SLOs, cost visibility                        |
| Security                 | identity, secrets, policy, image signing and verification           |

**Self-service is the defining property.** If provisioning a database requires a ticket to the platform team, that capability is not part of the platform - it is a service desk. The test is: can a new engineer go from empty repository to a running service in production, with monitoring and an owner recorded, without a human approving each step?

**Golden paths, not mandates.** The platform provides a well-supported default path that is easier than doing it yourself; teams with genuine reasons can go around it and accept more responsibility. Platforms that enforce a single way create shadow platforms; platforms that are merely convenient get adopted voluntarily, which is the outcome you want.

**The abstraction must be reversible.** Hide Kubernetes YAML behind a simpler interface, but let a senior engineer see and override the generated manifests. Leak-proof abstractions become blockers the moment a workload is unusual, and the platform team becomes the bottleneck it was meant to remove.

**What it replaces.** Ticket-driven ops, per-team snowflake pipelines, and the situation where each team's reliability depends on which engineer set it up. The business case is cycle time and consistency: compliant logging, backups, tagging, and alerting arrive by default rather than by discipline.

**When you do not need one.** With three teams and one deployment target, a template repository and a good CI pipeline is the platform. IDP investment pays off with roughly a dozen teams and up, or when compliance demands consistency. Building a Backstage instance for four services is the classic misapplication, and saying so is a strong interview answer.

## Example

```yaml
# The developer-facing contract: a small, reviewable spec that yields a
# running service, monitored, owned, and compliant - no tickets in between.
apiVersion: platform.acme.com/v1
kind: Service
metadata:
  name: checkout
spec:
  owner: team-payments # drives on-call routing and catalogue ownership
  tier: 1 # tier drives SLO defaults, backup policy, review requirements
  runtime:
    image: ghcr.io/acme/checkout
    port: 8080
    resources: { cpu: 500m, memory: 512Mi }
    scaling: { min: 3, max: 30, metric: rps, target: 800 }
  dependencies:
    - postgres: { size: small, backups: daily, pitr: true }
    - queue: { name: orders, dlq: true }
  observability:
    slo: { availability: 99.9, latency: { threshold: 300ms, percentile: 99 } }
  network:
    ingress: internal
```

## Interview tips

- Define it by self-service and by being a product with users - tool lists are the weak answer.
- "Golden paths, not mandates" and "abstractions must be escapable" are the two ideas that show maturity.
- Expect: "when is an IDP not worth building?" - small organisations; recommend templates and a shared pipeline instead.

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
