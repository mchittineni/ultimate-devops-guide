---
title: "What is Azure Policy and how do landing zones use it?"
id: 204
category: "Azure Engineering"
difficulty: "Advanced"
tags:
  - devops
  - azure-engineering
  - interview-questions
---

# What is Azure Policy and how do landing zones use it?

**Short answer:** Azure Policy evaluates resources against rules and takes an effect - `Audit`, `Deny`, `Modify`, `DeployIfNotExists`, or `AuditIfNotExists` - at management-group, subscription, or resource-group scope. Landing zones assign curated policy initiatives at the management-group level so that every subscription created underneath inherits the same guardrails automatically, including remediation for existing resources.

## Detail

**The effects, and how they are used in practice:**

| Effect              | Behaviour                                  | Typical use                                    |
| ------------------- | ------------------------------------------ | ---------------------------------------------- |
| `Audit`             | records non-compliance, changes nothing    | measure before enforcing                       |
| `Deny`              | blocks the create/update request           | no public IPs, approved regions, required tags |
| `Modify`            | adds/updates properties or tags on write   | inherit tags from resource group               |
| `DeployIfNotExists` | deploys a related resource when missing    | diagnostic settings to Log Analytics           |
| `AuditIfNotExists`  | flags resources lacking a related resource | VM without an agent installed                  |

**Roll out in stages.** Assign as `Audit` first, look at the compliance report, fix or exempt the existing estate, then flip to `Deny`. Turning on `Deny` across a live environment without that step breaks pipelines and destroys goodwill. Exemptions should be scoped and given expiry dates.

**`DeployIfNotExists` is what makes observability universal.** Rather than asking every team to wire diagnostic settings, the policy deploys them - every new resource ships logs and metrics to the central Log Analytics workspace by default. These policies need a managed identity with permissions at the assignment scope, which is the most common reason a remediation task fails.

**Policy versus RBAC versus locks.** RBAC decides who may act; Policy decides what shape a resource may have, regardless of who acts - an Owner still cannot create a resource a `Deny` policy forbids. Locks prevent deletion. Real governance uses all three, plus Defender for Cloud for posture assessment and regulatory-compliance dashboards.

**Azure Landing Zones (the Cloud Adoption Framework accelerator)** ship a management-group hierarchy plus initiative assignments per branch: for example, `Corp` denies public IPs and requires private endpoints, while `Online` requires WAF on public entry points and permits internet exposure. That differentiation by branch - rather than one policy set for everything - is what makes landing zones usable.

**Deny is not a substitute for policy-as-code in CI.** Policy catches things at the Azure API, which means the developer learns at deploy time. Running the same intent in the pipeline (a policy check over the Bicep/Terraform plan) gives feedback at pull-request time. Belt and braces: pipeline for fast feedback, Azure Policy as the boundary that cannot be bypassed.

## Example

```json
{
  "properties": {
    "displayName": "Deny public network access on storage accounts",
    "mode": "Indexed",
    "parameters": {
      "effect": {
        "type": "String",
        "defaultValue": "Audit",
        "allowedValues": ["Audit", "Deny", "Disabled"]
      }
    },
    "policyRule": {
      "if": {
        "allOf": [
          { "field": "type", "equals": "Microsoft.Storage/storageAccounts" },
          {
            "field": "Microsoft.Storage/storageAccounts/publicNetworkAccess",
            "notEquals": "Disabled"
          }
        ]
      },
      "then": { "effect": "[parameters('effect')]" }
    }
  }
}
```

```bash
# Stage the rollout: audit at the management group, review, then switch to Deny
az policy assignment create \
  --name deny-storage-public \
  --scope "/providers/Microsoft.Management/managementGroups/corp" \
  --policy "$POLICY_ID" -p '{"effect":{"value":"Audit"}}'
```

## Interview tips

- List the five effects and give one real use for each - that alone answers most versions of this question.
- "Audit first, then Deny, with expiring exemptions" is the rollout discipline interviewers want to hear.
- Expect the AWS comparison: Azure Policy is closer to Config rules plus SCPs combined, and unlike SCPs it can remediate.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you choose a cloud provider for a new workload?]] (`#281`): [How do you choose a cloud provider for a new workload?](../cloud-platforms/how-do-you-choose-a-cloud-provider-for-a-new-workload.md)
- [[How does networking differ across AWS, Azure, and GCP?]] (`#282`): [How does networking differ across AWS, Azure, and GCP?](../cloud-platforms/how-does-networking-differ-across-aws-azure-and-gcp.md)
- [[What is a cloud landing zone?]] (`#215`): [What is a cloud landing zone?](../cloud-engineering/what-is-a-cloud-landing-zone.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
