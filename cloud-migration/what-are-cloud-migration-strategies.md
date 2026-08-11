---
title: "What are Cloud Migration Strategies?"
id: 137
category: "Cloud Migration"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-migration
  - interview-questions
---

# What are Cloud Migration Strategies?

**Short answer:** The "6 Rs" - rehost, replatform, repurchase, refactor, retire, and retain - chosen per application based on business value, technical fit, effort, and risk.

## Detail

| Strategy       | Also called      | What it means                                                                                     | Effort     | When to choose                                                             |
| -------------- | ---------------- | ------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------- |
| **Rehost**     | Lift and shift   | Move as-is to cloud VMs                                                                           | Low        | Time pressure, data-centre exit deadline, stable legacy apps               |
| **Replatform** | Lift and reshape | Minor optimisations - managed database, managed load balancer - without changing the architecture | Low–medium | Quick wins available with little risk                                      |
| **Repurchase** | Drop and shop    | Replace with SaaS                                                                                 | Low–medium | Commodity function (email, CRM, ticketing)                                 |
| **Refactor**   | Re-architect     | Rebuild cloud-native - microservices, serverless, managed data stores                             | High       | Strategic applications needing scale or velocity                           |
| **Retire**     | -                | Switch it off                                                                                     | Very low   | Typically 10–20% of a portfolio is unused                                  |
| **Retain**     | Revisit          | Leave where it is, for now                                                                        | None       | Regulatory constraints, imminent replacement, or unmigratable dependencies |

**Choosing per application.** Score each on business criticality, change frequency, technical debt, dependencies, compliance constraints, and remaining useful life. High-value, frequently-changed applications justify refactoring; stable back-office systems rarely do.

**A pragmatic sequencing that works:** retire what is unused, repurchase commodities, rehost or replatform the bulk to hit the deadline, then refactor selectively once running in the cloud and generating real telemetry. Attempting to refactor everything during migration is the classic way to miss the date.

**Discovery finding to expect:** a significant fraction of servers in most estates are doing nothing. Retiring them is the cheapest win available.

## Interview tips

- Name all six Rs precisely, and stress that the choice is per application, not per portfolio.
- "Migrate then modernise" versus "modernise then migrate" is a great trade-off to discuss.
- The retire finding - often 10–20% of servers - is a memorable, credible detail.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
