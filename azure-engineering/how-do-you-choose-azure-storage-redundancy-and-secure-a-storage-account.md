---
title: "How do you choose Azure Storage redundancy and secure a storage account?"
id: 756
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - azure-engineering
  - storage
  - security-and-compliance
quiz:
  stem: "A storage account must survive the loss of an availability zone with no data loss, and also keep a copy in another region for a regional disaster. Which redundancy option fits?"
  options:
    - "LRS"
    - "GRS"
    - "GZRS"
    - "ZRS"
  answer: 3
  explanation: "GZRS replicates synchronously across three zones in the primary region (so a zone loss loses no data) and asynchronously to the paired region. GRS also copies to the paired region, but within the primary region it is only LRS - three copies in a single datacenter - so a zone outage takes the primary down. ZRS survives a zone loss but has no second region."
---

# How do you choose Azure Storage redundancy and secure a storage account?

**Short answer:** Redundancy is two independent choices: **within the primary region** - LRS (three copies in one datacenter) or ZRS (synchronously across three availability zones) - and **whether to copy asynchronously to the paired region** - GRS (LRS + secondary) or GZRS (ZRS + secondary), optionally with **read access** to the secondary (RA-GRS / RA-GZRS). Pick ZRS as the production default, add geo-replication when you need a regional DR copy, and remember the geo copy is **asynchronous** (check `LastSyncTime`; there is no RPO SLA). Securing the account is a short, fixed baseline: **Entra ID RBAC instead of account keys** (disable shared key access), **no anonymous blob access**, **private endpoints with public network access disabled**, TLS 1.2 minimum, and **soft delete, versioning, and immutability** for recovery from deletion and ransomware.

## Detail

### The redundancy options

| Option           | Primary region                 | Secondary region      | Survives                            | Notes                                                  |
| ---------------- | ------------------------------ | --------------------- | ----------------------------------- | ------------------------------------------------------ |
| LRS              | 3 copies, one datacenter       | -                     | Disk/rack failure                   | Cheapest; a datacenter or zone outage takes it offline |
| ZRS              | 3 copies across 3 zones (sync) | -                     | Zone loss, no data loss             | The sensible production default                        |
| GRS              | LRS                            | LRS, async            | Regional disaster (after failover)  | Primary is still single-datacenter                     |
| GZRS             | ZRS                            | LRS, async            | Zone loss **and** regional disaster | Highest durability                                     |
| RA-GRS / RA-GZRS | as above                       | **Readable** endpoint | Reads continue during an outage     | Readers must tolerate replication lag                  |

Two details carry the answer. First, **geo-replication is asynchronous**: anything written after the last sync point is lost if the primary region is gone, so state RPO as "typically minutes, not guaranteed" and monitor `LastSyncTime`. Second, the secondary is **not writable until you fail over**:

- **Unplanned (customer-managed) failover** promotes the secondary when the primary is unavailable; writes after the last sync are lost, and the account becomes locally redundant in the new region until you re-enable geo-replication.
- **Planned failover** (GA late 2025) swaps primary and secondary with no data loss while both regions are healthy - the tool for DR drills - and keeps geo-redundancy.
- Microsoft-managed failover happens only for a region-wide disaster and is not something to design around.

Premium accounts (premium block blobs, file shares) support only LRS or ZRS, and not every region has a pair or zones - check before promising GZRS.

### Access tiers and lifecycle

Blob data has **Hot**, **Cool** (30-day minimum), **Cold** (90-day minimum), and **Archive** (180-day minimum, offline - rehydration takes hours) tiers. Lifecycle management policies move blobs down the tiers by last-modified or last-access time and delete old versions and snapshots - the same cost discipline as S3 lifecycle rules, with the same early-deletion trap.

### The security baseline

| Control                 | Setting                                                                                             | Why                                                                |
| ----------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Authorisation           | Entra ID + data-plane roles (`Storage Blob Data Reader/Contributor`); `allowSharedKeyAccess: false` | Account keys are full-control passwords that never expire          |
| Delegated access        | **User delegation SAS** (signed with Entra credentials), short expiry                               | Account-key SAS cannot be revoked without rotating the key         |
| Anonymous access        | `allowBlobPublicAccess: false`                                                                      | Stops the "public container" leak regardless of container settings |
| Network                 | Private endpoints, `publicNetworkAccess: Disabled`, private DNS zones                               | Removes the internet path; leaked credentials are useless outside  |
| Transport               | `minimumTlsVersion: TLS1_2`, HTTPS only                                                             | Older TLS versions are being retired                               |
| Encryption              | Microsoft-managed keys by default; customer-managed keys in Key Vault where required                | Key control and revocation for regulated data                      |
| Recovery                | Blob and container soft delete, versioning, point-in-time restore                                   | Undo accidental deletes and overwrites                             |
| Immutability            | Time-based retention or legal hold (WORM), locked when proven                                       | Ransomware and compliance: even an Owner cannot delete             |
| Detection               | Diagnostic logs to Log Analytics, Defender for Storage                                              | "Who read this?" and malware/anomaly alerts                        |
| Deletion of the account | A `CanNotDelete` resource lock                                                                      | Soft delete does not protect against deleting the whole account    |

Enforce the baseline with Azure Policy (`Deny` on public access, shared key access, and public network access) rather than relying on each team to remember it.

## Example

```bash
# Zone- and geo-redundant, keyless, private, TLS 1.2
az storage account create -g rg-data -n stpaymentsprodweu -l westeurope \
  --kind StorageV2 --sku Standard_GZRS \
  --allow-blob-public-access false --allow-shared-key-access false \
  --min-tls-version TLS1_2 --https-only true \
  --public-network-access Disabled

# Recovery features: soft delete, container soft delete, versioning
az storage account blob-service-properties update -g rg-data -n stpaymentsprodweu \
  --enable-delete-retention true --delete-retention-days 14 \
  --enable-container-delete-retention true --container-delete-retention-days 14 \
  --enable-versioning true

# Data-plane RBAC instead of keys
az role assignment create --role "Storage Blob Data Contributor" \
  --assignee-object-id "$APP_PRINCIPAL_ID" --assignee-principal-type ServicePrincipal \
  --scope "$(az storage account show -g rg-data -n stpaymentsprodweu --query id -o tsv)"

# How far behind is the secondary? (your real RPO right now)
az storage account show -g rg-data -n stpaymentsprodweu --expand geoReplicationStats \
  --query geoReplicationStats.lastSyncTime -o tsv

# Protect the account itself from deletion
az lock create -g rg-data -n no-delete-storage --lock-type CanNotDelete \
  --resource-type Microsoft.Storage/storageAccounts --resource stpaymentsprodweu
```

## Interview tips

- Split redundancy into the two questions - in-region (LRS or ZRS) and cross-region (geo or not) - and the four SKUs fall out of it. Recommend ZRS as the default and GZRS when a regional DR copy is required.
- Say that geo-replication is **asynchronous**, the RPO is not guaranteed, and `LastSyncTime` is how you measure it. Then distinguish unplanned failover (possible data loss, ends up LRS) from planned failover (no data loss, for drills).
- Point out that GRS is single-datacenter in the primary region - the trap in "GRS is the most resilient option".
- For security, lead with disabling shared key access and using Entra RBAC plus user delegation SAS, then private endpoints and no anonymous access. Those three remove most real-world storage breaches.
- Add soft delete, versioning, and locked immutability policies as the ransomware answer, and a resource lock for the account itself.
- Map it across clouds if asked: ZRS ≈ S3 Standard's multi-AZ storage, GRS/GZRS ≈ S3 Cross-Region Replication, immutability ≈ S3 Object Lock. See [what are the S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md), [what is Azure Policy and how do landing zones use it](./what-is-azure-policy-and-how-do-landing-zones-use-it.md), and [what is Microsoft Entra ID and how does Azure RBAC work](./what-is-microsoft-entra-id-and-how-does-azure-rbac-work.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core differences between Cloud Object Storage, Block Storage, and File Storage?]] (`#545`): [What are the core differences between Cloud Object Storage, Block Storage, and File Storage?](../cloud-platforms/what-are-the-core-differences-between-cloud-object-storage-block-storage-and-file-storage.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
- [[How does networking differ across AWS, Azure, and GCP?]] (`#282`): [How does networking differ across AWS, Azure, and GCP?](../cloud-platforms/how-does-networking-differ-across-aws-azure-and-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
