---
title: "What is the Difference Between an SLA, an SLO, and an OLA?"
id: 724
category: "SLA Management"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - sla-management
  - sla
  - slo
  - ola
quiz:
  stem: "Why should an organization's internal Service Level Objective (SLO) always be stricter than its customer-facing Service Level Agreement (SLA)?"
  options:
    - "Because internal monitoring tools calculate time zones differently than customer clocks."
    - "To provide an operational safety margin that allows engineering teams to detect and remediate failures before legally binding financial penalties are triggered."
    - "To prevent developers from using version control systems during deployments."
    - "Because cloud providers prohibit aligning SLOs with SLAs."
  answer: 2
  explanation: "If your SLO is 99.9% and your SLA is 99.9%, the moment your internal budget is exhausted you are already incurring contractual liabilities and customer penalties. Stricter SLOs provide a critical buffer."
---

# What is the Difference Between an SLA, an SLO, and an OLA?

**Short answer:** An SLA is a legally binding customer contract with financial penalties for downtime. An SLO is an internal engineering reliability target stricter than the SLA. An OLA (Operational Level Agreement) is an internal contract between internal teams defining dependencies and response times required to meet the SLO.

## Detail

### The Reliability Triad: SLA, SLO, and OLA

Organizations that fail to distinguish between SLAs, SLOs, and OLAs either face frequent contractual penalties or create unachievable expectations between engineering teams.

```text
┌────────────────────────────────────────────────────────┐
│           Customer / Client Facing                     │
│  [SLA] Service Level Agreement                         │
│  - Legally binding contract                            │
│  - Financial remedies & service credits                │
│  - Example: 99.9% Monthly Uptime Guarantee             │
└──────────────────────────┬─────────────────────────────┘
                           │ Enabled by
┌──────────────────────────▼─────────────────────────────┐
│           Internal Engineering Governance              │
│  [SLO] Service Level Objective                         │
│  - Internal engineering target (Stricter than SLA)     │
│  - Drives error budget policy & feature freezes        │
│  - Example: 99.95% Availability Target                 │
└──────────────────────────┬─────────────────────────────┘
                           │ Dependent upon
┌──────────────────────────▼─────────────────────────────┐
│           Inter-Team Organizational Commitments        │
│  [OLA] Operational Level Agreement                     │
│  - Internal commitments between internal teams         │
│  - Defines upstream/downstream dependencies & response │
│  - Example: DBA team guarantees 15-min failover response │
└────────────────────────────────────────────────────────┘
```

### Detailed Breakdown

1. **Service Level Agreement (SLA)**:
   - **Audience**: External customers, enterprise procurement, legal teams.
   - **Nature**: Contractual commitment. Breaches result in financial service credits, contract cancellation rights, or regulatory fines.
   - **Target Safety Margin**: Always looser than internal SLOs (e.g., 99.9% SLA backed by a 99.95% internal SLO) to provide an engineering buffer before financial penalties occur.
2. **Service Level Objective (SLO)**:
   - **Audience**: SRE, software engineers, product managers.
   - **Nature**: Measurable target for SLIs over a rolling window (typically 30 days). Governs error budgets and release velocity.
3. **Operational Level Agreement (OLA)**:
   - **Audience**: Internal engineering silos (e.g., Platform Team, Network Ops, Database Ops, SecOps).
   - **Nature**: Internal commitments supporting the customer-facing service. For example, if the Application Team must meet a 99.95% SLO, the Infrastructure Team might have an OLA guaranteeing 99.99% compute and network availability.

**Trade-off.** OLAs add accountability but also bureaucracy: written like contracts, they encourage teams to argue about whose number was missed. They work best as lightweight internal SLOs for platform and shared services, reviewed together with the consuming teams.

### Real-World Production Scenario

A payments platform commits to an enterprise customer SLA of 99.9% uptime (allowing 43.8 minutes of downtime per month) with a 10% invoice credit if breached. Internally, the engineering team tracks an SLO of 99.95% (allowing only 21.9 minutes of downtime). To maintain this, the database team commits to an OLA guaranteeing automatic Multi-AZ failover within 120 seconds of hardware failure.

## Example

```yaml
# The three layers written down for one service
sla:            # customer contract
  objective: 99.9        # monthly uptime
  remedy: 10% credit below 99.9%, 25% below 99.0%
slo:            # internal target, stricter than the SLA
  objective: 99.95       # rolling 30 days
  policy: error-budget-policy.yaml
olas:           # what supporting teams commit to
  - team: database-platform
    commitment: automatic Multi-AZ failover within 120 s; page response within 15 min
  - team: network
    commitment: 99.99% availability of the regional load balancers
```

## Interview tips

- Highlight the vital importance of the safety buffer: never set your external SLA equal to your internal SLO, as doing so leaves zero room for error before financial penalties hit.
- Explain that OLAs prevent finger-pointing between internal teams during post-mortems by establishing clear expectations across internal dependencies.
- Discuss service credits as the standard contractual remedy for SLA breaches.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
