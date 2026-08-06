---
title: "What is Cloud Migration?"
id: 136
category: "Cloud Migration"
difficulty: "Beginner"
tags:
  - devops
  - cloud-migration
  - interview-questions
---

# What is Cloud Migration?

**Short answer:** Cloud migration is the process of moving applications, data, and infrastructure from on-premises data centres (or another cloud) to a cloud platform — planned in phases with assessment, strategy selection per application, execution, and optimisation.

## Detail

**Drivers:** data-centre exit or hardware refresh avoidance, elasticity for variable demand, faster provisioning, global reach, access to managed services, and improved disaster recovery. Cost is often cited but is rarely the primary saving unless the migration includes real modernisation.

**The phases**

1. **Assess** — inventory applications and infrastructure, map dependencies, measure utilisation, and estimate current total cost of ownership.
2. **Plan** — choose a strategy per application, sequence the waves (start with low-risk, low-dependency systems), design landing zones, and define success criteria.
3. **Prepare** — build the landing zone: account structure, networking, identity, security guardrails, logging, and IaC foundations.
4. **Migrate** — execute in waves, with a validation and rollback plan for each.
5. **Validate** — functional, performance, and security testing against agreed criteria.
6. **Optimise** — right-size, adopt managed services, apply commitments, and modernise iteratively after the move.

**Common failure modes:** migrating without a dependency map and discovering an undocumented integration at cutover; lifting and shifting everything and then being surprised by the bill; treating the migration as an infrastructure project without application-team involvement; and no plan for the last few systems that resist migration.

**Landing zone first.** Building the security, network, and account foundations before the first workload arrives is what prevents years of remediation later.

## Interview tips

- "Landing zone before workloads" is the piece of sequencing advice that signals real programme experience.
- Dependency discovery is the phase most underestimated — say so.
- Be clear that cost savings come from optimisation _after_ the move, not the move itself.

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
