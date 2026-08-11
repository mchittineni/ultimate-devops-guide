---
title: "What is the difference between a managed identity, a service principal, and an app registration?"
id: 488
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
  - devsecops
---

# What is the difference between a managed identity, a service principal, and an app registration?

**Short answer:** An **app registration** is the _application definition_ in Microsoft Entra ID - the global object describing an application, its client ID, redirect URIs, exposed scopes, and required permissions. A **service principal** is the _local instance_ of that application in a specific tenant - the actual security principal you assign RBAC roles to. So the relationship is: an app registration creates a service principal in your tenant, and the service principal is what gets permissions. A **managed identity** is a special kind of service principal whose **credentials are created, stored, and rotated by Azure**, and which you never see or handle - it exists only for Azure resources to authenticate to Azure services. The practical decision: **use a managed identity wherever the workload runs on an Azure resource that supports one** (App Service, Functions, VMs, AKS via workload identity, Container Apps, Data Factory), because there is no secret to leak, rotate, or expire; use an app registration with a service principal when the caller is **outside Azure** or needs OAuth flows a managed identity cannot do - and even then, prefer **federated credentials** over a client secret so there is still nothing to rotate.

## Detail

### How the three relate

```text
App registration  (Application object - global, one per application)
        │  clientId, redirect URIs, exposed API scopes, requested permissions
        │
        ├── creates ──> Service principal in tenant A   <- RBAC roles assigned HERE
        └── creates ──> Service principal in tenant B      (multi-tenant apps)

Managed identity  = a service principal with Azure-managed credentials
                    (no app registration you own, no secret you handle)
```

Two consequences worth stating: you assign a **role** (Reader, Contributor, Key Vault Secrets User) to the **service principal**, not to the app registration; and in a multi-tenant scenario one app registration has a separate service principal - and separate consent and permissions - in every tenant that uses it.

### Managed identity: system-assigned versus user-assigned

|                  | System-assigned                                 | User-assigned                                                                           |
| ---------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------- |
| Lifecycle        | Tied to one resource; deleted with it           | Independent resource; survives                                                          |
| Shared           | No - exactly one resource                       | **Yes** - many resources can use the same identity                                      |
| Role assignments | Recreated if the resource is recreated          | Assigned once, stable                                                                   |
| Good for         | A single VM or App Service that needs one thing | Anything managed by IaC, AKS workload identity, blue/green where resources are replaced |

The IaC argument matters: with a system-assigned identity, replacing the resource creates a **new** principal with a new object ID, so every role assignment must be recreated - which makes Terraform plans noisy and can break access mid-deployment. A **user-assigned** identity is created once, granted roles once, and attached to whatever resources need it. That is usually the right default in a Terraform-managed estate.

Mechanically, a managed identity works through a **local token endpoint** on the resource (IMDS on a VM, an environment-provided endpoint in App Service). The Azure SDK's `DefaultAzureCredential` finds it automatically, so the same code works locally with a developer login and in Azure with the managed identity - which is the practical reason to use it.

### When you still need an app registration and service principal

- **Callers outside Azure**: a GitHub Actions or Azure DevOps pipeline, an on-premises job, a script on a laptop, another cloud.
- **OAuth flows a managed identity cannot perform**: interactive user sign-in, delegated permissions on behalf of a user, exposing an API with scopes, multi-tenant SaaS.
- **Third-party integrations** that require a client ID and a credential.

For all of these, use **federated credentials (workload identity federation)** rather than a client secret: the app registration trusts an external OIDC issuer (GitHub, Azure DevOps, another Kubernetes cluster) for a specific subject, and the caller exchanges its own token for an Entra token. No secret exists, so nothing expires and nothing can be exfiltrated. The classic failure this removes is the annual outage when a service principal's client secret expires at 2 a.m. and every deployment stops - which is worth naming, because it is a real and common incident.

If a secret or certificate is genuinely unavoidable, prefer a **certificate** over a client secret, store it in Key Vault, set a short expiry, and alert 30 days before it lapses.

### AKS: the specific case

Do not use a service principal for the cluster or for workloads. The cluster should use a **managed identity**; workloads should use **Microsoft Entra Workload ID**, which federates a Kubernetes service account to a **user-assigned managed identity** through the cluster's OIDC issuer. AAD Pod Identity is deprecated, and using the **kubelet identity** for application access is wrong because every Pod on the node inherits it. See [consuming Azure Key Vault secrets from AKS and Azure Pipelines](./how-do-you-consume-azure-key-vault-secrets-from-aks-and-azure-pipelines.md).

### The equivalents on other clouds

Say this if the interviewer switches platform, because it shows you understand the concept rather than the branding: a managed identity is AWS's **instance profile / task role / IRSA** and GCP's **attached service account with Workload Identity**; an app registration with federated credentials is AWS's **OIDC role trust policy** and GCP's **Workload Identity Federation**. In every case the pattern is the same - bind a verifiable workload identity to a role and let the platform vend short-lived credentials.

### Governance

- **Own the lifecycle**: app registrations proliferate. Tag them with an owner, review unused ones (sign-in logs show last use), and have an expiry policy for credentials.
- **Least privilege at the right scope**: assign the role at the resource or resource-group scope, not the subscription, and prefer built-in roles like Key Vault Secrets User over Contributor.
- **Restrict who may create them**: by default many tenants allow any user to register an application - turn that off and route requests through a process.
- **Audit**: Entra sign-in logs for service principals, plus Azure Activity Log for what the identity did. "Which app registrations have secrets expiring in the next 60 days?" should be a scheduled query, not a discovery during an incident.

## Example

```bash
# A user-assigned managed identity: created once, roles assigned once, attached anywhere
az identity create -g rg-prod -n id-payments
PRINCIPAL=$(az identity show -g rg-prod -n id-payments --query principalId -o tsv)

az role assignment create --assignee-object-id "$PRINCIPAL" \
  --assignee-principal-type ServicePrincipal \
  --role "Key Vault Secrets User" \
  --scope "$(az keyvault show -g rg-prod -n kv-payments --query id -o tsv)"

# attach it to the workloads that need it - no secret anywhere in this flow
az webapp identity assign -g rg-prod -n app-payments \
  --identities "$(az identity show -g rg-prod -n id-payments --query id -o tsv)"
```

```csharp
// The application code is identical locally and in Azure - no credentials in it
var client = new SecretClient(
    new Uri("https://kv-payments.vault.azure.net/"),
    new DefaultAzureCredential());          // dev: az login | Azure: managed identity
var pw = await client.GetSecretAsync("db-password");
```

```bash
# A caller OUTSIDE Azure: app registration + FEDERATED credential (no client secret)
APP_ID=$(az ad app create --display-name gha-payments-deploy --query appId -o tsv)
az ad sp create --id "$APP_ID"                     # the service principal in this tenant

az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:acme/payments:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

az role assignment create --assignee "$APP_ID" --role Contributor \
  --scope /subscriptions/SUBID/resourceGroups/rg-prod    # scoped, not subscription-wide
```

```yaml
# The pipeline side: OIDC, so there is no secret to store or rotate
- uses: azure/login@v2
  with:
    client-id: ${{ vars.AZURE_CLIENT_ID }} # not a secret - just an ID
    tenant-id: ${{ vars.AZURE_TENANT_ID }}
    subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
    # no client-secret: the federated credential does the work
```

```bash
# Governance: find the secrets that will break a deployment next quarter
az ad app list --all --query "[?passwordCredentials[?endDateTime < '2026-11-01']]
  .{app:displayName, id:appId, expires:passwordCredentials[0].endDateTime}" -o table

# Which service principals have not signed in for 90 days?
az ad sp list --all --query "[].{name:displayName,id:appId}" -o tsv | head
# (cross-reference with Entra sign-in logs in Log Analytics)

# What did this identity actually do?
az monitor activity-log list --caller "$APP_ID" --start-time "$(date -u -d '-7 days' +%FT%TZ)" \
  --query '[].{op:operationName.value,status:status.value,time:eventTimestamp}' -o table
```

## Interview tips

- Give the relationship first: an app registration is the **application definition** (global), a service principal is its **instance in a tenant** and the thing you assign roles to, and a managed identity is a service principal whose credentials **Azure manages for you**. That hierarchy is the answer.
- State the decision rule plainly: managed identity whenever the workload runs on an Azure resource that supports one; app registration plus service principal when the caller is outside Azure or needs an OAuth flow a managed identity cannot do.
- Volunteer the **user-assigned versus system-assigned** distinction and the IaC argument - recreating a resource with a system-assigned identity creates a new principal and orphans every role assignment. Recommending user-assigned as the Terraform default reads as experience.
- Push federated credentials hard for external callers, and name the incident they prevent: a client secret expiring and stopping every deployment. That story lands better than "it is more secure".
- If a credential is unavoidable, say certificate over client secret, stored in Key Vault, with a 30-day expiry alert.
- For AKS, say the cluster uses a managed identity and workloads use **Entra Workload ID** federated to a user-assigned identity; note that AAD Pod Identity is deprecated and the kubelet identity must not be used for application access.
- Mention that roles are assigned to the **service principal**, at the resource or resource-group scope, using built-in least-privilege roles rather than Contributor.
- Close by mapping to AWS (instance profile / task role / IRSA, and OIDC role trust) and GCP (attached service account, Workload Identity Federation) so it is clear you understand federation as a pattern. See [what is Microsoft Entra ID and how does Azure RBAC work](./what-is-microsoft-entra-id-and-how-does-azure-rbac-work.md), [how is the Azure resource hierarchy organised](./how-is-the-azure-resource-hierarchy-organised.md), [authenticating to AWS without long-lived access keys](../aws-engineering/how-do-you-authenticate-to-aws-without-long-lived-access-keys.md), and [designing least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is the difference between a ConfigMap and a Secret in Kubernetes?]] (`#442`): [What is the difference between a ConfigMap and a Secret in Kubernetes?](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)
- [[How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?]] (`#405`): [How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
