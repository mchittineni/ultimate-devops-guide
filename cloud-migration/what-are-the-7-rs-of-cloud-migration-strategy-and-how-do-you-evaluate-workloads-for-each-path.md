---
title: "What are the 7 Rs of Cloud Migration strategy and how do you evaluate workloads for each path?"
id: 692
category: "Cloud Migration"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - cloud-migration
  - 7-rs
  - strategy
  - architecture
quiz:
  stem: "Which cloud migration strategy involves moving an on-premise MySQL database onto Amazon RDS without rewriting the core application code?"
  options:
    - "Rehost"
    - "Replatform"
    - "Retire"
    - "Repurchase"
  answer: 2
  explanation: "Replatforming swaps unmanaged infrastructure components for managed cloud services (like self-hosted MySQL to AWS RDS) without altering core application business logic."
---

# What are the 7 Rs of Cloud Migration strategy and how do you evaluate workloads for each path?

**Short answer:** The 7 Rs framework (Rehost, Replatform, Refactor, Repurchase, Retain, Retire, Relocate) categorizes the architectural strategy for migrating applications from on-premise data centers to the cloud based on business value, risk, and timeline.

## Detail

Gartner described five Rs in 2010; AWS extended the list to six and later seven by adding **relocate**. The value of the framework is that it forces a decision **per application**, not a single strategy for the whole estate.

### The seven strategies

1. **Rehost ("lift and shift")**: move VMs to cloud IaaS unchanged, typically with block-level replication (AWS MGN, Azure Migrate). Fastest way out of a data centre; carries the on-premises design and sizing with it.
2. **Replatform ("lift, tinker, and shift")**: swap self-managed components for managed services without changing core code - self-hosted MySQL to RDS, a WebLogic app into containers, cron VMs to managed schedulers.
3. **Refactor / re-architect**: redesign the application for cloud-native patterns - containers, serverless, managed data stores, event-driven integration. The highest long-term benefit for strategic systems, and the most time, cost, and risk.
4. **Repurchase ("drop and shop")**: replace custom or licensed software with SaaS - a home-grown CRM to Salesforce, on-prem Exchange to Microsoft 365.
5. **Relocate**: move a hypervisor estate as-is to a cloud-hosted equivalent (VMware workloads to a cloud VMware service) without changing guest OSes or IPs - fast for large VMware estates, but consider licensing changes under Broadcom's VMware pricing before relying on it.
6. **Retain ("revisit")**: keep it where it is for now - regulatory or residency constraints, recently purchased hardware, unmigratable dependencies, or an imminent replacement.
7. **Retire**: switch off what nobody uses. Discovery routinely finds a noticeable share of servers (often quoted as 10-20%) that can simply be decommissioned - the cheapest "migration" of all.

### How to evaluate a workload

Score each application on a few dimensions and let the pattern pick the R:

| Signal                                                                      | Points toward                              |
| --------------------------------------------------------------------------- | ------------------------------------------ |
| Hard exit deadline, stable app, little change                               | Rehost or relocate                         |
| Self-managed database or middleware with a managed equivalent               | Replatform                                 |
| High business value and frequent change, scaling or velocity pain           | Refactor (often _after_ an initial rehost) |
| Commodity function (email, HR, ticketing)                                   | Repurchase                                 |
| Compliance/residency blocker, hardware-bound licence, end of life in months | Retain or retire                           |
| No users, no traffic, no owner                                              | Retire                                     |

**Trade-off to name.** Faster strategies (rehost, relocate) move the problem rather than solve it - costs and operational toil come along - while slower ones (refactor) can blow the migration timeline. Most programmes rehost or replatform the bulk to meet the deadline, then refactor selectively with real cloud telemetry.

## Example

```text
Wave plan excerpt: strategy decided per application, not per portfolio

app               signal                                      strategy     wave
----------------  ------------------------------------------  -----------  ----
hr-portal         commodity, vendor offers SaaS               repurchase   -
reports-legacy    0 logins in 180 days                         retire       -
vmware-cluster-3  300 VMs, DC lease ends in 9 months           relocate     1
orders-db         self-managed MySQL 8, 2 TB                  replatform   2   (RDS)
checkout          tier 1, daily deploys, scaling pain         refactor     4   (after rehost in 2)
core-ledger       data residency, mainframe                   retain       -
```

## Interview tips

- List all seven, and say relocate is the one AWS added most recently.
- Stress that the decision is per application and driven by business value, change frequency, constraints, and deadline.
- Contrast rehost (fast, carries the old cost profile) with refactor (slow, highest long-term value), and describe "rehost now, refactor later" as the usual sequencing.
- Mention retire as the cheapest win discovered during assessment.
- Tie it to evidence: discovery and utilisation data, not opinions, should drive the classification.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
