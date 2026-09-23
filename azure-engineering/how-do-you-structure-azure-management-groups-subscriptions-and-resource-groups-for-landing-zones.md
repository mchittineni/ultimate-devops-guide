---
title: "How Do You Structure Azure Management Groups, Subscriptions, and Resource Groups for Landing Zones?"
id: 741
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - azure-engineering
  - governance
  - landing-zones
  - management-groups
quiz:
  stem: "In the Azure resource hierarchy, what is the primary operational role of Management Groups?"
  options:
    - "They replace individual virtual machine operating system kernels."
    - "They provide a hierarchical governance scope above subscriptions to apply Azure Policy and RBAC permissions that inherit downward across all child subscriptions."
    - "They act as physical data centers within an Azure geographic region."
    - "They are used exclusively for paying invoices via credit card."
  answer: 2
  explanation: "Management Groups organize subscriptions in a container tree, enabling centralized governance, compliance enforcement via Azure Policy, and access control via Azure RBAC that automatically inherit to all nested resources."
---

# How Do You Structure Azure Management Groups, Subscriptions, and Resource Groups for Landing Zones?

**Short answer:** Azure Landing Zones organize resources into a hierarchical tree: Management Groups apply enterprise policies and RBAC across multiple subscriptions, Subscriptions act as billing, quota, and identity boundaries, and Resource Groups group logically related assets sharing a common lifecycle.

**Short answer:** Management groups carry policy and RBAC for many subscriptions and should be organized by **governance need** (platform versus application landing zones, corp versus online), not by org chart or environment. Subscriptions are the unit of billing, quota, and blast radius, so each workload gets its own - typically one per environment. Resource groups hold resources that share a lifecycle. The Azure Landing Zones reference architecture encodes this: Platform (identity, management, connectivity), Landing Zones (corp, online), Sandbox, and Decommissioned.

## Detail

### The Azure Landing Zones Hierarchy

```text
               [Tenant Root Group]
                       │
               [Intermediate root, e.g. "contoso"]
     ┌─────────────┬───────────────┬─────────────┬──────────────────┐
     ▼             ▼               ▼             ▼                  ▼
 [Platform]   [Landing Zones]   [Sandbox]   [Decommissioned]
  ├─ Identity   ├─ Corp  (private, hub-connected)
  │   sub       │   ├─ ecommerce-prod sub
  ├─ Management │   └─ ecommerce-dev sub
  │   sub       └─ Online (internet-facing)
  └─ Connectivity   ├─ web-prod sub
      sub           └─ web-dev sub
```

### Hierarchy Layers and Responsibilities

1. **Management groups (governance boundary)**
   - Policy assignments and RBAC at a management group inherit to every child management group and subscription.
   - Keep the tree shallow (up to six levels are allowed below the root; three or four is plenty) and assign under an intermediate root rather than the tenant root, so you can test changes in a parallel "canary" hierarchy.
   - Split by what governance differs: **Corp** (no public IPs, private endpoints required, hub-connected) versus **Online** (internet-facing, WAF required). Microsoft recommends **not** creating separate prod and non-prod management groups: the same policies should apply to both so that what you test is what you run, and environments are separated at the subscription level instead.
2. **Subscriptions (billing, quota, and blast-radius boundary)**
   - Each subscription is a billing container with its own per-region quotas and an RBAC scope, trusting exactly one Entra tenant.
   - One subscription per workload per environment (`ecommerce-prod`, `ecommerce-dev`) keeps quotas, costs, and access separate; **subscription vending** (a pipeline that creates a subscription, places it in the right management group, peers its VNet to the hub, and assigns budgets and RBAC) makes this cheap.
   - Platform subscriptions hold shared services: Connectivity (hub VNet, Firewall, ExpressRoute, DNS), Management (Log Analytics, automation), Identity (domain controllers, if any).
3. **Resource groups (lifecycle boundary)**
   - Resources provisioned, updated, and deleted together belong in the same resource group; deleting the group deletes everything in it.
   - Resource group location only stores metadata; resources can be in other regions.

**Trade-offs.** More subscriptions give cleaner isolation but more peering, private DNS, and cost-management overhead - which is why vending automation is a prerequisite, not an optimization. Moving subscriptions between management groups is easy; moving resources between subscriptions is constrained per resource type.

### Real-World Production Scenario

A multinational firm migrates to Azure using the Azure Landing Zones accelerator. A policy on the **Corp** management group denies public IP creation and requires private endpoints; the Retail and Logistics production and development subscriptions all sit under Corp, so both application teams inherit identical guardrails, while their public-facing storefront lives in a separate subscription under **Online** with a WAF requirement. Budgets and cost reports stay separate per subscription.

## Example

```bash
# Management group tree under an intermediate root
az account management-group create --name contoso --display-name "Contoso"
for mg in platform landingzones sandbox decommissioned; do
  az account management-group create --name "$mg" --parent contoso
done
az account management-group create --name corp   --parent landingzones
az account management-group create --name online --parent landingzones

# Place a vended subscription and apply a guardrail at the Corp level
az account management-group subscription add --name corp --subscription "$ECOM_PROD_SUB"
# built-in definition 6c112d4e-...: "Not allowed resource types"
az policy assignment create --name deny-public-ip \
  --scope "/providers/Microsoft.Management/managementGroups/corp" \
  --policy "6c112d4e-5bc7-47ae-a041-ea2d9dccd749" \
  --params '{"listOfResourceTypesNotAllowed":{"value":["Microsoft.Network/publicIPAddresses"]}}'
```

## Interview tips

- Explain inheritance: policy and RBAC flow from management groups to subscriptions to resource groups to resources.
- Organize management groups by governance difference (Corp/Online, Platform/Landing Zones), not by environment or org chart - and say why.
- Treat subscriptions as the blast-radius and quota boundary, and mention subscription vending as how you make many subscriptions manageable.
- Reference the Azure Landing Zones architecture (Cloud Adoption Framework) and its accelerators (Bicep or Terraform modules).
- Expect the AWS comparison: management group ≈ OU, subscription ≈ account, resource group has no direct equivalent.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[How does networking differ across AWS, Azure, and GCP?]] (`#282`): [How does networking differ across AWS, Azure, and GCP?](../cloud-platforms/how-does-networking-differ-across-aws-azure-and-gcp.md)
- [[What are Cloud Availability Zones and how are they engineered for fault independence?]] (`#544`): [What are Cloud Availability Zones and how are they engineered for fault independence?](../cloud-platforms/what-are-cloud-availability-zones-and-how-are-they-engineered-for-fault-independence.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
