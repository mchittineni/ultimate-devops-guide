---
title: "How to implement cost tagging strategy?"
id: 94
category: "Cloud Cost Optimization"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
---

# How to implement cost tagging strategy?

**Short answer:** Define a small mandatory tag schema (owner, environment, cost centre, application), enforce it automatically through IaC defaults and policy, activate the tags for cost allocation, and report untagged spend as a tracked metric until it approaches zero.

## Detail

**Design the schema first - keep it small.** Every additional mandatory tag reduces compliance. A workable minimum:

| Tag           | Purpose            | Example                          |
| ------------- | ------------------ | -------------------------------- |
| `Owner`       | Team accountable   | `platform-team`                  |
| `Environment` | Lifecycle stage    | `production` / `staging` / `dev` |
| `Application` | Service or product | `checkout-api`                   |
| `CostCenter`  | Finance allocation | `CC-4471`                        |
| `ManagedBy`   | Provenance         | `terraform`                      |

Agree on case and allowed values, and document them - `Env=prod` and `environment=Production` will not aggregate together.

**Enforce automatically**

- **IaC defaults** - `default_tags` in the AWS Terraform provider, or a shared module that injects tags; this covers the majority with no per-resource effort.
- **Policy as code** - AWS Service Control Policies or Tag Policies, Azure Policy `deny` or `modify` effects, or OPA in the pipeline to reject untagged resources.
- **Remediation** - periodic jobs that report or auto-tag stragglers from account or resource-group defaults.

**Then use them.** Activate cost-allocation tags in the billing console (untagged historical data cannot be backfilled), build per-team and per-environment cost dashboards, set budgets with alerts per owner, and publish a monthly showback or chargeback report.

**Track compliance as a metric:** percentage of spend that is fully tagged. It is the number that tells you whether the strategy is working.

**Note the limits:** some resources cannot be tagged, and shared costs (NAT gateways, data transfer, cluster control planes) need a documented split rule. Kubernetes workloads need labels plus a tool such as OpenCost, because the cloud bill stops at the node. Tag policies also cannot fix what was never tagged, which is why enforcement at creation matters more than audits.

## Example

```hcl
# Terraform AWS provider: every resource created through this provider gets the tags.
provider "aws" {
  region = "eu-west-1"
  default_tags {
    tags = {
      Owner       = "platform-team"
      Environment = "production"
      Application = "checkout-api"
      CostCenter  = "CC-4471"
      ManagedBy   = "terraform"
    }
  }
}
```

```bash
# Activate the tags for cost allocation (they only report from activation onward).
aws ce update-cost-allocation-tags-status --cost-allocation-tags-status \
  TagKey=Owner,Status=Active TagKey=Environment,Status=Active TagKey=CostCenter,Status=Active

# Track the gap: resources missing a required tag.
aws resourcegroupstaggingapi get-resources --query \
  'ResourceTagMappingList[?!not_null(Tags[?Key==`CostCenter`].Value | [0])].ResourceARN'
```

## Interview tips

- "Enforce in IaC, verify with policy, report the gap" is the three-part answer.
- Mention that cost-allocation tags apply going forward only - a genuinely useful practical detail.
- Untagged-spend percentage as a tracked KPI shows you have run this programme, not just designed it.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
