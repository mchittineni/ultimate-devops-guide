---
title: "What are Cloud Migration Tools?"
id: 140
category: "Cloud Migration"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-migration
  - interview-questions
---

# What are Cloud Migration Tools?

**Short answer:** Discovery tools (AWS Application Discovery Service, Azure Migrate, Device42), server and database replication tools (AWS MGN and DMS, Azure Migrate, GCP Migrate to Virtual Machines), data transfer services (DataSync, Snowball, Storage Migration Service), and IaC to build the target environment.

## Detail

| Purpose                        | AWS                                          | Azure                           | GCP                                  | Third party                     |
| ------------------------------ | -------------------------------------------- | ------------------------------- | ------------------------------------ | ------------------------------- |
| Discovery & dependency mapping | Application Discovery Service, Migration Hub | Azure Migrate                   | Migration Center                     | Device42, Flexera               |
| Server migration               | Application Migration Service (MGN)          | Azure Migrate: Server Migration | Migrate to Virtual Machines          | Carbonite, Zerto                |
| Database migration             | DMS + SCT                                    | Azure DMS                       | Database Migration Service           | Striim, Qlik Replicate          |
| Bulk data transfer             | DataSync, Snowball/Snowmobile                | Data Box, AzCopy                | Transfer Appliance, Storage Transfer | Signiant                        |
| Containers                     | App2Container                                | App Containerization tool       | Migrate to Containers                | Kubernetes-native tooling       |
| Target environment             | CloudFormation, CDK                          | Bicep, ARM                      | Deployment Manager                   | Terraform, Pulumi (multi-cloud) |

**How the replication tools work.** Server migration services install an agent that continuously block-replicates the source machine to the target cloud while it keeps running. You then launch test instances repeatedly for validation, and cut over during a short window with minimal downtime. Database migration services do the same for data: a full load followed by continuous change data capture, so the target stays in sync until you switch.

**Practical points**

- Rehearse the cutover more than once. Test launches are cheap; a failed cutover is not.
- For very large datasets, physical transfer appliances beat the network - calculate transfer time honestly before committing.
- Heterogeneous database migrations (Oracle to PostgreSQL) need schema conversion tooling _plus_ substantial application testing; the tools convert schema and data, not application SQL semantics.
- Use Terraform for the target environment so what you build during migration is reproducible afterwards.

## Interview tips

- Continuous replication plus a short cutover window is the mechanism to explain.
- "Rehearse the cutover repeatedly" is the practical advice that shows you have done one.
- Note that heterogeneous database migration is an application project, not a tooling exercise.

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
