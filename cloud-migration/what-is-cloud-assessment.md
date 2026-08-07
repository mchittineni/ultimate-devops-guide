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

**How discovery is done.** Agent-based or agentless tooling (AWS Application Discovery Service, Azure Migrate, Google's migration centre, or third parties like Device42) collects utilisation and network flow data automatically. Flow data is what builds the dependency map - interviews with application owners always miss connections.

**The business case.** Compare current TCO with projected cloud cost including right-sizing, commitments, and the migration project cost itself. Include the operational benefits that are harder to quantify - provisioning speed, DR capability, and reduced hardware refresh risk.

## Interview tips

- Network flow analysis for dependency mapping is the technique to name; interviews with owners are insufficient.
- Right-sizing from measured utilisation, not from existing specs, is where the cost case is won or lost.
- Mention licence portability - it derails more migrations than technology does.

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
