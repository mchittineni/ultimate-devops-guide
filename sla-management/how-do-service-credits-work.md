---
title: "How do service credits work?"
id: 188
category: "SLA Management"
difficulty: "Intermediate"
tags:
  - devops
  - sla-management
  - interview-questions
---

# How do service credits work?

**Short answer:** A service credit is a percentage of the affected period's fees refunded when measured availability falls below the committed tier — typically 10% for a small miss, rising to 25–100% for severe ones, capped at the monthly fee, and usually claimable only if the customer files within a stated window. They are the standard remedy precisely because they are bounded and predictable.

## Detail

**A typical tier structure:**

| Monthly availability | Credit |
| -------------------- | ------ |
| < 99.9% and ≥ 99.0%  | 10%    |
| < 99.0% and ≥ 95.0%  | 25%    |
| < 95.0%              | 100%   |

**Credits are a cap on liability, not compensation.** A customer whose business lost six figures during your outage receives a percentage of one month's subscription. That asymmetry is intentional and is why credits alone rarely satisfy enterprise buyers, who instead negotiate termination rights after repeated breaches, higher caps, or (rarely) direct damages.

**Claim-based versus automatic.** Most vendors require the customer to file a claim with supporting detail within 30 days; some large providers apply credits automatically. Claim-based schemes mean many breaches are never claimed — engineering should still count them internally, because "no claim" is not "no breach".

**Terms that materially change exposure:** whether credits are the "sole and exclusive remedy" (usual, and important), whether they apply per affected service or to the whole invoice, whether unclaimed credits expire, whether repeated breaches unlock termination for cause, and whether credits are cash or future-service value.

**What engineering owes the process.** Retained, queryable availability data at the contractual granularity; an incident record with accurate UTC start and end times; and the ability to compute per-customer availability when the outage was regional or tenant-specific. Being unable to prove which customers were affected usually means paying everyone.

**Design against credit exposure the honest way.** Reduce blast radius (cells, per-tenant isolation) so an incident affects a fraction of customers; keep announced-maintenance exclusions realistic; and set the internal SLO tighter than the SLA so remediation begins before the contractual line is crossed.

## Example

```text
Incident: 2026-02-11, 03:04–04:22 UTC (78 min), EU region only

Monthly window        : February, 28 days = 40,320 min
Downtime              : 78 min for EU tenants only
EU availability       : 1 - 78/40320 = 99.807%  -> below 99.9%, at or above 99.0%
Credit tier           : 10% of monthly fees for affected EU customers
Affected customers    : 412 of 1,908 (proven from per-region request logs)
Exposure              : 10% x EU MRR, not 10% x total MRR

Unaffected regions: no credit. Being able to prove this saved ~78% of the exposure.
```

## Interview tips

- Name the typical tiers and the "sole and exclusive remedy" clause — it shows commercial literacy.
- The strongest engineering point: per-tenant/per-region measurement limits exposure, so blast-radius reduction has a direct financial return.
- Expect: "was it a breach if nobody claimed?" — yes, and you should track it internally regardless.

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
