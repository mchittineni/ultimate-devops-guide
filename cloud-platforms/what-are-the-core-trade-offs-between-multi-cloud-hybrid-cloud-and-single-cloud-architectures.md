---
title: "What are the core trade-offs between Multi-Cloud, Hybrid-Cloud, and Single-Cloud architectures?"
id: 542
category: "Cloud Platforms"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cloud
  - architecture
  - multi-cloud
  - hybrid-cloud
quiz:
  stem: "What is the primary hidden architectural and cost challenge when running active-active microservices across multiple cloud providers?"
  options:
    - "Linux containers cannot run on more than one cloud platform"
    - "Substantial inter-cloud network latency and exorbitant cross-cloud data egress transfer costs"
    - "Multi-cloud architectures do not support DNS routing"
    - "Cloud providers automatically cancel subscriptions when detecting competing providers"
  answer: 2
  explanation: "Transferring data across cloud providers incurs high egress fees and substantial public internet latency, making synchronous cross-cloud database replication cost-prohibitive and slow."
---

# What are the core trade-offs between Multi-Cloud, Hybrid-Cloud, and Single-Cloud architectures?

**Short answer:** **Single-cloud** gives the most velocity because you can use the provider's managed services and IAM deeply; the risk is concentration on one provider's availability, pricing, and roadmap. **Multi-cloud** buys negotiating leverage, access to a best-of-breed service, or regulatory/customer-driven redundancy, at the cost of duplicated skills, tooling, and security models, cross-cloud egress, and a drift towards lowest-common-denominator services. **Hybrid** connects on-premises or edge estates to the cloud for data residency, latency, or legacy systems that cannot move, at the cost of network and identity complexity.

## Detail

| Strategy     | Primary benefit                                                       | Primary drawback                                                                 | Typical driver                                              |
| ------------ | --------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Single-cloud | Velocity; deep use of managed services (IAM, DynamoDB, BigQuery, KMS) | Concentration risk on one provider                                               | Most product teams, startups, most enterprises per workload |
| Multi-cloud  | Leverage, specific services, customer or regulatory requirements      | Two of everything: skills, IAM, networking, observability; egress between clouds | Acquisitions, SaaS vendors serving customers on each cloud  |
| Hybrid       | Keep data or systems on-premises while using cloud elasticity         | Private connectivity, overlapping CIDRs, split DNS, identity federation          | Regulated industries, mainframes, factories, edge sites     |

**Distinguish the two kinds of multi-cloud.** Most "multi-cloud" organizations run **different workloads on different clouds** (for example, the data platform on GCP, the ERP on Azure) - manageable, with a shared identity provider, IaC, and observability layer. Running **one workload active-active across clouds** is much harder: synchronous replication across the public internet or interconnects is slow and expensive, and you must abstract away each provider's managed services.

**What makes hybrid work.** Private connectivity (Direct Connect, ExpressRoute, Cloud Interconnect) with redundant links, a non-overlapping IP plan, a DNS strategy that resolves both sides, a single identity provider, and a management plane that reaches both - Azure Arc, Google Distributed Cloud, AWS Outposts, or Kubernetes with GitOps as the common substrate.

**Resilience honesty.** Multi-cloud is rarely the cheapest way to get availability. Multi-AZ and, where justified, multi-region within one provider covers most failure scenarios at a fraction of the complexity. Regulators in some sectors (for example, DORA in EU financial services) require exit plans and concentration-risk analysis, which is a documented, tested exit strategy - not necessarily active-active across providers.

## Example

```text
Decision sketch
1. Is there a hard driver? (customer contract, regulation, acquisition, one irreplaceable service)
   No  -> single-cloud, multi-AZ; multi-region only for workloads whose SLO needs it
   Yes -> continue
2. Can workloads be split by cloud rather than stretched across clouds?
   Yes -> "workload-per-cloud" with shared IdP, IaC, observability, and FinOps
   No  -> active-active across clouds: budget for egress, data consistency, and 2x ops
3. Must data or systems stay on-premises?
   Yes -> hybrid: redundant private links, non-overlapping CIDRs, hybrid DNS, one IdP
```

```hcl
# Portable layer: one IaC tool, one module interface, provider-specific implementations
module "app_aws" {
  source   = "./modules/app/aws"
  image    = var.image
  replicas = 3
}

module "app_gcp" {
  source   = "./modules/app/gcp"
  image    = var.image
  replicas = 3
}
```

## Interview tips

- Ask "what problem is multi-cloud solving here?" - lock-in avoidance alone rarely justifies the cost.
- Separate workload-per-cloud (common, sensible) from a stretched active-active workload (rare, expensive).
- Name egress, identity, and skills duplication as the hidden costs, not just "complexity".
- For hybrid, show you know the plumbing: redundant private links, IP planning, split DNS, single IdP.
- Mention regulatory exit planning (for example, DORA) as a driver that is often met with a tested exit strategy rather than full multi-cloud.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design a production-ready VPC on AWS?]] (`#191`): [How do you design a production-ready VPC on AWS?](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md)
- [[How does AWS IAM evaluate a request?]] (`#192`): [How does AWS IAM evaluate a request?](../aws-engineering/how-does-aws-iam-evaluate-a-request.md)
- [[What is the difference between ECS, EKS, and Fargate?]] (`#193`): [What is the difference between ECS, EKS, and Fargate?](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
