---
title: "What is Conway's Law and how does the Reverse Conway Maneuver architect microservices?"
id: 684
category: "DevOps Culture and Practices"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - devops-culture-and-practices
  - culture
  - conways-law
  - architecture
  - microservices
quiz:
  stem: "What is the primary objective of applying the 'Reverse Conway Maneuver' in software engineering organizations?"
  options:
    - "To force all engineers to work in the same physical office room"
    - "To restructure organizational teams into cross-functional domain units so the resulting software architecture naturally reflects decoupled microservices"
    - "To eliminate all version control branches"
    - "To replace human managers with automated algorithms"
  answer: 2
  explanation: "The Reverse Conway Maneuver deliberately shapes team communication boundaries first, knowing that the software architecture will naturally mirror those team structures into decoupled services."
---

# What is Conway's Law and how does the Reverse Conway Maneuver architect microservices?

**Short answer:** Conway's Law states that software architecture inevitably mirrors an organization's communication structures; the Reverse Conway Maneuver reorganizes cross-functional teams to match the desired decoupled microservice architecture first.

## Detail

Formulated by Melvin Conway in his paper "How Do Committees Invent?" (written 1967, published in _Datamation_ in 1968):

> _Organizations which design systems (in the broad sense used here) are constrained to produce designs which are copies of the communication structures of these organizations._

### The Monolith Trap

If you have a centralized DBA team, a centralized Frontend team, and a centralized Backend team:

- You will tend to produce a **tightly coupled layered architecture** whose boundaries follow the teams (UI, services, database) rather than the business domains.
- Every simple feature change requires coordination and meetings across all three siloed departments.

### The Reverse Conway Maneuver

If you desire an architecture of independent, decoupled, loosely connected microservices:

1. **Reorganize the Teams First**: Form small, cross-functional, autonomous 'Two-Pizza Teams' (each containing frontend, backend, database, and DevOps capabilities) around specific business domains.
2. **The Architecture Follows**: Because teams communicate via well-defined business interfaces, the resulting software tends to decouple along those same boundaries into independently deployable services with clean API contracts.

**Trade-offs.** The manoeuvre (named by ThoughtWorks in the mid-2010s) is not free: reorganisations are disruptive, existing code does not move just because the org chart did, and getting domain boundaries wrong now bakes the mistake into both teams and services. It also applies in reverse to decisions you did not intend - a shared "platform database" team will quietly pull every service back towards one schema. Microservices are one possible outcome, not the goal; a modular monolith owned by domain-aligned teams obeys Conway's Law just as well.

## Example

The same product under two org designs:

```text
Functional teams (Conway: layers)          Domain teams (Reverse Conway: services)

  [Frontend team] -> web-ui                  [Checkout team]  -> checkout-ui + checkout-api + orders DB
  [Backend team]  -> monolith-api            [Search team]    -> search-ui  + search-api  + index
  [DBA team]      -> one shared schema       [Accounts team]  -> accounts-api + accounts DB

  "Add a checkout field" = 3 teams,          "Add a checkout field" = 1 team,
  3 backlogs, 1 coordinated release          1 backlog, 1 independent deploy
```

## Interview tips

- Software architecture mirrors human organizational communication.
- Siloed functional teams (DBA, Frontend, Ops) produce monolithic architectures.
- Reverse Conway Maneuver: restructuring teams to force the desired software architecture.
- Cross-functional Two-Pizza teams aligned to domain-driven design.
- Awareness of the cost: reorganising is disruptive, and wrong domain boundaries are expensive to undo.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Culture and Practices](./README.md) · [All topics](../README.md)
