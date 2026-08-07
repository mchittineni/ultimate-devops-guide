---
title: "How is the GCP resource hierarchy organised?"
id: 207
category: "GCP Engineering"
difficulty: "Beginner"
tags:
  - devops
  - gcp-engineering
  - interview-questions
---

# How is the GCP resource hierarchy organised?

**Short answer:** Organization → folders (optionally nested) → projects → resources. The project is the fundamental boundary for billing, quotas, APIs, and IAM; folders exist to group projects for inherited policy; and the organization node is where org policies and the strongest constraints live. IAM and org policies inherit downward and are additive.

## Detail

**The project is the unit that matters.** Every resource belongs to exactly one project. Quotas, enabled APIs, billing attribution, and most IAM boundaries are per-project, so the standard pattern is one project per workload per environment - `payments-prod`, `payments-staging` - rather than one large shared project.

**Folders carry policy for a group of projects.** A common layout mirrors the organisation: folders for `platform`, `business-units/<bu>/<team>`, `sandbox`, and `bootstrap`. Nesting is limited (10 levels), and the practical guidance is to keep the tree shallow enough that a person can predict which policies apply.

**IAM inherits and is additive - there is no deny by omission at a lower level.** A role granted at the folder applies to every project inside it. IAM Deny policies exist and evaluate before allows, but the default model is union-of-grants, which is why granting `Editor` at the organisation node is such a common and serious mistake.

**Organization policy constraints are the real guardrails.** Distinct from IAM, they restrict what configurations are permitted regardless of permissions: `constraints/compute.requireShieldedVm`, `constraints/compute.vmExternalIpAccess` (no public IPs), `constraints/iam.disableServiceAccountKeyCreation`, `constraints/gcp.resourceLocations` (data residency). Applied at the organisation or folder level, they are inherited and cannot be overridden below unless the constraint allows it.

**Billing is attached, not inherited.** A billing account links to projects and is managed separately from the resource hierarchy, so a project can be moved between folders without changing billing, and billing admin is a separate role from resource admin. Labels on projects and resources are what make cost reports meaningful - enforce them with policy and validate them in CI, because GCP does not require them.

**Deletion has a safety net.** A deleted project enters a pending-deletion state for around 30 days before resources are irreversibly removed, which has saved many teams. Liens (`gcloud alpha resource-manager liens create`) can block deletion of critical projects outright.

## Example

```text
Organization: acme.com
├── folder: bootstrap        (Terraform service accounts, state bucket)
├── folder: platform
│   ├── project: net-hub-prod        (Shared VPC host, Cloud Interconnect)
│   ├── project: logging-prod        (log sinks, BigQuery datasets)
│   └── project: security-prod       (SCC, KMS keyrings)
├── folder: business-units
│   └── folder: payments
│       ├── project: payments-prod        (service project on the Shared VPC)
│       ├── project: payments-staging
│       └── project: payments-dev
└── folder: sandbox          (budget alerts, 30-day cleanup, no prod data policy)

Org policies at the organization node:
  compute.vmExternalIpAccess = deny all       (public IPs only via explicit exception)
  iam.disableServiceAccountKeyCreation = true (force workload identity federation)
  gcp.resourceLocations = in:eu-locations     (data residency)
```

## Interview tips

- Name the four levels and identify the project as the billing/quota/IAM boundary - that is the core of the question.
- Distinguish IAM (who may act) from org policy constraints (what configuration is allowed); interviewers probe this.
- Mention `disableServiceAccountKeyCreation` - it signals you know the modern, keyless GCP posture.

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
