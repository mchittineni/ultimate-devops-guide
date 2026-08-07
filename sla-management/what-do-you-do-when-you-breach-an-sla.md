---
title: "What do you do when you breach an SLA?"
id: 190
category: "SLA Management"
difficulty: "Intermediate"
tags:
  - devops
  - sla-management
  - interview-questions
---

# What do you do when you breach an SLA?

**Short answer:** Establish the facts precisely (which customers, which window, measured against the contractual definition), notify proactively rather than waiting for a claim, apply the credits the contract requires, deliver a post-incident review with committed remediation, and then treat the underlying cause as prioritised engineering work with a named owner and a date.

## Detail

**Facts first, in contractual terms.** Compute availability exactly as the SLA defines it - the right vantage point, the right sample interval, the right window, per region or tenant. Internal dashboards often use a different definition and will give a different number; presenting a figure you cannot reproduce from contractual measurement is how disputes escalate.

**Notify before the customer notices.** Proactive disclosure with the credit already applied is the difference between a renewal conversation and an escalation to your CEO. It also removes the incentive to argue about measurement: you conceded the breach yourself.

**Separate the commercial response from the engineering response.** Commercially: credits, an account-team conversation, and for repeat breaches often a written improvement plan with milestones the customer can hold you to. Technically: a post-incident review naming contributing factors, and remediation items that are scheduled work rather than aspirations. Customers have learned to distrust "we will improve monitoring".

**Then fix the systemic issue.** A breach means your internal SLO buffer was insufficient, the failure mode was undetected, or the dependency graph is weaker than the promise. Concretely: revisit the SLO buffer, add the missing detection, reduce blast radius so the next occurrence affects fewer tenants, and - if the target genuinely exceeds what the architecture can deliver - say so and renegotiate rather than breaching quarterly.

**Repeat breaches change the contract.** Most enterprise SLAs grant termination for cause after a defined pattern (for example, three breaches in a rolling twelve months). Track your breach history against those clauses; that history, not a single incident, is what determines contractual risk.

**Watch for the perverse incentive.** When a month is already breached, teams sometimes conclude that further downtime is free. Rolling internal windows and per-incident review remove that logic, and it is worth saying out loud that customer trust is not tiered like credits.

## Example

```text
Breach response checklist - run in this order

1. Compute availability per the contract (region, tenant, sample interval, window)
2. Identify affected customers with evidence retained for the full claim window
3. Notify affected customers; state the credit you are applying without being asked
4. Publish incident summary on the status page; attach the post-incident review
5. Apply credits on the next invoice; record the breach against the SLA history
6. File remediation items with owners and dates; review the internal SLO buffer
7. If the target is not architecturally achievable, open the renegotiation conversation
```

## Interview tips

- "Notify proactively and apply the credit before it is claimed" is the answer that shows maturity.
- Naming the termination-for-cause pattern shows you understand the contractual stakes beyond credits.
- Expect: "the month is already breached - does more downtime matter?" Say yes, explain rolling windows, and name the trust cost.

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
