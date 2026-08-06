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

**Short answer:** A service catalogue is the authoritative inventory of an organisation's software services — recording what each service is, who owns it, its dependencies, documentation, dashboards, and runbooks — usually surfaced through a developer portal such as Backstage.

## Detail

**What each entry records**

- **Identity** — name, description, and the business capability it serves.
- **Ownership** — the team accountable, plus on-call rotation and escalation contact.
- **Lifecycle** — experimental, production, or deprecated.
- **Links** — repository, CI pipeline, dashboards, alerts, runbooks, API documentation.
- **Dependencies** — services consumed and consumed by, ideally derived from traces rather than hand-maintained.
- **Metadata** — tier/criticality, data classification, SLOs, and compliance scope.

**Why it matters.** During an incident, "who owns this service and where is its runbook?" must be answerable in seconds. Beyond incidents, a catalogue enables dependency-aware change planning, security response ("which services use this library?"), cost allocation, and onboarding.

**Keeping it accurate is the whole challenge.** A manually curated catalogue is stale within a quarter. The techniques that work: define entries as code (`catalog-info.yaml`) in each service's repository so ownership changes with the code, auto-discover from repositories and cloud resources, derive dependencies from distributed traces, and gate deployment on catalogue registration so an unregistered service cannot reach production.

**Backstage** (from Spotify, now CNCF) is the dominant implementation, adding software templates for scaffolding new services, integrated technical documentation, and scorecards that grade services against standards such as "has an SLO", "has a runbook", "has no critical CVEs".

**Note:** "service catalog" also refers to AWS Service Catalog and ITIL service catalogues, which are about approved provisionable products rather than a software inventory. Clarify which is meant if the question is ambiguous.

## Interview tips

- Entries as code in the service repository is the answer to "how do you keep it accurate?"
- Deployment gated on registration is a strong enforcement mechanism worth naming.
- Scorecards turning a catalogue into a driver of standards is the mature use case.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
