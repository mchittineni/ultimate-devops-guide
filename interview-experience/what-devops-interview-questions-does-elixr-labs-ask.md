---
title: "What DevOps interview questions does Elixr Labs ask?"
id: 330
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - elixr-labs
  - azure-engineering
  - cloud-migration
  - cloud-cost-optimization
  - backup-and-disaster-recovery
  - monitoring-and-logging
  - network-security
  - serverless-architecture
---

# What DevOps interview questions does Elixr Labs ask?

## Questions

**Migration**

- **What is landing-zone work in a migration project?**
- **Have you done a migration — on-premises to Azure, or Azure to Azure? Was it a resource migration or a data migration?**
- **What pre-checks do you carry out before a migration?**

**Azure architecture and connectivity**

- **Which core Azure services would you consider for a new workload?**
- **Explain the hub-and-spoke network topology.**
- **Pick one requirement you delivered and walk me through the end-to-end Azure deployment.**
- **Take a three-tier .NET application where the web API runs on App Service, background jobs on Function Apps, and messaging goes through Service Bus. How is connectivity between all of those configured?**
- **How does an on-premises user reach an application or code deployed in a cloud service — how is that connectivity configured?**
- **As an Azure specialist, what is your recommendation — site-to-site VPN or ExpressRoute?**
- **Take a banking customer with a limited budget. You recommended site-to-site VPN for low budget, but you also said ExpressRoute is more secure. How do you justify that trade-off to a customer who has a hard budget limit?**
- **In which specific scenarios do you choose site-to-site VPN, and in which ExpressRoute?**
- **Is your deployment model IaaS or SaaS?**

**Storage and cost optimisation**

- **Which storage components have you worked with?**
- **A storage account holds a large and continuously growing dataset — for example a camera recording 24/7 — and end users still need to retrieve data from it. What cost-optimisation techniques would you apply to that storage account?**
- **If a storage account was created in the hot tier, can it be changed to the cool tier?**
- **You can change hot to cool manually, but with a very large volume of data that takes time. How do you deal with that?**

**Backup and disaster recovery**

- **Have you hit any problems while taking backups? What issues?**
- **Which backup services have you used — Azure-native or on-premises tooling?**
- **Which disaster recovery scenarios have you configured?**

**Monitoring and alerting**

- **What monitoring techniques and alerts do you set up?**
- **Production infrastructure runs on Azure and the customer has given you threshold values, but across a large estate you are receiving hundreds of alerts. How do you triage and prioritise which alerts matter?**
- **Describe a known issue you hit — during a pipeline integration or a production code push — that was critical, and how you resolved it.**

**Ways of working**

- **What does your day-to-day work look like — is it support or project delivery?**
- **Which pipelines do you handle — QA, UAT?**
- **How many people are on your team?**

## Example

```text
Elixr Labs — DevOps Engineer (6 YOE), reported round
25 questions — 100% Azure

  Azure architecture / network 9   hub-and-spoke, 3-tier .NET connectivity,
                                   on-prem to cloud, VPN vs ExpressRoute
                                   (asked 3 ways), IaaS vs SaaS
  Storage and cost             4   storage components, 24/7 growing dataset,
                                   hot->cool tier change, doing it at scale
  Migration                    3   landing zone, migration you ran, pre-checks
  Backup and DR                3   backup problems, backup services, DR scenarios
  Monitoring / alerting        3   techniques, alert-fatigue triage, critical issue
  Ways of working              3   support vs project, QA/UAT pipelines, team size

THE INTERVIEWER'S TECHNIQUE
  They press the same decision three times — VPN vs ExpressRoute in general,
  then under a banking budget constraint, then "in which scenario each".
  They are testing whether you can defend a recommendation under pressure
  and change it when a constraint changes. Do not flip-flop; state the
  deciding variable.
```

## Interview tips

- The VPN-versus-ExpressRoute sequence is the core of this interview and the trap is treating "cheaper" and "more secure" as a contradiction you must resolve. Reframe it: ExpressRoute is a private circuit that never traverses the public internet and gives predictable bandwidth and latency with an SLA; a site-to-site VPN is IPsec-encrypted but rides the public internet, so the traffic is confidential yet the _path_ is neither private nor predictable. Encryption and network isolation are different properties — say that sentence and the apparent contradiction dissolves.
- Then answer the banking-budget version as a risk conversation rather than a technical one: establish what the regulator and the data classification actually require, because if a private circuit is mandated then it is not a budget question; if it is not mandated, a VPN with strong crypto plus monitoring is a defensible interim, and you can plan ExpressRoute with a VPN as failover later. Offering a staged path is what a consultant is expected to do.
- For the scenario split, be concrete: VPN for low bandwidth, non-critical or temporary connectivity, proofs of concept, and branch offices; ExpressRoute for sustained high throughput, latency-sensitive workloads, regulated data, and anything needing a bandwidth SLA. See [connecting an on-premises network to the cloud](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md).
- The hot-to-cool tier questions have a precise factual answer that many candidates get wrong. The _account_-level default access tier can be switched at any time, and individual blobs can be moved between tiers — but the practical answer to "it takes time with huge data" is that you do not do it manually at all: you apply a lifecycle management policy that transitions blobs to cool or archive automatically after N days since last modification or last access. Naming lifecycle policies is the expected answer. Add the two costs that catch people out — early-deletion charges on cool and archive, and rehydration latency and cost when reading from archive.
- For the 24/7 camera-data question, build the full answer around access pattern: lifecycle tiering by age, archive for anything beyond the retention window with a documented rehydration path, a retention policy that actually deletes, compression before upload, locally-redundant rather than geo-redundant storage where the data is reproducible, and a CDN or cache in front of the small hot subset users actually request. Say that you would measure the read pattern first, because if users routinely fetch old footage then archive is the wrong answer. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).
- The alert-fatigue question is really about alerting philosophy. Say that hundreds of alerts means the thresholds are measuring causes rather than symptoms, and give the fix: alert on user-facing symptoms and SLO burn rate, use severity tiers where only customer-impacting issues page and the rest become tickets or dashboards, group and deduplicate related alerts, add action groups with suppression during known maintenance, and delete any alert nobody has ever acted on. The line that lands is "every page must be actionable, or people stop reading them". See [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md) and [error budgets](../site-reliability-engineering/what-is-error-budget.md).
- For the three-tier .NET connectivity question, answer with private networking and managed identity rather than connection strings: VNet integration for App Service and Function Apps, private endpoints for Service Bus and the database, private DNS zones so the names resolve internally, and managed identities so no secret is stored anywhere. That combination is what an Azure specialist is expected to name. See [defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md).
- "Landing job activity" is a transcription of landing-zone work. Define it properly: the foundational subscription and management-group structure, networking topology, identity, policy, and governance baseline you establish _before_ workloads land, so every migrated application inherits the same guardrails. See [what a cloud landing zone is](../cloud-engineering/what-is-a-cloud-landing-zone.md).
- Migration pre-checks should be a real checklist rather than a sentiment: application and dependency discovery, whether the workload is supported on the target, right-sizing from observed usage rather than current spec, network and bandwidth planning for the data transfer, licensing implications, a data-sync and cutover plan with a rollback, a tested backup taken before you start, and a defined success criterion. See [connecting an on-premises network to the cloud](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md).
- Hub-and-spoke deserves the _why_ as well as the shape: shared services — firewall, gateways, DNS, jump hosts — live once in the hub, spokes peer to it for isolation per workload or environment, and transit between spokes goes through the hub where it can be inspected. Mention that spoke-to-spoke peering does not transit by default, which is why the hub needs a firewall or route server. See [network segmentation](../network-security/what-is-network-segmentation.md).
- The DR question in an Azure context should name mechanisms, not just RTO and RPO: Site Recovery for VM replication and failover, geo-redundant or read-access geo-redundant storage, paired-region deployment, and Traffic Manager or Front Door to redirect traffic. Say whether you have actually failed over or only tested a plan on paper — honesty here reads better than an overstated claim. See [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
