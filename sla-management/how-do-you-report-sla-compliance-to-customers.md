---
title: "How do you report SLA compliance to customers?"
id: 189
category: "SLA Management"
difficulty: "Intermediate"
tags:
  - devops
  - sla-management
  - interview-questions
---

# How do you report SLA compliance to customers?

**Short answer:** Publish availability from the same measurement the contract defines, automatically and on a schedule: a live status page driven by monitoring rather than by hand, a monthly compliance figure per service and region, and an incident history with timestamps and post-incident summaries. Manual reporting is slow, disputed, and - during an incident - always late.

## Detail

**Automate the status page.** During an outage, the page is edited by the people who are busiest. Drive component status from the same probes that compute the SLI, with a human-authored narrative on top, and host it off your primary infrastructure (a different provider, static hosting) so it survives your own failure. A status page hosted in the region that just failed is the classic mistake.

**Report at the granularity the contract promises.** If the SLA is per region or per plan tier, a single global number is not evidence of compliance - and it usually flatters you, hiding a regional outage in global traffic. Per-tenant reporting is stronger still and turns disputes into arithmetic.

**Distinguish availability from incident communication.** Customers need both a number (monthly percentage, trend, credits applied) and a narrative (what happened, when, what changed as a result). Enterprise customers will ask for the post-incident review; decide in advance what you share - timeline, impact, and remediation, without internal names or security-sensitive detail.

**Set the update cadence during incidents and keep it.** Commit to an interval (for example, every 30 minutes) and post on it even when there is nothing new; silence is read as loss of control. State impact in customer terms ("card payments failing for EU merchants") rather than internal terms ("the payments StatefulSet is degraded").

**Handle disputes with data, not argument.** A customer's own monitoring will sometimes disagree with yours - their client-side measurement includes their network and their retries. Keep raw per-minute data for the full claim window, be able to reproduce the calculation, and where their evidence is credible, accept it. A vendor that always wins measurement disputes loses renewals.

## Example

```text
Monthly SLA report - Checkout API - February 2026

Region      Availability   Commitment   Status      Downtime   Credits
eu-west-1   99.807%        99.9%        BREACH      78 min     10% (EU tenants)
us-east-1   99.996%        99.9%        Met          1.6 min   —
ap-south-1  100.000%       99.9%        Met          0 min     —

Incidents
  2026-02-11 03:04-04:22 UTC  EU  Database failover exceeded connection timeout
                                  Post-incident review: PIR-2026-014 (attached)
Measurement: 1-min synthetic probes, external vantage points, edge-terminated
Excluded: 2026-02-02 01:00-02:00 UTC announced maintenance (notified 2026-01-24)
```

## Interview tips

- "Host the status page off your own infrastructure" is a small point that consistently impresses.
- Emphasise reporting at contractual granularity - global averages hiding regional outages is the trap.
- Expect: "the customer's numbers disagree with yours" - explain vantage points, keep raw data, and concede when their evidence is sound.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
