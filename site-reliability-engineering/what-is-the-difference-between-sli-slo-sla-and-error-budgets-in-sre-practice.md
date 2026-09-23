---
title: "What is the difference between SLI, SLO, SLA, and Error Budgets in SRE practice?"
id: 641
category: "Site Reliability Engineering (SRE)"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - sre
  - sli
  - slo
  - sla
  - error-budget
quiz:
  stem: "What is the primary operational purpose of an SRE Error Budget?"
  options:
    - "To calculate annual employee salary deductions for outages"
    - "To act as a neutral governor balancing feature velocity against reliability by defining how much unreliability is tolerable"
    - "To bill clients for API requests exceeding rate limits"
    - "To purchase spare physical server hardware"
  answer: 2
  explanation: "An error budget ($100\% - \text{SLO}$) quantifies acceptable failure, allowing product teams to push features aggressively until the budget is burned, at which point focus pivots to stability."
---

# What is the difference between SLI, SLO, SLA, and Error Budgets in SRE practice?

**Short answer:** An SLI is a quantifiable metric of service health; an SLO is an internal target reliability goal agreed upon by engineering and product; an SLA is a legally binding customer contract with financial penalties; an Error Budget is the allowable unreliability ($100\% - \text{SLO}$) used to balance innovation speed with stability.

## Detail

The foundational vocabulary of Google Site Reliability Engineering:

```text
SLI (Indicator)    --> "What is the error rate right now?" (e.g. 99.92% successful requests)
SLO (Objective)    --> "What is our internal target?" (e.g. 99.9% success over 30 days)
Error Budget       --> "How much failure is acceptable?" (100% - 99.9% = 0.1% allowable failures)
SLA (Agreement)    --> "What if we fail customers?" (e.g. < 99.5% triggers a 15% bill credit)
```

### The Error Budget as an Engineering Arbiter

Reliability is not 100%—aiming for 100% reliability is prohibitively expensive and halts feature velocity.

- As long as the Error Budget is positive, product teams ship features rapidly.
- If the Error Budget is exhausted (e.g. burned by outages), feature releases are halted, and engineering focuses on stability, bug fixes, and infrastructure resilience until the budget recovers - as defined in a pre-agreed error budget policy.

**Ordering matters.** The SLO must be stricter than the SLA (for example 99.95% internal against 99.9% contractual), so the internal budget runs out and triggers action well before any money is owed. The limitation: the whole chain is only as good as the SLI - if it is measured in the wrong place (inside the application instead of at the edge) or excludes the wrong traffic, every number above it is precise and wrong.

## Example

```text
Checkout service, 30-day window, 50M requests

SLI           non-5xx responses at the load balancer / all valid requests = 99.93% so far
SLO           99.95%  -> error budget = 0.05% = 25,000 failed requests
Consumed      0.07% observed failure rate = 35,000 failures -> budget overspent (140%)
Consequence   error budget policy: feature freeze, reliability work first
SLA           99.9% contractual  -> not yet breached (credit only below 99.9%)
```

## Interview tips

- SLI = metric; SLO = internal goal; SLA = contractual commitment with financial penalties.
- Error Budget formula: $100\% - \text{SLO}$.
- 100% uptime is the wrong target (diminishing returns, zero innovation).
- Error budget policy halting feature releases when budget is exhausted.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the Difference Between an SLA, an SLO, and an OLA?]] (`#724`): [What is the Difference Between an SLA, an SLO, and an OLA?](../sla-management/what-is-the-difference-between-an-sla-an-slo-and-an-ola.md)
- [[What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?]] (`#675`): [What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?](../incident-management/what-are-incident-severity-levels-sev-1-to-sev-4-and-how-do-they-govern-response-slas-and-war-rooms.md)
- [[What is the Difference Between Request-Based and Window-Based SLIs?]] (`#718`): [What is the Difference Between Request-Based and Window-Based SLIs?](../slo-engineering/what-is-the-difference-between-request-based-and-window-based-slis.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
