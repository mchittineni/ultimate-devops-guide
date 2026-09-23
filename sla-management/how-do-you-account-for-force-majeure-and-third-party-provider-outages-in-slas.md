---
title: "How Do You Account for Force Majeure and Third-Party Provider Outages in SLAs?"
id: 726
category: "SLA Management"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - sla-management
  - force-majeure
  - third-party-risk
quiz:
  stem: "Why are standard cloud provider regional outages (e.g., AWS us-east-1 failing) typically NOT eligible for Force Majeure relief in enterprise contracts?"
  options:
    - "Because cloud providers do not use physical data centers."
    - "Because regional cloud outages are foreseeable operational risks that can be mitigated through multi-region or resilient architectural design."
    - "Because Force Majeure only applies to open-source software licenses."
    - "Because cloud contracts require judicial approval before any outage occurs."
  answer: 2
  explanation: "Force Majeure applies only to unforeseeable, unavoidable events like natural catastrophes or war. Cloud infrastructure disruptions are foreseeable operational risks that enterprises expect vendors to engineer around."
---

# How Do You Account for Force Majeure and Third-Party Provider Outages in SLAs?

**Short answer:** SLA contracts account for external risks through explicit exclusion clauses covering force majeure events (natural disasters, war, major internet infrastructure blackouts) and upstream third-party dependencies, supported by multi-vendor redundancy or customer pass-through terms.

## Detail

### The Reality of External Dependencies

Modern platforms rely heavily on external SaaS, PaaS, and IaaS components: AWS/GCP for hosting, Cloudflare for CDN/DDoS, Twilio for SMS, and Stripe for payments. When an upstream provider suffers an outage, downstream platforms often fail as well.

Engineering and legal teams must clearly define how upstream outages impact customer SLA commitments.

### Contractual Handling of External Failures

#### 1. The Pass-Through SLA Model

- The downstream vendor's SLA commitment is pegged directly to the upstream cloud provider's SLA.
- If AWS is down, the contract explicitly states that unavailability caused by upstream cloud infrastructure providers is excluded from customer penalty calculations.
- **Customer Reception**: Common in small or lower-tier contracts, but resisted by enterprise clients who expect the vendor to architect for resilience.

#### 2. The Resilient Architecture Model (No Exclusion)

- Enterprise clients reject third-party excuses: 'We pay you to deliver a service; your architecture choices are your responsibility.'
- The vendor accepts financial responsibility for third-party failures and designs multi-region active-active architectures or multi-vendor failover patterns to isolate against single-provider failures.

### Force Majeure Clauses

A standard legal provision excusing both parties from contractual liability if an extraordinary event beyond reasonable human control occurs.

- **Qualifying Events**: Acts of God (earthquakes, floods, hurricanes), acts of war, terrorism, government sanctions, or total nationwide telecommunications failures.
- **What Is Usually NOT Force Majeure**: Standard fiber cuts, routine cloud regional outages, DDoS attacks, or staff shortages. Customers argue - and many contracts now say explicitly - that these are foreseeable operational risks the vendor must protect against.

The exact outcome depends on the wording of the clause and the governing law, so engineering's job is to give legal an accurate picture of which risks are actually mitigated (multi-region, DDoS protection, second provider) before the list of exclusions is negotiated. Most force majeure clauses also require the vendor to have followed its own business-continuity obligations and to notify promptly - an unexercised DR plan weakens the claim.

```text
[Outage Event]
       │
       ├── Is it an Act of God / War / regional grid failure?
       │     └──► YES: Force Majeure claimed (relief if the clause and precautions hold)
       │
       ├── Is it an AWS / Cloud Regional Failure?
       │     ├── Vendor Contract Excludes Third-Party? ──► YES: Excluded
       │     └── No Exclusion (Enterprise Contract)   ──► NO : SLA Breach & Credits Owed
```

### Real-World Production Scenario

A major hurricane floods a coastal metropolitan area, cutting power and terrestrial fibre across the region and prompting a state of emergency. A SaaS company's single data center loses all connectivity for 12 hours. The contract's force majeure clause names natural disasters, so the company claims relief from service credits - but an enterprise customer disputes it, pointing out that the company's own security questionnaire promised a secondary region it had never built. Force majeure relief is strongest when the vendor can show the event overwhelmed reasonable precautions, not replaced them.

## Example

```text
Contract clause pattern that engineering can actually support

Exclusions from Unavailability:
  (a) Force majeure events as defined in section 14, provided Provider has
      maintained the disaster-recovery capabilities described in Schedule C
      and notified Customer within 24 hours.
  (b) Failures of Customer's own systems, networks, or configuration.
NOT excluded:
  - Outages of Provider's hosting, CDN, DNS, or payment sub-processors.
  - Loss of a single cloud region (Provider operates active-passive in two regions).
  - Volumetric DDoS attacks (mitigated by Provider's DDoS protection service).
```

## Interview tips

- Distinguish between standard cloud regional failures (which are foreseeable engineering challenges) and genuine Force Majeure events (acts of God/war).
- Explain the commercial negotiation: large enterprise customers almost never allow vendors to pass off AWS or GCP downtime as an excused outage.
- Mention architectural mitigations like multi-region deployments and graceful degradation when upstream SaaS providers fail.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[How do you prevent and handle secret leaks in CI/CD pipelines?]] (`#237`): [How do you prevent and handle secret leaks in CI/CD pipelines?](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md)
- [[What is Pipeline as Code and how do modern CI systems validate and isolate pipeline runs?]] (`#532`): [What is Pipeline as Code and how do modern CI systems validate and isolate pipeline runs?](../cicd/what-is-pipeline-as-code-and-how-do-modern-ci-systems-validate-and-isolate-pipeline-runs.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
