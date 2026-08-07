---
title: "How do the core services of AWS, Azure, and GCP map to each other?"
id: 221
category: "Cloud Engineering"
difficulty: "Beginner"
tags:
  - devops
  - cloud-engineering
  - interview-questions
---

# How do the core services of AWS, Azure, and GCP map to each other?

**Short answer:** Most primitives map closely — compute, object storage, managed Kubernetes, IAM, and monitoring exist everywhere with different names. The mappings that are _not_ one-to-one are the interesting ones: GCP's VPC is global while AWS and Azure networks are regional, Azure adds resource groups and a management-group layer above subscriptions, and each provider's serverless and data services differ in semantics as well as naming.

## Detail

| Capability              | AWS                        | Azure                           | GCP                              |
| ----------------------- | -------------------------- | ------------------------------- | -------------------------------- |
| Tenancy boundary        | account                    | subscription (+ resource group) | project                          |
| Policy grouping         | organizational unit + SCP  | management group + Azure Policy | folder + org policy              |
| Virtual machines        | EC2                        | Virtual Machines                | Compute Engine                   |
| Autoscaling group       | Auto Scaling group         | VM Scale Set                    | Managed Instance Group           |
| Managed Kubernetes      | EKS                        | AKS                             | GKE                              |
| Serverless containers   | ECS/Fargate, App Runner    | Container Apps                  | Cloud Run                        |
| Functions               | Lambda                     | Azure Functions                 | Cloud Run functions              |
| Object storage          | S3                         | Blob Storage                    | Cloud Storage                    |
| Block storage           | EBS                        | Managed Disks                   | Persistent Disk / Hyperdisk      |
| Managed relational      | RDS / Aurora               | Azure SQL / Flexible Server     | Cloud SQL / AlloyDB              |
| Global-scale relational | Aurora Global / DSQL       | Cosmos DB (multi-model)         | Spanner                          |
| Key-value / NoSQL       | DynamoDB                   | Cosmos DB                       | Firestore / Bigtable             |
| Data warehouse          | Redshift                   | Fabric / Synapse                | BigQuery                         |
| Managed streaming       | Kinesis / MSK              | Event Hubs                      | Pub/Sub                          |
| Queue                   | SQS                        | Service Bus / Storage Queues    | Pub/Sub (or Cloud Tasks)         |
| Secrets                 | Secrets Manager            | Key Vault                       | Secret Manager                   |
| KMS                     | KMS                        | Key Vault / Managed HSM         | Cloud KMS                        |
| Private service access  | PrivateLink / VPC endpoint | Private Endpoint                | Private Service Connect          |
| Dedicated connectivity  | Direct Connect             | ExpressRoute                    | Cloud Interconnect               |
| CDN + WAF               | CloudFront + AWS WAF       | Front Door + WAF                | Cloud CDN + Cloud Armor          |
| Monitoring / logs       | CloudWatch                 | Azure Monitor / Log Analytics   | Cloud Monitoring / Cloud Logging |
| Audit trail             | CloudTrail                 | Activity Log                    | Cloud Audit Logs                 |
| IaC (native)            | CloudFormation / CDK       | Bicep / ARM                     | (Terraform; DM deprecated)       |
| Threat detection        | GuardDuty + Security Hub   | Defender for Cloud              | Security Command Center          |

**Where the mapping breaks down — worth stating explicitly:**

- **Networking scope.** A GCP VPC is global with regional subnets; AWS VPCs and Azure VNets are regional and need peering or transit to join. This changes multi-region designs materially.
- **Resource groups.** Azure's resource group is a lifecycle container with no AWS or GCP equivalent; people coming from AWS routinely misuse it as an environment boundary.
- **IAM semantics.** AWS evaluates identity plus resource policies with explicit-deny precedence; GCP is additive inherited bindings with separate deny policies; Azure separates directory roles from resource RBAC. The models are genuinely different, not renamed.
- **Serverless semantics.** Cloud Run handles many concurrent requests per instance, Lambda is one per instance (with concurrency scaling), and Azure Functions varies by plan. "Equivalent" services can require different application designs.
- **Data services.** Cosmos DB is multi-model with five consistency levels; DynamoDB and Firestore are different data models again. Naming similarity hides real design differences.

## Interview tips

- Being able to translate fluently between providers is a genuine hiring signal — practise the top dozen mappings.
- Score points by naming where the mapping _fails_ (global VPC, resource groups, IAM models) rather than reciting the table.
- Expect: "you know AWS, could you work on GCP?" — answer with the primitives that transfer and the specific differences you would need to learn.

---

[⬅ Back to Cloud Engineering](./README.md) · [All topics](../README.md)
