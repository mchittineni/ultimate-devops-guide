---
title: "What are the pillars of the AWS Well-Architected Framework?"
id: 797
category: "AWS Engineering"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - well-architected
  - architecture
quiz:
  stem: "Under the AWS shared responsibility model for sustainability, which of these is the customer's responsibility?"
  options:
    - "The energy efficiency of AWS data-centre cooling systems"
    - "Rightsizing instances, scaling idle non-production resources to zero, and applying data lifecycle policies"
    - "Choosing renewable energy contracts for AWS regions"
    - "Nothing - the Sustainability pillar is entirely handled by AWS"
  answer: 2
  explanation: "AWS is responsible for sustainability of the cloud (facilities, hardware, power). Customers are responsible for sustainability in the cloud: using only the resources a workload needs, choosing efficient instance types such as Graviton, and deleting or tiering data they no longer need."
---

# What are the pillars of the AWS Well-Architected Framework?

**Short answer:** Six: **Operational Excellence**, **Security**, **Reliability**, **Performance Efficiency**, **Cost Optimization**, and **Sustainability** (added in 2021 to the original five). Each pillar has design principles and a set of review questions, and the framework is applied through **Well-Architected Reviews** - usually in the free Well-Architected Tool - that produce a list of high- and medium-risk issues to fix. The point is not to memorise names but to show you can turn each pillar into concrete controls and make trade-offs between them.

## Detail

### The six pillars, as an engineer would apply them

| Pillar                     | What it asks                                                      | Concrete practices                                                                                                                   |
| -------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Operational Excellence** | Can you run, change and improve the workload safely?              | Everything as code, small reversible deployments, observability, runbooks, blameless post-incident reviews                           |
| **Security**               | Are identities, data and infrastructure protected and monitored?  | Least-privilege IAM and short-lived credentials, encryption, logging and detection (CloudTrail, GuardDuty), incident response drills |
| **Reliability**            | Does it recover from failure and meet demand?                     | Multi-AZ, automatic recovery, backups with tested restores, DR strategy matched to RTO/RPO, service-quota management                 |
| **Performance Efficiency** | Are you using the right resources, and do you keep re-evaluating? | Right instance families, managed and serverless services, caching, load testing, experimenting with new options                      |
| **Cost Optimization**      | Do you pay only for what delivers value?                          | Rightsizing, Savings Plans for the baseline, Spot for interruptible work, cost allocation tags, per-team budgets (FinOps)            |
| **Sustainability**         | Does the workload minimise the resources it consumes?             | Rightsizing, Graviton, scaling idle resources to zero, data lifecycle and deletion, efficient regions and architectures              |

### Sustainability is shared, not "AWS's job"

AWS describes a shared responsibility model here too: AWS owns sustainability **of** the cloud (facilities, hardware, power sourcing), and customers own sustainability **in** the cloud. A workload that runs oversized instances around the clock and keeps every log forever is unsustainable no matter how efficient the data centre is. In practice the sustainability and cost pillars point the same way most of the time.

### How the framework is used

- **Well-Architected Tool**: a free console service where you define a workload, answer the questions pillar by pillar, and get a report of high-risk and medium-risk issues plus an improvement plan. Milestones let you track progress between reviews.
- **Lenses** extend the base framework for a domain - for example Serverless, SaaS, Container Build, and others for analytics, machine learning and generative AI. Organisations can also write **custom lenses** with their own questions.
- **Cadence**: before a major launch, after a significant architecture change, and periodically (for example yearly) for critical workloads.

### The trade-offs are the interesting part

The pillars pull against each other, and interviewers want to hear you weigh them:

- Reliability vs cost: multi-region active-active is resilient and expensive; most services do not need it.
- Security vs operational excellence: tight controls can slow delivery unless they are automated into the pipeline.
- Performance vs cost and sustainability: overprovisioning for peak buys latency headroom and burns money and energy the rest of the time.

The framework does not choose for you; it makes the trade-off explicit and recorded.

## Example

```bash
# The Well-Architected Tool is scriptable: list available lenses and existing reviews
aws wellarchitected list-lenses --query 'LensSummaries[].[LensAlias,LensName]' --output table
aws wellarchitected list-workloads \
  --query 'WorkloadSummaries[].[WorkloadName,RiskCounts.HIGH,RiskCounts.MEDIUM]' --output table
```

```yaml
# Turning review findings into a backlog - one item per pillar, owned and dated
- pillar: reliability
  finding: Backups exist but restores have never been tested
  action: Quarterly automated restore test with AWS Backup restore testing
  risk: high
- pillar: security
  finding: Three services still use static access keys
  action: Move to EKS Pod Identity and delete the keys
  risk: high
- pillar: cost-optimization
  finding: No cost allocation tags; nobody owns spend
  action: Enforce team/service tags with a tag policy; per-team budgets
  risk: medium
- pillar: sustainability
  finding: Non-production runs 24x7
  action: Scale non-prod to zero outside working hours
  risk: medium
```

## Interview tips

- Name all six in one breath, then go one level deeper on each with a concrete practice. Candidates often list the names, describe one pillar twice, and skip Cost Optimization entirely - make sure each pillar gets its own example.
- Correct the misconception that Sustainability is handled by AWS: it is a shared responsibility, and the customer side is rightsizing, Graviton, scaling to zero and data lifecycle.
- Mention the Well-Architected Tool, lenses and that reviews produce high- and medium-risk issues - it shows you have used the framework, not just read about it.
- Talk about trade-offs between pillars; that is usually the follow-up ("which would you sacrifice for a startup MVP?").
- Connect to related topics: [RTO and RPO and DR tiers](../backup-and-disaster-recovery/what-are-rto-and-rpo-and-how-do-they-drive-disaster-recovery-architecture-tiers.md), [cloud cost optimization](../cloud-cost-optimization/what-is-cloud-cost-optimization.md), and [structuring a multi-account AWS organisation](./how-do-you-structure-a-multi-account-aws-organisation.md).

**Telling it as a STAR story** (an adaptable example)

- **Situation:** Before a platform's general-availability launch, leadership asked for a Well-Architected Review because earlier launches had produced surprise bills and untested DR.
- **Task:** Lead the review across all six pillars and turn the findings into a prioritised, owned backlog.
- **Action:** Ran one session per pillar in the Well-Architected Tool with the service teams. Moved manual hotfixes into the pipeline (Operational Excellence), replaced static keys with Pod Identity (Security), scheduled automated restore tests (Reliability), moved a CPU-bound service to compute-optimised Graviton nodes after load testing (Performance Efficiency), added mandatory cost tags, budgets and a Savings Plan for the baseline (Cost Optimization), and scaled non-production to zero at night (Sustainability).
- **Result:** Most high-risk issues were closed before launch, and the first restore test exposed a missing KMS permission that would have broken a real recovery.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core trade-offs between Multi-Cloud, Hybrid-Cloud, and Single-Cloud architectures?]] (`#542`): [What are the core trade-offs between Multi-Cloud, Hybrid-Cloud, and Single-Cloud architectures?](../cloud-platforms/what-are-the-core-trade-offs-between-multi-cloud-hybrid-cloud-and-single-cloud-architectures.md)
- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What are Cloud Availability Zones and how are they engineered for fault independence?]] (`#544`): [What are Cloud Availability Zones and how are they engineered for fault independence?](../cloud-platforms/what-are-cloud-availability-zones-and-how-are-they-engineered-for-fault-independence.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
