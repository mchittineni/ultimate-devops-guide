---
title: "How do you choose a cloud provider for a new workload?"
id: 281
category: "Cloud Platforms"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-platforms
  - interview-questions
---

# How do you choose a cloud provider for a new workload?

**Short answer:** For most organisations the decision is already made - you go where your existing accounts, contracts, and skills are, because the cost of a second provider is paid in people, not licences. When it is genuinely open, decide on four axes in this order: **regulatory and data-residency constraints**, **the managed services this workload actually depends on**, **existing team skills and enterprise agreements**, and **total cost including egress and support**. Feature checklists are the least useful input.

## Detail

**Start with the constraints that can disqualify a provider outright.** Data residency and sovereignty (EU-only processing, sovereign cloud requirements, government accreditations like FedRAMP or IRAP), industry certifications your auditors expect, and whether the provider has two or more regions in the geography your users are in. A provider that fails here is out regardless of price.

**Then look at the two or three services this workload genuinely leans on**, not the whole catalogue. Everyone has compute, object storage, managed Kubernetes, and a relational database, and at that layer the providers are near-interchangeable. The differences that matter are specific:

- **Data and analytics** - BigQuery's serverless model is a real differentiator on GCP; Snowflake and Databricks run everywhere but integrate differently.
- **Enterprise identity** - if the company runs Microsoft 365 and Entra ID, Azure removes an entire identity integration project.
- **Breadth and maturity of primitives** - AWS still has the widest surface and the deepest third-party ecosystem, which matters for unusual requirements.
- **ML/AI accelerators** - availability and quota for the GPU or TPU classes you need, in your region, is often the binding constraint rather than the model catalogue.
- **Kubernetes ergonomics** - GKE Autopilot, EKS Auto Mode, and AKS differ enough in operational load to matter to a small team.

**Weigh the human cost honestly.** A team fluent in AWS shipping on Azure will be slower and less safe for six to twelve months, and every runbook, module, and pipeline is rewritten. Existing enterprise agreements and committed-spend discounts are frequently worth more than any architectural preference. This is why "we picked the provider we already know" is a legitimate senior answer.

**Cost, computed the way the bill arrives.** Compare like-for-like on your actual shape - reserved or committed pricing at your usage floor, Spot/preemptible for interruptible work, **egress** (routinely the surprise line item for media, analytics, or multi-cloud designs), inter-AZ traffic, managed-service premiums, and the support plan tier you will be forced to buy. Model twelve months of projected growth, not today's footprint.

**Design for a reversible decision rather than for portability.** True provider-agnostic architecture costs you the managed services you are paying for. The pragmatic middle: keep the boundaries clean - containers, standard APIs, Terraform or another provider-neutral IaC tool, OpenTelemetry for instrumentation, your data in open formats (Parquet, Iceberg) - and accept provider-specific glue where it earns its keep. That keeps a future migration expensive but bounded.

## Example

```text
Decision order for a new workload
1. Disqualifiers   residency, certifications, ≥2 regions in-geo, sovereignty
2. Dependencies    the 2-3 managed services this workload truly needs
3. People          existing skills, EA / committed spend, on-call familiarity
4. Cost            committed pricing + egress + inter-AZ + support tier, over 12 months
5. Exit cost       what a migration would look like in 3 years - bounded, not free
```

| Workload signal                              | Usually points to              | Because                                             |
| -------------------------------------------- | ------------------------------ | --------------------------------------------------- |
| Microsoft-shop identity, Windows, SQL Server | Azure                          | Entra ID and licensing integration                  |
| Warehouse-heavy analytics, ad-hoc SQL        | GCP                            | BigQuery's serverless separation of storage/compute |
| Unusual primitives, widest partner ecosystem | AWS                            | Breadth and maturity of the service surface         |
| Strict EU-only processing                    | Provider with sovereign region | Residency is a disqualifier, not a preference       |
| Simple containerised web app                 | Any - pick on skills/cost      | The commodity layer is genuinely commoditised       |

```hcl
# Keep the decision reversible: provider-neutral tooling, provider-specific glue isolated.
module "app" {
  source = "./modules/app"           # containers, 12-factor config, OTel instrumentation
}

module "cloud_glue" {
  source = "./modules/aws-glue"      # the one module you would rewrite on a move
  # queues, managed database, IAM wiring - explicitly quarantined here
}
```

## Interview tips

- Say "usually the decision is already made, and that is fine" before the analysis. Interviewers want judgment, not a vendor bake-off.
- Order the axes: disqualifiers, then dependencies, then people, then cost. Leading with feature comparisons reads as junior.
- Name egress and support-tier cost explicitly. They are the two line items that break naive comparisons.
- Give one concrete differentiator per provider rather than marketing summaries - Entra ID for Azure, BigQuery for GCP, service breadth for AWS.
- Distinguish reversibility from portability. Full portability is a cost most teams should decline.
- Expect the follow-up "so when _is_ multi-cloud right?" Have an answer ready: acquisitions, a hard customer or regulatory requirement, or one specific service you cannot get elsewhere.

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
