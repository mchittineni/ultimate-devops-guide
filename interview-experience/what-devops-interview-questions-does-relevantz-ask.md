---
title: "What DevOps interview questions does RelevantZ ask?"
id: 375
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - relevantz
  - azure-engineering
  - infrastructure-as-code
  - cicd
  - kubernetes
  - backup-and-disaster-recovery
  - cloud-migration
  - cloud-cost-optimization
  - network-security
---

# What DevOps interview questions does RelevantZ ask?

## Questions

**Migration and databases**

- **Have you migrated an on-premises database to the cloud — PostgreSQL or another engine? And do you remember the PostgreSQL port number?**
- **A database sits in a private subnet and you want only specific people to reach it. How do you achieve that?**
- **Do you have any migration experience beyond that?**

**Terraform**

- **You have two environments: one where nothing should be deployed and another whose infrastructure should be deployed via Terraform. What strategy would you use?**
- **You are writing a hundred lines of Terraform and want to avoid that. How do you achieve it?**
- **If several people run Terraform commands at the same time, what problem occurs?**
- **What is Terraform drift?**

**Azure DevOps and Azure services**

- **Which Azure DevOps tools have you used, and where do you store the output of a CI pipeline?**
- **What steps do you create in an Azure pipeline?**
- **How do you store secrets in Azure DevOps?**
- **Have you automated the `.csr` to `.cer` to `.pfx` certificate workflow?**
- **What do you use a Log Analytics workspace for?**
- **What do you use the Azure Recovery Services vault for?**
- **How do you communicate from one Azure subscription to another — what methods are available?**
- **There is data in Azure Data Factory that is not constant but dynamic. How do you get it, analyse it, and present it — possibly through a pipeline?**

**Kubernetes**

- **How do you log into a Pod using `kubectl`?**
- **Give me some Kubernetes commands — how do you troubleshoot with them?**

**Resilience, monitoring, and cost**

- **How do you build a DC/DR setup, and what is the purpose of DR?**
- **How do you take backups, and which strategies have you used?**
- **Which cost optimisation methods have you used to reduce spend?**
- **Have you used any monitoring tools?**

## Example

```text
RelevantZ — DevOps Engineer (5 YOE), reported round
21 questions

  Azure DevOps / Azure        8   pipeline tooling + artefacts, pipeline steps,
                                  secrets, certificate automation, Log
                                  Analytics, Recovery Services vault,
                                  cross-subscription, dynamic ADF data
  Terraform                   4   two environments with different rules,
                                  avoid 100 lines, concurrent runs, drift
  Migration and databases     3   on-prem Postgres to cloud + port number,
                                  private DB for specific people, migrations
  Resilience / cost / monitor 4   DC/DR build and purpose, backup strategies,
                                  cost methods, monitoring tools
  Kubernetes                  2   exec into a Pod, troubleshooting commands

100% AZURE, WITH A POSTGRES PORT CHECK
  The interviewer explicitly asks for the PostgreSQL port number — a small
  factual check to see whether database work was hands-on. It is 5432.
```

## Interview tips

- The PostgreSQL port is **5432**, and the interviewer asks specifically because it is a quick test of whether you actually operated the database. Have the neighbours ready too, since they follow naturally: MySQL and MariaDB on 3306, SQL Server on 1433, MongoDB on 27017, Redis on 6379, Oracle on 1521. For the migration itself, name the method rather than describing it vaguely: Azure Database Migration Service or `pg_dump`/`pg_restore` for an offline move, and logical replication or DMS in continuous mode for near-zero downtime — replicate until the lag is minimal, stop writes briefly, cut over, and keep the source readable for rollback. Say what you validated: row counts, sequence values, and extensions, because a Postgres migration that forgets sequences or extensions breaks after cutover.
- The "avoid writing 100 lines of Terraform" question is really asking whether you know the language's abstractions. Give them in order of leverage: **modules** for reuse across environments, `for_each` and `count` to generate many similar resources from a map instead of repeating blocks, `dynamic` blocks for repeated nested configuration such as security-group rules, `locals` for computed values, variables with sensible defaults, and existing registry modules rather than reinventing common infrastructure. Say the guiding principle — adding a resource should be a data change, not a code change. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- The two-environments question wants a strategy for asymmetric management, which is a genuinely good problem. Say: separate state per environment so they cannot affect each other, separate directories or workspaces, and separate credentials — the pipeline for the protected environment simply has no apply permission, enforced by IAM or Azure RBAC rather than by convention. Add `prevent_destroy` on anything critical there, and if that environment must be visible to Terraform without being managed, read it with `data` sources rather than `resource` blocks — the ownership distinction is the key insight. Say the rule out loud: enforce it with permissions, not with discipline. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- Concurrent Terraform runs and drift are a pair, so answer them together. Concurrency: without locking, two simultaneous applies race and can corrupt state or create duplicate resources — which is why a remote backend takes a lock (a blob lease on Azure Storage, DynamoDB or native locking on S3) so the second run waits or fails fast. Say that locking prevents concurrent _writes_ but not conflicting _intentions_, which is what code review is for, and that `force-unlock` is a break-glass you use only after confirming no apply is running. Drift: the divergence between state and reality caused by out-of-band changes; you detect it with `terraform plan -refresh-only` on a schedule and either import reality, revert it by applying, or `ignore_changes` on fields you do not own.
- The private-database-for-specific-people question should be answered in layers, because a single control is not an answer. Network: the database stays in a private subnet with no public endpoint, reachable only through a private endpoint, and its NSG or firewall rule allows just the application subnet. Access path: Azure Bastion or Just-In-Time access rather than a permanent jump box, so there is no standing route in. Identity: Entra ID authentication to the database so access is by named identity and auditable, with per-user database grants rather than a shared password, and privileged access requiring approval. Audit: diagnostic logs to a Log Analytics workspace. Say that "specific people" is an identity problem as much as a network one. See [zero-trust security](../network-security/what-is-zero-trust-security.md).
- The certificate-automation question is a strong differentiator if you can walk the chain: generate a private key and a `.csr` (certificate signing request), submit it to a CA which returns a `.cer` or `.crt` (the signed public certificate), then bundle the key and the certificate chain into a `.pfx`/PKCS#12 for Windows and Azure services that need both together. Then say what automation looks like: store the certificate as a Key Vault certificate with an integrated issuer so renewal is automatic, reference it from Application Gateway or App Service by its **versionless** secret identifier so a rotated certificate is picked up without redeploying, and alert 30 days before expiry. The versionless-reference detail is why certificates "expire despite being renewed". See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- Cross-subscription communication has several methods and naming the decision criteria matters more than the list: VNet peering (including global peering across regions) for general network connectivity, provided CIDRs do not overlap; Private Link or Private Endpoint to expose a single service without joining networks — which also works with overlapping ranges; a hub-and-spoke topology with a shared hub when several subscriptions are involved; Azure Virtual WAN at larger scale; and, for control-plane rather than network access, granting an identity RBAC across subscriptions via a management group. Say that overlapping address space is the constraint that usually decides it. See [network segmentation](../network-security/what-is-network-segmentation.md).
- Log Analytics and the Recovery Services vault are both "what is this for" questions with precise answers. A Log Analytics workspace is the store and query engine behind Azure Monitor — it ingests platform, resource, and guest logs plus metrics, queried with KQL, and it is what Container Insights, alerts, and workbooks sit on; the operational points are retention tiers, data caps, and that ingestion volume is the cost driver. A Recovery Services vault holds backups and replication for Azure Backup and Site Recovery — VM and file backups with retention policies, and VM replication for failover — so it is your DR and backup control plane, and it is worth adding that soft delete and immutability protect the backups from being deleted by an attacker. See [monitoring in DevOps](../monitoring-and-logging/what-is-monitoring-in-devops.md).
- The DC/DR question should give both halves: the _purpose_ is meeting an RTO and RPO the business has agreed, not "having a second site" — so lead with those numbers. Then the build: paired regions, replication for data with an immutable backup copy, infrastructure as code so the standby can be created or scaled on demand, Traffic Manager or Front Door for traffic redirection, and a documented, _rehearsed_ failover and failback runbook. Say that replication is not backup because deletions replicate, and that an untested plan does not count. See [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md).
- The Azure DevOps block has short exact answers. Pipeline output goes to **pipeline artefacts** (`PublishPipelineArtifact`), with Azure Artifacts for versioned packages and a container registry for images. Secrets: variable groups linked to Key Vault so values resolve at run time, secret variables marked so they are masked, and a service connection using a workload-identity federation rather than a stored service-principal secret. Steps in a pipeline: trigger and branch filters, checkout, restore and build, unit tests with published results, static analysis and scanning, publish the artefact, then stage-gated deployment jobs targeting environments with approval checks.
- For the dynamic-ADF-data question, keep it at the pattern level rather than pretending deep data engineering expertise: a parameterised pipeline with a schedule or event trigger, `Get Metadata` and `ForEach` to handle a varying set of files or partitions, a copy or data-flow activity landing into a lake or warehouse, and Power BI or a Synapse view for presentation — with failure handling and alerting on the pipeline run. Be honest about the boundary between your DevOps ownership and a data engineer's.
- `kubectl exec -it <pod> -- /bin/sh` (or `bash`) is how you get a shell, with `-c <container>` for a multi-container Pod. Add the modern alternative for images with no shell: `kubectl debug -it <pod> --image=busybox --target=<container>` attaches an ephemeral container. For the troubleshooting-commands question, group them by intent — `get`/`describe`/`get events` for state, `logs --previous` for a crashed container, `top` for usage, `auth can-i` for permissions, `rollout status`/`undo` for deployments, `port-forward` to test a Service directly — and say which you reach for first. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- Cost optimisation and backup strategy are both "which have you used" questions, so bring specifics with numbers: reserved instances or savings plans for the steady baseline, spot for interruptible work, right-sizing from observed metrics, auto-shutdown on non-production, storage lifecycle tiering, and cutting log ingestion — plus what you actually saved. For backups, name the 3-2-1 principle updated for cloud, grandfather-father-son retention, and the fact that a restore rehearsal is the only proof a backup works. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
