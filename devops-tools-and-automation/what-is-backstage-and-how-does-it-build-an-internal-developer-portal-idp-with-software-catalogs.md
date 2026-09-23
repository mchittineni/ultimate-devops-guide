---
title: "What is Backstage and how does it build an Internal Developer Portal (IDP) with software catalogs?"
id: 634
category: "DevOps Tools and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - backstage
  - platform-engineering
  - idp
  - developer-portal
quiz:
  stem: "What is the primary function of the Software Catalog in Spotify's Backstage?"
  options:
    - "To buy commercial SaaS licenses at enterprise discounts"
    - "To provide a centralized, searchable registry of all services, libraries, and APIs along with their ownership, dependencies, and health"
    - "To run continuous integration unit tests"
    - "To compile TypeScript code into machine binaries"
  answer: 2
  explanation: "The Backstage Software Catalog centralizes ownership, dependencies, documentation, and lifecycle status for every service across an enterprise, ending microservice discovery chaos."
---

# What is Backstage and how does it build an Internal Developer Portal (IDP) with software catalogs?

**Short answer:** Backstage is an open-source framework created by Spotify that centralizes developer infrastructure into an Internal Developer Portal (IDP), providing a unified Software Catalog, automated Golden Path software templates, and technical documentation.

## Detail

In large microservice organisations, developers struggle with discovery: _Who owns this service? Where are its API docs? Which channel handles its pages? How do I create a new Go service that already meets our security standards?_ Backstage answers these in one portal. It was open-sourced by Spotify in 2020, donated to the CNCF, and is now a CNCF incubating project.

### Core pillars

1. **Software Catalog** - the heart of it. Each repository carries a `catalog-info.yaml` descriptor declaring what the entity is (`Component`, `API`, `Resource`, `System`, `Domain`, `Group`, `User`), who owns it, and how it relates to others (`dependsOn`, `providesApis`, `partOf`). Backstage _ingests_ these with entity providers and processors - discovering them across GitHub/GitLab orgs, and importing users and groups from an identity provider - so the catalog is kept current from Git rather than typed into a wiki.
2. **Software Templates (Scaffolder)** - golden paths as code. A template asks the developer a few parameters, then runs actions: fetch a skeleton, render it, create the repository, register it in the catalog, open pull requests against config repos. The result is a new service with CI/CD, security scanning, and deployment manifests already wired up.
3. **TechDocs** - docs-as-code: Markdown next to the source, built with MkDocs and rendered on the entity's page.
4. **Plugins** - most value comes from plugins that attach context to an entity page: Kubernetes workloads, CI runs, Argo CD sync status, PagerDuty on-call, SonarQube, cost data. Search indexes all of it.

### What it is not

Backstage is a **framework, not a product**. You get a TypeScript/React monorepo that you build, host, upgrade (monthly releases), and extend. The newer backend system and new frontend system reduce the glue code for installing plugins, but running Backstage well still takes dedicated engineers. Managed offerings (Spotify Portal, Roadie, and others) and commercial alternatives (Port, Cortex, OpsLevel) exist for teams that do not want to own it. Also, a portal is only an interface: without an underlying platform - automated provisioning, pipelines, and policies - the templates have nothing to call.

**Common failure mode.** The catalog decays if ownership and metadata are optional. Enforce `catalog-info.yaml` in the template, validate it in CI, and use scorecards or tech insights to make gaps visible.

## Example

```yaml
# catalog-info.yaml in the service's repository
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payment-service
  description: Card authorisation and capture
  annotations:
    github.com/project-slug: acme/payment-service
    backstage.io/techdocs-ref: dir:.
    pagerduty.com/service-id: P1234AB
spec:
  type: service
  lifecycle: production
  owner: group:payments-team
  system: e-commerce
  providesApis: [payments-api]
  dependsOn: [resource:payments-db]
```

```yaml
# A Scaffolder template: the golden path for a new service
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata: { name: go-service, title: Go microservice }
spec:
  owner: group:platform-team
  type: service
  parameters:
    - title: Service details
      required: [name, owner]
      properties:
        name: { type: string }
        owner: { type: string, "ui:field": OwnerPicker }
  steps:
    - id: fetch
      action: fetch:template
      input: { url: ./skeleton, values: { name: "${{ parameters.name }}", owner: "${{ parameters.owner }}" } }
    - id: publish
      action: publish:github
      input: { repoUrl: "github.com?owner=acme&repo=${{ parameters.name }}" }
    - id: register
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
        catalogInfoPath: /catalog-info.yaml
```

## Interview tips

- Say what problem it solves - discovery and ownership in a large estate - before listing features.
- Explain that the catalog is populated from `catalog-info.yaml` files in Git and kept fresh by ingestion, not maintained by hand.
- Describe templates as golden paths that create repositories and register them, not just boilerplate generators.
- Be honest about the cost: Backstage is a framework you build and operate; mention managed and commercial alternatives.
- A portal on top of no platform is just a prettier ticket form - the automation behind it is what matters.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
