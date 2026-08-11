---
title: "What is Business Continuity Planning?"
id: 64
category: "Backup and Disaster Recovery"
difficulty: "Intermediate"
tags:
  - devops
  - backup-and-disaster-recovery
  - interview-questions
---

# What is Business Continuity Planning?

**Short answer:** Business continuity planning is the organisation-wide discipline of keeping critical business functions running through a disruption - of which IT disaster recovery is one part alongside people, facilities, suppliers, and communications.

## Detail

**BCP vs DR.** DR is the technical restoration of systems. BCP is broader: how the business keeps operating - including manual workarounds, alternative premises, supplier substitution, and customer communication - while systems are being restored.

**The process**

1. **Business Impact Analysis (BIA)** - identify critical functions, their dependencies, and the financial and regulatory cost of downtime over time. This produces the RTO/RPO targets that DR then implements.
2. **Risk assessment** - likelihood and impact of threats: outage, cyber attack, supplier failure, natural disaster, key-person loss.
3. **Strategy** - for each critical function, define continuity options and the resources required.
4. **Plan documentation** - activation criteria, roles and authority (who declares an incident), contact trees, step-by-step procedures, and communication templates for customers, regulators, and staff.
5. **Testing** - tabletop walkthroughs, functional drills, and full simulations. This is where plans meet reality.
6. **Maintenance** - review after every incident, test, and significant change.

**Where plans typically fail:** the contact list is out of date, the plan is stored only in the system that is down, nobody is authorised to declare the disaster out of hours, or the third-party dependency nobody mapped turns out to be critical.

For a DevOps engineer, the practical contributions are: keeping the dependency map current, maintaining DR automation as code, ensuring runbooks are accessible offline, and pushing for real failover tests rather than paper exercises.

## Interview tips

- Position BCP as containing DR, not the reverse - the distinction is often tested.
- Name the BIA as the source of RTO/RPO targets.
- The best practical point: store the plan and credentials somewhere that survives the outage the plan is for.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
