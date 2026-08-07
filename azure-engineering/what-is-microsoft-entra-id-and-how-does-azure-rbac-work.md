---
title: "What is Microsoft Entra ID and how does Azure RBAC work?"
id: 200
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
---

# What is Microsoft Entra ID and how does Azure RBAC work?

**Short answer:** Entra ID (formerly Azure AD) is the identity provider — it authenticates users, groups, and workload identities. Azure RBAC is the authorisation layer that grants those identities permissions on Azure resources through role assignments scoped to a management group, subscription, resource group, or single resource. Entra roles govern the directory; Azure RBAC governs resources, and mixing them up is a common interview slip.

## Detail

**A role assignment has three parts:** the security principal (user, group, service principal, or managed identity), the role definition (a set of allowed and denied operations), and the scope. Assignments inherit downward, and the effective permission is the union of all matching assignments — except that a `Deny` assignment (used by Azure Blueprints and managed apps) always wins.

**Managed identities remove secrets.** A system-assigned managed identity is tied to one resource's lifecycle; a user-assigned identity is a standalone resource shared by several. Either way, the platform issues tokens through the instance metadata endpoint, so no credential exists in configuration. For CI/CD outside Azure, workload identity federation lets a GitHub Actions or GitLab OIDC token exchange for Azure tokens — the modern replacement for a service-principal secret.

**Prefer built-in roles, then narrow custom ones.** Owner, Contributor, and Reader are the coarse trio; Contributor notably cannot grant access, which is why `User Access Administrator` exists separately. Custom roles matter when a team needs, say, restart-but-not-delete on virtual machines. Assign to groups, never to individuals, so joiner/leaver processes work.

**Privileged Identity Management for standing access.** PIM makes privileged roles eligible rather than active: the engineer activates the role for a limited window, with justification, approval, and MFA. Combined with Conditional Access (device compliance, location, risk level) this is the Azure implementation of least privilege for humans, and it is what auditors look for.

**Layered controls beyond RBAC.** Azure Policy decides whether a resource _may exist_ in a given shape; RBAC decides who may act. Resource locks (`CanNotDelete`, `ReadOnly`) protect against accidents even by owners. All three are complementary, and interviews often probe whether you know that RBAC alone cannot enforce configuration standards.

**Common pitfalls worth naming:** role assignments at subscription scope that should have been at resource-group scope; guest users inheriting more than intended; service principals with `Contributor` on a whole subscription used by pipelines; and forgetting that RBAC changes can take a few minutes to propagate.

## Example

```bash
# Workload identity federation: GitHub Actions gets Azure tokens with no stored secret
az ad app create --display-name gha-checkout
APP_ID=$(az ad app list --display-name gha-checkout --query '[0].appId' -o tsv)
az ad sp create --id "$APP_ID"

az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "gha-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:acme/checkout:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

# Least privilege: scope the assignment to one resource group, not the subscription
az role assignment create \
  --assignee "$APP_ID" \
  --role "Contributor" \
  --scope "/subscriptions/$SUB_ID/resourceGroups/rg-checkout-prod-weu"
```

## Interview tips

- State the split clearly: Entra roles govern the directory, Azure RBAC governs resources.
- Managed identities and workload identity federation are the answers to every "how do you avoid secrets?" follow-up.
- Mention PIM plus Conditional Access for human access, and Azure Policy for what RBAC cannot express.

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
