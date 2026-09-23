---
title: "How Does Azure Key Vault Managed HSM Differ from Standard Key Vault and How Do You Enforce Access?"
id: 742
category: "Azure Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - azure-engineering
  - key-vault
  - hsm
  - compliance
quiz:
  stem: "What is a major security distinction regarding data-plane access control in Azure Key Vault Managed HSM compared to Standard Key Vault?"
  options:
    - "Managed HSM keys are completely unencrypted in memory."
    - "Managed HSM uses its own local RBAC system, preventing even Azure Subscription Owners or Global Admins from accessing keys without explicit local role assignment."
    - "Managed HSM cannot be accessed via Azure Private Endpoints."
    - "Standard Key Vault does not support TLS encryption during transit."
  answer: 2
  explanation: "Managed HSM features an independent, local data-plane RBAC model. Subscription administrators and Entra ID Global Admins have no implicit access to cryptographic keys unless granted a specific Managed HSM local role."
---

# How Does Azure Key Vault Managed HSM Differ from Standard Key Vault and How Do You Enforce Access?

**Short answer:** Standard Azure Key Vault is a multi-tenant service with FIPS 140-2 Level 2/3 validation. Managed HSM is a fully single-tenant, dedicated Hardware Security Module cluster offering FIPS 140-2 Level 3 protection, automated cryptographic data isolation, and localized RBAC independent of Microsoft tenant administrators.

**Short answer:** Key Vault comes in **Standard** (software-protected keys, multi-tenant) and **Premium** (adds HSM-protected keys in multi-tenant HSMs validated to FIPS 140-3 Level 3). **Managed HSM** is a single-tenant pool of FIPS 140-3 Level 3 HSMs dedicated to you: you own its **security domain** (the key material that lets the HSM be activated or restored), and data-plane access is governed by **Managed HSM local RBAC**, separate from Azure RBAC - so a subscription Owner can manage the resource but cannot use the keys without a local role assignment. It stores keys only (no secrets or certificates) and costs a fixed hourly rate per HSM pool.

## Detail

### Key Architectural Differences

| Feature           | Key Vault (Standard / Premium)                                                   | Managed HSM                                                                     |
| :---------------- | :------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **Tenancy**       | Multi-tenant                                                                     | Single-tenant HSM pool                                                          |
| **Validation**    | Standard: software keys (FIPS 140 Level 1); Premium HSM keys: FIPS 140-3 Level 3 | FIPS 140-3 Level 3                                                              |
| **Objects**       | Keys, secrets, certificates                                                      | Keys only                                                                       |
| **Control plane** | Azure RBAC                                                                       | Azure RBAC (create, delete, network settings)                                   |
| **Data plane**    | Azure RBAC (recommended) or legacy access policies                               | Managed HSM local RBAC, scoped to the whole HSM or individual keys              |
| **Root of trust** | Microsoft-managed                                                                | Customer-held security domain (quorum of RSA keys)                              |
| **Throughput**    | Shared service limits per vault                                                  | Dedicated capacity per pool                                                     |
| **Resilience**    | Zone-redundant; replication to the paired region where one exists                | Zone-redundant within a region; optional multi-region replication; full backups |
| **Cost**          | Per operation (plus per HSM key on Premium)                                      | Fixed hourly price per pool, whether used or not                                |

### The Security Domain

Activating a new Managed HSM requires downloading its **security domain**, encrypted to a set of RSA public keys you supply (minimum three) with a quorum (for example, two of three) needed to decrypt it. Without the security domain and the quorum of private keys, nobody - including Microsoft - can restore the HSM's keys elsewhere; lose them and a disaster recovery restore is impossible. Store the private keys offline with separate custodians.

### Access Enforcement with Local RBAC

- Azure RBAC decides who can create, delete, or change the network settings of the HSM resource. **Local RBAC** decides who can create, use, or manage keys, and a subscription Owner or Global Administrator has no key access unless granted a local role.
- Built-in local roles include **Managed HSM Administrator**, **Managed HSM Crypto Officer** (key management), **Managed HSM Crypto User** (cryptographic operations), **Managed HSM Crypto Service Encryption User** (for Azure services using customer-managed keys), and **Managed HSM Backup** and **Policy Administrator** roles for operational separation.
- Assignments can be scoped to `/` (all keys) or `/keys/<name>`, which is how you give each application access to exactly one key.
- Lock the network down with private endpoints and disable public access, and send audit logs to Log Analytics.

**Trade-offs.** Managed HSM adds cost and operational duties (security domain custody, capacity, backups) that most workloads do not need; Key Vault Premium already provides FIPS 140-3 Level 3 HSM-protected keys. Choose Managed HSM when you need single-tenancy, full control of the root of trust, dedicated throughput, or specific regulatory requirements. For payment-industry HSM operations or full admin control of an HSM, Azure Payment HSM and Azure Cloud HSM are separate offerings.

### Real-World Production Scenario

A defense contractor must keep the root of trust for telemetry encryption keys under its own control, on single-tenant FIPS 140-3 Level 3 hardware. It provisions a Managed HSM, activates it with a 3-of-5 security domain quorum held by separate officers, grants the ground-station service principal **Managed HSM Crypto User** on one key only, and uses the Crypto Service Encryption User role for the storage accounts that use customer-managed keys.

## Example

```bash
# Create the HSM (control plane uses Azure RBAC); initial administrators get local admin
az keyvault create --hsm-name hsm-telemetry-prod -g rg-crypto -l westeurope \
  --administrators "$(az ad signed-in-user show --query id -o tsv)" --retention-days 90

# Activate by downloading the security domain, encrypted to three RSA public keys, quorum 2
az keyvault security-domain download --hsm-name hsm-telemetry-prod \
  --sd-wrapping-keys cert0.cer cert1.cer cert2.cer --sd-quorum 2 \
  --security-domain-file hsm-telemetry-prod-SD.json

# Create a key, then grant one app crypto access to that key only (local RBAC)
az keyvault key create --hsm-name hsm-telemetry-prod -n telemetry-kek --kty RSA-HSM --size 3072
az keyvault role assignment create --hsm-name hsm-telemetry-prod \
  --role "Managed HSM Crypto User" \
  --assignee-object-id "$APP_SP_OBJECT_ID" --scope /keys/telemetry-kek
```

## Interview tips

- Separate the tiers: Key Vault Standard (software), Premium (multi-tenant HSM, FIPS 140-3 Level 3), Managed HSM (single-tenant, customer-held security domain).
- Explain the control-plane versus data-plane split: Azure RBAC manages the resource; local RBAC governs key use, so subscription Owners cannot use keys by default.
- Mention the security domain and quorum - losing it makes recovery impossible, and it is the core of "customer-controlled root of trust".
- Note that Managed HSM stores keys only; secrets and certificates stay in Key Vault.
- Call out cost honestly: a fixed hourly charge per pool versus per-operation pricing, so Managed HSM needs a clear requirement to justify it.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?]] (`#543`): [How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?](../cloud-platforms/how-does-the-cloud-shared-responsibility-model-divide-security-obligations-between-iaas-paas-and-saas.md)
- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
