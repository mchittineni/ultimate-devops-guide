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

**Short answer:** The "6 Rs" - rehost, replatform, repurchase, refactor, retire, and retain - chosen per application based on business value, technical fit, effort, and risk. AWS now publishes a seventh, **relocate** (moving a hypervisor estate as-is, e.g. VMware to a cloud-hosted VMware service), which is why you will also hear "the 7 Rs".

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

**Trade-off to state.** Rehost is fast but carries the on-premises design (and its cost profile) into the cloud; refactor unlocks the cloud's benefits but is slow and risky if done under a data-centre deadline. The choice is really about where you want to spend effort - before the move or after it.

## Example

```text
Portfolio triage (excerpt) - one row per application, decided in a wave-planning workshop

app              criticality  change freq  tech debt  constraint           strategy     wave
---------------  -----------  -----------  ---------  -------------------  -----------  ----
payroll-legacy   medium       yearly       high       vendor EOL 2027      repurchase   -
intranet-wiki    low          never        medium     none                 retire       -
orders-api       high         daily        medium     none                 replatform   2   (RDS, ALB)
checkout         high         daily        high       peak-season freeze   refactor     4   (after move)
mainframe-batch  high         monthly      high       data residency       retain       -
file-shares      medium       n/a          low        none                 rehost       1
```

## Interview tips

- Name all six Rs precisely, and stress that the choice is per application, not per portfolio.
- "Migrate then modernise" versus "modernise then migrate" is a great trade-off to discuss.
- The retire finding - often 10–20% of servers - is a memorable, credible detail.
- Mention relocate as the seventh R so the answer matches current AWS guidance.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
