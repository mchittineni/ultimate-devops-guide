---
title: "How do you consume Azure Key Vault secrets from AKS and Azure Pipelines?"
id: 486
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
  - devsecops
  - kubernetes
---

# How do you consume Azure Key Vault secrets from AKS and Azure Pipelines?

**Short answer:** In **AKS**, use the **Azure Key Vault Provider for Secrets Store CSI Driver** with **workload identity**: a `SecretProviderClass` names the vault and the secrets, a Kubernetes service account is federated to a **user-assigned managed identity**, and the driver mounts the secrets as files into the Pod (optionally also syncing them into a Kubernetes Secret for `env` consumption). No credentials in the cluster, no secret in Git, and access is governed by Azure RBAC on the vault. In **Azure Pipelines**, link a **variable group to the Key Vault** (or use the `AzureKeyVault@2` task) through a **service connection using workload identity federation**, so the pipeline fetches secrets at run time and Azure DevOps stores nothing. The critical operational detail people miss: **mounted secrets do not refresh on their own by default** - the CSI driver needs `enableSecretRotation` with a rotation poll interval, and even then a container that read the value into memory at startup keeps using the old one, so **rotation requires either a rolling restart or an application that re-reads the file**.

## Detail

### AKS: the three mechanisms, and which to choose

| Approach                                         | How it works                                                                | Verdict                                                                                                             |
| ------------------------------------------------ | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Secrets Store CSI driver + workload identity** | `SecretProviderClass` + federated service account; secrets mounted as files | **Default choice.** No secret in etcd unless you opt into syncing, per-Pod identity, Azure RBAC and audit           |
| **External Secrets Operator**                    | Controller syncs vault values into Kubernetes Secrets on a schedule         | Good when you want normal `Secret` objects (for `envFrom`, or for tools that need them) and multi-cloud consistency |
| **Manually created Kubernetes Secret**           | Someone runs `kubectl create secret` or commits a manifest                  | Avoid. No rotation, no audit, base64 in Git if you are careless                                                     |

Two identity mechanisms exist and only one is current: **Microsoft Entra Workload ID** (OIDC federation - a Kubernetes service account token exchanged for an Entra token) is the supported model; **AAD Pod Identity** is deprecated. Do not use the **kubelet identity** for application access - every Pod on the node inherits it, which is the Azure equivalent of using the node instance profile on EKS.

Set up in order: enable OIDC issuer and workload identity on the cluster, create a user-assigned managed identity, grant it **Key Vault Secrets User** via Azure RBAC on the vault (or an access policy if the vault still uses the legacy model), create a federated credential mapping `system:serviceaccount:<namespace>:<name>` to that identity, annotate the Kubernetes service account with the client ID, and label the Pod `azure.workload.identity/use: "true"`.

### Rotation: the question behind the question

_"When a secret is rotated in Key Vault, how does the running Pod pick up the new value?"_ Be precise, because the honest answer has three layers:

1. **The mount** - with `enableSecretRotation=true` and `rotationPollInterval` (default 2 minutes) on the CSI driver, the mounted file is updated in place. Without it, the file keeps the value from Pod start, forever.
2. **The synced Kubernetes Secret** - if you use `secretObjects`, the Secret is updated too, but **environment variables from a Secret are fixed at container start**, so an `env`-consuming app never sees the new value.
3. **The application** - even with an updated file, a process that read the value once at startup holds the old one in memory.

So the working patterns are: the application **watches the file** and reloads (best), or you trigger a **rolling restart** after rotation (`kubectl rollout restart`, or Reloader/Stakater watching the Secret), or you use short-lived credentials so rotation is the norm rather than an event. Mounting as a **file rather than an env var** is the prerequisite for any of this. And the strongest version - use **Entra ID authentication to the database or service** with a token fetched per request, so there is no long-lived secret to rotate at all.

### Azure Pipelines

- **Variable group linked to Key Vault** (Library → Variable group → Link secrets from an Azure key vault) is the tidiest: secrets appear as pipeline variables, are masked in logs, and are fetched at run time. The service connection's identity needs **Get** and **List** on secrets.
- **`AzureKeyVault@2` task** when you want to fetch inside a specific job or filter by name pattern.
- **Masked, not safe**: masking replaces exact matches. A secret that is base64-encoded, split, or printed by a tool as part of a larger string is **not** masked. Keep `--debug`/`system.debug` off in production pipelines.
- **Secret variables need explicit `env:` mapping** to reach a script - they are deliberately not injected automatically.
- **Service connection with workload identity federation** rather than a service principal secret: nothing to rotate, no annual expiry outage, and the trust is scoped to the project and pipeline.
- **Private vaults**: if the Key Vault has a private endpoint and public access disabled, a Microsoft-hosted agent cannot reach it. Use a **self-hosted agent** inside the VNet (or an agent pool in AKS), which is the real answer to "how is networking established between the pipeline and Key Vault?" - identity gets you authorised, but you still need a network path.

### Vault design and access control

- **Azure RBAC over access policies.** The RBAC model gives you granular roles (Key Vault Secrets User, Secrets Officer, Administrator, Crypto User), inherits from management groups, and is auditable like everything else in Azure. Access policies are the legacy model with coarser permissions.
- **A vault per environment**, not one vault with prefixed names - so a dev identity cannot read production secrets and the RBAC boundary matches the blast radius.
- **Soft delete and purge protection on** (purge protection is required for some compliance profiles and cannot be turned off once enabled).
- **Private endpoint** plus firewall rules with "allow trusted Microsoft services" only where genuinely needed.
- **Diagnostic logs to Log Analytics** so you can answer "who read this secret and when?" - the audit trail is a large part of why you use a vault rather than a Kubernetes Secret.
- **Certificates in Key Vault** with auto-renewal from an integrated CA, consumed by Application Gateway and App Service - which is also where the `.csr` → `.cer` → `.pfx` workflow ends up automated rather than manual.

### The equivalents elsewhere

Worth a sentence, because interviewers switch platforms: AWS uses **IRSA or EKS Pod Identity** with Secrets Manager (or the same CSI driver with the AWS provider), and GCP uses **Workload Identity** with Secret Manager. The pattern is identical - federate a Kubernetes service account to a cloud identity, then let the platform vend short-lived credentials - and saying that shows the concept rather than the product is what you understand.

## Example

```bash
# One-time cluster and identity setup
az aks update -g rg-prod -n aks-prod --enable-oidc-issuer --enable-workload-identity

az identity create -g rg-prod -n id-payments
CLIENT_ID=$(az identity show -g rg-prod -n id-payments --query clientId -o tsv)
OIDC=$(az aks show -g rg-prod -n aks-prod --query oidcIssuerProfile.issuerUrl -o tsv)

# Azure RBAC on the vault - least privilege, not "Contributor"
az role assignment create --role "Key Vault Secrets User" \
  --assignee-object-id "$(az identity show -g rg-prod -n id-payments --query principalId -o tsv)" \
  --assignee-principal-type ServicePrincipal \
  --scope "$(az keyvault show -g rg-prod -n kv-payments-prod --query id -o tsv)"

# Federate the Kubernetes service account to the managed identity
az identity federated-credential create --name payments-fed \
  --identity-name id-payments -g rg-prod --issuer "$OIDC" \
  --subject "system:serviceaccount:payments:payments-sa" \
  --audience api://AzureADTokenExchange
```

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payments-sa
  namespace: payments
  annotations:
    azure.workload.identity/client-id: "00000000-1111-2222-3333-444444444444"
---
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata: { name: kv-payments, namespace: payments }
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    clientID: "00000000-1111-2222-3333-444444444444" # workload identity
    keyvaultName: kv-payments-prod
    tenantId: "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    objects: |
      array:
        - |
          objectName: db-password
          objectType: secret
        - |
          objectName: api-key
          objectType: secret
  secretObjects: # optional: also sync into a Kubernetes Secret
    - secretName: payments-secrets
      type: Opaque
      data:
        - { objectName: db-password, key: DB_PASSWORD }
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: payments, namespace: payments }
spec:
  template:
    metadata:
      labels:
        app: payments
        azure.workload.identity/use: "true" # required for the token projection
    spec:
      serviceAccountName: payments-sa
      containers:
        - name: app
          image: acrprod.azurecr.io/payments:1.9.0
          volumeMounts:
            - name: secrets
              mountPath: /mnt/secrets # FILES: can be refreshed; env vars cannot
              readOnly: true
      volumes:
        - name: secrets
          csi:
            driver: secrets-store.csi.k8s.io
            readOnly: true
            volumeAttributes: { secretProviderClass: kv-payments }
```

```bash
# Rotation actually working requires the driver to poll AND something to react
helm upgrade csi-secrets-store csi-secrets-store-provider-azure/csi-secrets-store-provider-azure \
  -n kube-system --set secrets-store-csi-driver.enableSecretRotation=true \
  --set secrets-store-csi-driver.rotationPollInterval=2m

az keyvault secret set --vault-name kv-payments-prod --name db-password --value 'new-value'
# the mounted FILE updates within the poll interval:
kubectl exec -n payments deploy/payments -- cat /mnt/secrets/db-password
# an app that read it at startup still holds the old value -> restart or watch the file
kubectl rollout restart deploy/payments -n payments
```

```yaml
# Azure Pipelines: variable group linked to Key Vault + federated service connection
variables:
  - group: payments-kv # linked to kv-payments-prod; secrets fetched at run time
steps:
  - task: AzureKeyVault@2 # or fetch explicitly in a job
    inputs:
      azureSubscription: sc-prod-federated # workload identity federation: no secret
      KeyVaultName: kv-payments-prod
      SecretsFilter: "db-password,api-key"
      RunAsPreJob: true
  - script: |
      psql "postgresql://app:$DB_PASSWORD@db.postgres.database.azure.com/orders" -c 'select 1'
    env:
      DB_PASSWORD: $(db-password) # explicit mapping: secret vars are not auto-injected
```

## Interview tips

- Answer AKS with the **Secrets Store CSI driver plus workload identity**, and say why: no credential in the cluster, per-Pod identity, Azure RBAC and audit on the vault. Mention External Secrets Operator as the alternative when you specifically want Kubernetes `Secret` objects.
- Say **AAD Pod Identity is deprecated** and that you never use the kubelet identity for application access, because every Pod on the node would inherit it. That pair of facts dates your knowledge correctly.
- For the rotation question, give all three layers - the CSI mount needs `enableSecretRotation`, env vars from a Secret are fixed at container start, and the application may still hold the value in memory - then the fixes: mount as a file and watch it, or roll the Deployment (Reloader), or use Entra ID tokens so there is nothing long-lived to rotate. This is the highest-value part of the whole answer.
- Emphasise mounting **files, not environment variables**, as the prerequisite for refresh.
- For pipelines, recommend a variable group **linked to Key Vault** plus a service connection using **workload identity federation**, and note that a service principal secret expiring is a self-inflicted annual outage.
- Warn that masking only catches exact matches, and that secret variables need explicit `env:` mapping to reach a script.
- Raise the network half of the question: a private-endpoint vault is unreachable from a Microsoft-hosted agent, so you need a self-hosted agent in the VNet. Identity and network path are separate problems.
- Prefer **Azure RBAC over access policies**, a **vault per environment**, purge protection on, and diagnostic logs to Log Analytics for the "who read this secret?" audit trail.
- Close by mapping the pattern to AWS (IRSA / Pod Identity) and GCP (Workload Identity) to show you understand federation rather than one product. See [what is Azure Kubernetes Service (AKS)](./what-is-azure-kubernetes-service-aks.md), [what is Microsoft Entra ID and how does Azure RBAC work](./what-is-microsoft-entra-id-and-how-does-azure-rbac-work.md), [ConfigMaps and Secrets in Kubernetes](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md), and [rotating secrets without downtime](../devsecops/how-do-you-rotate-secrets-without-downtime.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between a ConfigMap and a Secret in Kubernetes?]] (`#442`): [What is the difference between a ConfigMap and a Secret in Kubernetes?](../kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)
- [[How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?]] (`#405`): [How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
