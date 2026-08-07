---
title: "What is Backstage?"
id: 225
category: "Platform Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# What is Backstage?

**Short answer:** Backstage is an open-source developer portal framework from Spotify, now a CNCF project. Its core pieces are a software catalogue (every service, its owner, its dependencies), software templates (scaffolding new components), TechDocs (docs-as-code rendered beside each component), and a plugin system that surfaces CI, cloud, and incident data in one place. It is a framework you build on, not a product you install.

## Detail

**The catalogue is the foundation and the hardest part.** Components, systems, APIs, resources, and groups are declared in `catalog-info.yaml` files discovered from repositories, so ownership lives next to the code. The value appears in every adjacent workflow - who owns this failing service, which services consume this API, which teams are affected by deprecating this database - and none of it works if the catalogue is incomplete or stale. Automated discovery plus a policy that unregistered services do not get platform features is how teams keep it honest.

**Templates connect the portal to the golden path.** A template collects a few inputs and then executes actions: create the repository from a skeleton, register it in the catalogue, open the pull request wiring CI, provision infrastructure. This is the "create a new service" button that makes a portal feel like a platform rather than a directory.

**Scorecards drive standards without mandates.** A tech-health or maturity plugin scores each component against checks - has an owner, has an SLO, on a supported base image, dependencies patched, runbook exists - and shows teams their gaps. Visibility plus ownership moves behaviour more effectively than blocking pipelines, and it gives leadership a real compliance picture.

**Be honest about the cost.** Backstage is a TypeScript/React application that you fork, extend, deploy, and upgrade; keeping current with upstream releases and plugin churn is ongoing work, typically at least one dedicated engineer. Managed alternatives (Spotify Portal, Roadie, Red Hat Developer Hub) and competing products (Port, Cortex, OpsLevel) trade extensibility for lower maintenance - often the right call for a mid-sized organisation.

**A portal is not a platform.** A portal on top of ticket-driven operations is a nicer window onto the same delays. Build the self-service capabilities first, then a portal to surface them. Interviewers ask about Backstage partly to see whether you conflate the interface with the capability.

**Not everyone wants a UI.** Many engineers prefer a CLI or pure Git workflows. The catalogue and templates can be consumed through APIs, so treat the web portal as one interface over the platform, not the only one.

## Example

```yaml
# catalog-info.yaml - ownership and relationships live next to the code
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: checkout
  description: Card checkout and authorisation
  annotations:
    github.com/project-slug: acme/checkout
    backstage.io/techdocs-ref: dir:.
    pagerduty.com/service-id: PXYZ123
    prometheus.io/rule: checkout-slo
  tags: [tier-1, payments, go]
spec:
  type: service
  lifecycle: production
  owner: group:team-payments
  system: payments
  providesApis: [checkout-api]
  consumesApis: [ledger-api, fraud-api]
  dependsOn: [resource:default/orders-postgres]
```

## Interview tips

- Name the four pillars - catalogue, templates, TechDocs, plugins - and say the catalogue is where the value and the difficulty both live.
- "A portal is not a platform" is the line that shows you understand the ordering of the work.
- Expect: "would you build Backstage or buy a portal?" - weigh a dedicated engineer's cost against extensibility needs, and answer for the size of team in question.

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
