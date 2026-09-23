---
title: "How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?"
id: 543
category: "Cloud Platforms"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - cloud
  - security
  - shared-responsibility
  - compliance
quiz:
  stem: "Under the cloud Shared Responsibility Model, which component is ALWAYS the customer's responsibility across IaaS, PaaS, and SaaS?"
  options:
    - "Physical server hardware maintenance"
    - "Hypervisor kernel vulnerability patching"
    - "Customer data classification, access control, and identity management"
    - "Facility physical security guards"
  answer: 3
  explanation: "Across all service models, the customer retains sole responsibility for securing their data, managing user identities, and granting least-privilege IAM permissions."
---

# How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?

**Short answer:** The provider always secures the physical facilities, hardware, and virtualization layer; the customer always owns their data, identities, and access policies. In between, the line moves with the service model: in **IaaS** the customer patches the OS and configures the network; in **PaaS** the provider runs the OS and runtime while the customer owns code, dependencies, and configuration; in **SaaS** the provider runs the whole application and the customer owns who can use it, how it is configured, and what data goes in.

## Detail

A useful way to phrase it is the AWS wording: the provider is responsible for security _of_ the cloud, the customer for security _in_ the cloud.

```text
Layer                    IaaS (EC2/GCE/Azure VM)  PaaS (Lambda/App Service/Cloud Run)  SaaS (M365/Salesforce)
Data, identities, access Customer                 Customer                             Customer
Configuration / settings Customer                 Customer                             Customer
Application code         Customer                 Customer                             Provider
Libraries / dependencies Customer                 Customer (in your package/image)     Provider
Language runtime         Customer                 Provider (managed runtime)*          Provider
Operating system         Customer                 Provider                             Provider
Virtualization           Provider                 Provider                             Provider
Physical infrastructure  Provider                 Provider                             Provider

* Custom runtimes and container images move the runtime back to the customer.
```

**What stays with the customer everywhere:**

- Identity and access management - who has which role, MFA, federation, removing leavers.
- Data classification, encryption choices (including key management if you use customer-managed keys), retention, and sharing settings.
- Configuration of the service itself: a public S3 bucket or an over-shared SharePoint site is a customer failure even though the provider runs the platform.
- Endpoint devices and user behavior.

**Where people get it wrong.**

- Assuming "managed" means "secured". A managed database is patched by the provider, but network exposure, users, and backups retention are still yours.
- Forgetting deprecation deadlines are a customer duty in PaaS: when a Lambda or App Service runtime reaches end of support, the provider stops patching it and you must move your code to a supported version.
- Treating the provider's compliance certifications as your own. An ISO 27001 or SOC 2 report covers the provider's side; auditors still assess your configuration.

**Trade-off.** Moving up the stack hands over more patching and hardening, but also removes control - you cannot add a host-level agent to a SaaS product, and your evidence for audits comes from the provider's logs and reports rather than your own.

## Example

The same "customer-owned" control - blocking public data exposure - applied at the account level on AWS, where it is always your responsibility regardless of service model:

```bash
# Block all public access to S3 for the whole account (customer-side responsibility)
aws s3control put-public-access-block \
  --account-id 123456789012 \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Evidence for the provider's side comes from their reports, not your logs
aws artifact list-reports --max-results 5
```

## Interview tips

- Lead with the two constants: provider owns physical and virtualization, customer owns data, identity, and configuration.
- Walk the boundary through one concrete example per model - patching the OS on EC2, updating a Lambda runtime, managing MFA and sharing in Microsoft 365.
- Call out misconfiguration as the dominant real-world failure mode; it is almost always on the customer side of the line.
- Mention that provider certifications do not transfer - you inherit controls, you do not inherit compliance.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How Does Azure Key Vault Managed HSM Differ from Standard Key Vault and How Do You Enforce Access?]] (`#742`): [How Does Azure Key Vault Managed HSM Differ from Standard Key Vault and How Do You Enforce Access?](../azure-engineering/how-does-azure-key-vault-managed-hsm-differ-from-standard-key-vault-and-how-do-you-enforce-access.md)
- [[How Do You Configure Google Cloud Workload Identity for Secure GKE Service Authentication?]] (`#746`): [How Do You Configure Google Cloud Workload Identity for Secure GKE Service Authentication?](../gcp-engineering/how-do-you-configure-google-cloud-workload-identity-for-secure-gke-service-authentication.md)
- [[How Do You Implement VPC Service Controls to Prevent Data Exfiltration in Google Cloud?]] (`#750`): [How Do You Implement VPC Service Controls to Prevent Data Exfiltration in Google Cloud?](../gcp-engineering/how-do-you-implement-vpc-service-controls-to-prevent-data-exfiltration-in-google-cloud.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
