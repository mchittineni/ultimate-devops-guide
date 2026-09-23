---
title: "What is a Service Catalog?"
id: 147
category: "Advanced DevOps & Cloud"
difficulty: "Intermediate"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is a Service Catalog?

**Short answer:** A service catalogue is the authoritative inventory of an organisation's software services - recording what each service is, who owns it, its dependencies, documentation, dashboards, and runbooks - usually surfaced through a developer portal such as Backstage.

## Detail

**What each entry records**

- **Identity** - name, description, and the business capability it serves.
- **Ownership** - the team accountable, plus on-call rotation and escalation contact.
- **Lifecycle** - experimental, production, or deprecated.
- **Links** - repository, CI pipeline, dashboards, alerts, runbooks, API documentation.
- **Dependencies** - services consumed and consumed by, ideally derived from traces rather than hand-maintained.
- **Metadata** - tier/criticality, data classification, SLOs, and compliance scope.

**Why it matters.** During an incident, "who owns this service and where is its runbook?" must be answerable in seconds. Beyond incidents, a catalogue enables dependency-aware change planning, security response ("which services use this library?"), cost allocation, and onboarding.

**Keeping it accurate is the whole challenge.** A manually curated catalogue is stale within a quarter. The techniques that work: define entries as code (`catalog-info.yaml`) in each service's repository so ownership changes with the code, auto-discover from repositories and cloud resources, derive dependencies from distributed traces, and gate deployment on catalogue registration so an unregistered service cannot reach production.

**Backstage** (from Spotify, now CNCF) is the dominant implementation, adding software templates for scaffolding new services, integrated technical documentation, and scorecards that grade services against standards such as "has an SLO", "has a runbook", "has no critical CVEs".

**Note:** "service catalog" also refers to AWS Service Catalog and ITIL service catalogues, which are about approved provisionable products rather than a software inventory. Clarify which is meant if the question is ambiguous.

## Example

```yaml
# catalog-info.yaml - Backstage entity kept in the service's own repository
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: checkout-api
  description: Takes payment and creates orders
  annotations:
    github.com/project-slug: example/checkout-api
    pagerduty.com/service-id: PX1234A
    backstage.io/techdocs-ref: dir:.
  links:
    - url: https://grafana.example.com/d/checkout
      title: Dashboard
    - url: https://runbooks.example.com/checkout
      title: Runbook
  tags: [tier-1, pci]
spec:
  type: service
  lifecycle: production
  owner: group:payments-team
  system: commerce
  dependsOn: [resource:orders-db, component:payments-gateway]
  providesApis: [checkout-api]
```

## Interview tips

- Entries as code in the service repository is the answer to "how do you keep it accurate?"
- Deployment gated on registration is a strong enforcement mechanism worth naming.
- Scorecards turning a catalogue into a driver of standards is the mature use case.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
