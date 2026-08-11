---
title: "How is the Azure resource hierarchy organised?"
id: 199
category: "Azure Engineering"
difficulty: "Beginner"
tags:
  - devops
  - azure-engineering
  - interview-questions
---

# How is the Azure resource hierarchy organised?

**Short answer:** Four levels - management groups, subscriptions, resource groups, resources. Management groups carry policy and RBAC inheritance across many subscriptions; the subscription is the billing and quota boundary; the resource group is a lifecycle and deployment container within one region's metadata; resources live in exactly one resource group.

## Detail

**Management groups** form a tree under a single root, up to six levels deep, and exist so that policy assignments and role assignments apply to many subscriptions at once. The conventional shape mirrors the Azure landing zone: a root, then platform (identity, management, connectivity) and landing zones (corp, online), plus sandbox and decommissioned branches.

**Subscriptions are the isolation unit that matters.** They bound billing, quotas, and to a large extent blast radius - analogous to an AWS account, though the mapping is not exact because Azure applies policy above the subscription. Quotas are per-subscription per-region, which is a common reason large environments split subscriptions per environment or per business unit rather than per team.

**Resource groups are lifecycle containers.** Everything in a group should share a deployment and deletion lifecycle, because deleting a resource group deletes everything in it. A resource group has a location, but that location only stores the group's metadata - resources inside it may live in other regions.

**Inheritance flows down and cannot be broken.** A policy assigned at a management group applies to every subscription beneath it; an RBAC assignment at a subscription applies to all resource groups and resources within. There is no "deny inheritance" - Azure Policy `Deny` effects at a higher scope cannot be overridden lower down, which is precisely what makes them useful as guardrails.

**Tags do not inherit by default.** Tags applied to a resource group do not propagate to resources - a frequent surprise on cost reports. Use an Azure Policy with a `modify` effect to inherit required tags from the resource group, and make the tags themselves mandatory with a `deny` policy at the management-group level.

**Moving things is possible but constrained.** Resources can be moved between resource groups and subscriptions, but support varies by resource type, references (like a VM's network interfaces) must move together, and the resource is locked during the move. Design the hierarchy expecting reorganisation to be awkward.

## Example

```text
Tenant root group
├── platform
│   ├── identity        (subscription: domain controllers, Entra Domain Services)
│   ├── management      (subscription: Log Analytics, automation, backup vaults)
│   └── connectivity    (subscription: hub VNet, firewall, ExpressRoute, DNS)
├── landing-zones
│   ├── corp            (internal apps; policy: no public IPs)
│   │   ├── sub: payments-prod   → rg-payments-prod-weu, rg-payments-data-weu
│   │   └── sub: payments-nonprod → rg-payments-dev-weu, rg-payments-test-weu
│   └── online          (internet-facing apps; policy: WAF required)
├── sandbox             (budget caps, auto-delete after 30 days)
└── decommissioned      (deny-all policy, awaiting deletion)
```

## Interview tips

- Name all four levels in order and say what boundary each one is - that is the whole question.
- The tags-do-not-inherit detail and the policy `modify` fix is a strong practical addition.
- Expect the AWS comparison: subscription ≈ account, management group ≈ OU, resource group has no AWS equivalent.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
- [[What are the different types of cloud services?]] (`#25`): [What are the different types of cloud services?](../cloud-platforms/what-are-the-different-types-of-cloud-services.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
