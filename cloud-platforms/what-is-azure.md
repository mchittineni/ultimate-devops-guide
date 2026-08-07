---
title: "What is Azure?"
id: 23
category: "Cloud Platforms"
difficulty: "Beginner"
tags:
  - devops
  - cloud-platforms
  - interview-questions
---

# What is Azure?

**Short answer:** Microsoft Azure is Microsoft's cloud platform, strongest in enterprises already invested in Microsoft technology thanks to deep integration with Entra ID (formerly Azure AD), Windows Server, and Microsoft 365.

## Detail

Core services and their AWS analogues:

| Category             | Azure                         | AWS equivalent        |
| -------------------- | ----------------------------- | --------------------- |
| Virtual machines     | Azure Virtual Machines        | EC2                   |
| Managed Kubernetes   | AKS                           | EKS                   |
| Serverless functions | Azure Functions               | Lambda                |
| Object storage       | Blob Storage                  | S3                    |
| Relational database  | Azure SQL / Flexible Server   | RDS                   |
| NoSQL                | Cosmos DB                     | DynamoDB              |
| Identity             | Microsoft Entra ID            | IAM + Identity Center |
| IaC                  | ARM templates / Bicep         | CloudFormation        |
| CI/CD                | Azure DevOps / Pipelines      | CodePipeline          |
| Monitoring           | Azure Monitor + Log Analytics | CloudWatch            |
| Secrets              | Key Vault                     | Secrets Manager + KMS |

Azure organises resources hierarchically: **management groups → subscriptions → resource groups → resources**. Resource groups are a genuine lifecycle boundary - you can deploy, tag, and delete a whole group together, which has no direct AWS equivalent.

**Azure Policy** enforces governance rules (allowed regions, required tags, denied SKUs) across subscriptions, and is the usual answer for compliance at scale. **Managed identities** give a VM or app a rotating identity in Entra ID so code never handles credentials.

## Interview tips

- Hierarchy and resource groups are the Azure-specific concept most often tested.
- Managed identities are Azure's answer to "how do you avoid secrets in config?"
- If the role is hybrid-cloud, mention Azure Arc for managing on-premises and other-cloud resources.

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
