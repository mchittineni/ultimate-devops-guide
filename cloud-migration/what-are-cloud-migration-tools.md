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

**Short answer:** Discovery tools (AWS Transform, Azure Migrate, Google Migration Center, Device42), server and database replication tools (AWS MGN and DMS, Azure Migrate, GCP Migrate to Virtual Machines), data transfer services (DataSync, Data Box, Storage Transfer Service, physical transfer appliances), and IaC to build the target environment.

## Detail

| Purpose                        | AWS                                                                                     | Azure                           | GCP                                                                      | Third party                              |
| ------------------------------ | --------------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------- |
| Discovery & dependency mapping | AWS Transform (successor to Application Discovery Service and Migration Hub)            | Azure Migrate                   | Migration Center                                                         | Device42, Flexera                        |
| Server migration               | Application Migration Service (MGN)                                                     | Azure Migrate: Server Migration | Migrate to Virtual Machines                                              | Carbonite, Zerto                         |
| Database migration             | DMS (incl. DMS Schema Conversion, successor to the SCT desktop tool)                    | Azure DMS                       | Database Migration Service                                               | Striim, Qlik Replicate                   |
| Bulk data transfer             | DataSync, Data Transfer Terminal (Snowball closed to new customers; Snowmobile retired) | Data Box, AzCopy                | Transfer Appliance, Storage Transfer                                     | Signiant                                 |
| Containers                     | App2Container                                                                           | App Containerization tool       | Migrate to Containers                                                    | Kubernetes-native tooling                |
| Target environment             | CloudFormation, CDK                                                                     | Bicep, ARM                      | Infrastructure Manager (Terraform; Deployment Manager is end-of-support) | Terraform/OpenTofu, Pulumi (multi-cloud) |

**How the replication tools work.** Server migration services install an agent that continuously block-replicates the source machine to the target cloud while it keeps running. You then launch test instances repeatedly for validation, and cut over during a short window with minimal downtime. Database migration services do the same for data: a full load followed by continuous change data capture, so the target stays in sync until you switch.

**Practical points**

- Rehearse the cutover more than once. Test launches are cheap; a failed cutover is not.
- For very large datasets, physical transfer appliances beat the network - calculate transfer time honestly before committing.
- Heterogeneous database migrations (Oracle to PostgreSQL) need schema conversion tooling _plus_ substantial application testing; the tools convert schema and data, not application SQL semantics.
- Use Terraform/OpenTofu for the target environment so what you build during migration is reproducible afterwards.
- **The tool catalogue churns - check it before you plan.** AWS closed Application Discovery Service, Migration Hub, and the Snowball family to new customers in November 2025 in favour of AWS Transform, DataSync, and Data Transfer Terminal; Google's Deployment Manager reached end of support in 2026. A plan built on a tool you cannot onboard to is a plan with a hole in it.

## Example

```bash
# AWS Application Migration Service (MGN): replicate a running server, test, then cut over.
# 1. On the source machine: install the replication agent (block-level, continuous).
sudo python3 aws-replication-installer-init.py --region eu-west-1 --no-prompt

# 2. Launch a non-disruptive test instance from the replicated volumes, as often as needed.
aws mgn start-test --source-server-ids s-1234567890abcdef0

# 3. Cutover window: stop writes at the source, confirm replication lag, launch cutover.
aws mgn describe-source-servers --filters sourceServerIDs=s-1234567890abcdef0 \
  --query 'items[].dataReplicationInfo.lagDuration'
aws mgn start-cutover --source-server-ids s-1234567890abcdef0
aws mgn finalize-cutover --source-server-id s-1234567890abcdef0   # stops replication
```

## Interview tips

- Continuous replication plus a short cutover window is the mechanism to explain.
- "Rehearse the cutover repeatedly" is the practical advice that shows you have done one.
- Note that heterogeneous database migration is an application project, not a tooling exercise.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[How do you prevent and handle secret leaks in CI/CD pipelines?]] (`#237`): [How do you prevent and handle secret leaks in CI/CD pipelines?](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
