---
title: "What is Cloud Assessment?"
id: 138
category: "Cloud Migration"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-migration
  - interview-questions
---

# What is Cloud Assessment?

**Short answer:** Cloud assessment is the discovery and analysis phase before migration - inventorying applications and infrastructure, mapping dependencies, measuring utilisation, estimating cost, and producing a prioritised migration plan with a strategy per application.

## Detail

**What it must produce**

- **Inventory** - every server, application, database, licence, and integration, with an owner for each.
- **Dependency map** - which systems talk to which, on what ports and protocols. This is the artifact that prevents cutover failures, and it almost always reveals connections nobody documented.
- **Utilisation baseline** - CPU, memory, storage, IOPS, and network over several weeks, including peaks. This drives right-sizing rather than a like-for-like copy of over-provisioned hardware.
- **Current cost baseline** - total cost of ownership including hardware amortisation, licences, facilities, power, and staff time, so the cloud comparison is honest.
- **Constraints** - data residency, compliance obligations, licence portability, latency requirements to systems that are staying, and contractual lock-ins.
- **Migration plan** - a strategy per application, grouped into waves by dependency, with effort estimates and risks.

**How discovery is done.** Agent-based or agentless tooling (AWS Transform - which replaced Application Discovery Service and Migration Hub for new customers in late 2025 - Azure Migrate, Google Migration Center, or third parties like Device42) collects utilisation and network flow data automatically. Flow data is what builds the dependency map - interviews with application owners always miss connections.

**The business case.** Compare current TCO with projected cloud cost including right-sizing, commitments, and the migration project cost itself. Include the operational benefits that are harder to quantify - provisioning speed, DR capability, and reduced hardware refresh risk.

**Limitation.** Discovery tooling only sees what runs during the collection window - a quarterly batch job or a year-end process can be missed entirely, so collect for long enough to cover the business calendar and confirm with owners.

## Example

```text
Assessment record for one application (feeds the wave plan)

app: orders-api                owner: team-orders           criticality: tier 1
servers: 6 VMs (4 app, 2 db)   OS: RHEL 8                   licences: none hardware-bound
utilisation (6-week p95):      app CPU 22%, mem 41%  ->  right-size 8 vCPU -> 4 vCPU
                               db  CPU 35%, IOPS 3.1k peak (month-end)
dependencies (from flow data): payments-gw:443, ldap:636, mainframe-mq:1414 (!)
constraints: mainframe stays on-prem -> needs hybrid link, latency budget < 10 ms
strategy: replatform (RDS PostgreSQL, ALB)   wave: 2 (with payments-gw)
risks: month-end batch not seen in first 2 weeks of data; MQ dependency undocumented
```

## Interview tips

- Network flow analysis for dependency mapping is the technique to name; interviews with owners are insufficient.
- Right-sizing from measured utilisation, not from existing specs, is where the cost case is won or lost.
- Mention licence portability - it derails more migrations than technology does.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
