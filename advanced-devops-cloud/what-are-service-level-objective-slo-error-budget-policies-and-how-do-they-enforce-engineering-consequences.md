---
title: "What are Service Level Objective (SLO) Error Budget Policies and how do they enforce engineering consequences?"
id: 703
category: "Advanced DevOps & Cloud"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - sre
  - slo
  - error-budget
  - governance
  - policy
quiz:
  stem: "What is the primary governance mechanism triggered by an SRE Error Budget Policy when a service burns 100% of its monthly error budget?"
  options:
    - "Terminating the lead engineer's contract"
    - "Halting non-critical feature releases and redirecting sprint capacity to reliability fixes, bug remediation, and resilience engineering"
    - "Deleting the service's monitoring dashboard"
    - "Lowering the SLO target so the budget appears green again"
  answer: 2
  explanation: "An Error Budget Policy creates a contractual governor: when the budget is spent, feature releases pause, forcing teams to invest engineering effort into fixing stability issues."
---

# What are Service Level Objective (SLO) Error Budget Policies and how do they enforce engineering consequences?

**Short answer:** An error budget policy is a pre-agreed document - signed off by product, engineering, and SRE leadership - that says what happens when a service spends its error budget: typically slowing or freezing risky releases and redirecting capacity to reliability work until the budget recovers. Its value is that the decision is made calmly in advance, so nobody negotiates reliability during an incident; its weakness is that it only works if leadership actually honours it.

## Detail

**Why it is needed.** An SLO of 99.9% gives a budget of 0.1% failed requests (about 43 minutes of full downtime in 30 days). Without a policy, that budget is a dashboard that gets ignored whenever a deadline looms. The policy turns the number into a decision rule both sides accepted beforehand.

**What a policy contains**

- **Scope** - which services and SLOs it covers, and the window (usually rolling 28 or 30 days).
- **Thresholds and consequences** - graded, not a single cliff:

| Budget state                         | Consequence                                                                                   |
| ------------------------------------ | --------------------------------------------------------------------------------------------- |
| Healthy (well within budget)         | Normal release cadence; the team may spend budget on experiments and faster rollouts          |
| Burning fast (burn-rate alert fired) | Incident response; pause the rollout that is burning it                                       |
| Low (e.g. under 25% remaining)       | Extra review for risky changes; slower canaries; prioritise top reliability fixes             |
| Exhausted                            | Freeze non-essential feature releases; only bug fixes, security patches, and reliability work |

- **Exceptions** - security fixes and legally required changes always ship; who can grant any other exception (usually a named executive) and how it is recorded.
- **Postmortem trigger** - e.g. any single incident consuming more than 20% of the budget gets a postmortem with owned actions.
- **Exit criteria** - the freeze lifts when the budget is back above a threshold, not when someone feels better.
- **Out-of-scope failures** - how to treat budget burned by a dependency or a provider outage (often counted, but with the fix directed at resilience to that dependency).

**Mechanics that make it enforceable:** multi-window burn-rate alerts so teams learn early, a deployment gate or change-management check that reads budget state, and a regular (weekly or monthly) review where product and engineering look at the same number.

**Failure modes:** loosening the SLO to make the budget look green (the SLO should change only in a scheduled review, based on user impact), policies with no executive sponsor, and freezes that are so absolute teams route around them. A good policy is graded and has a legitimate exception path.

## Example

```yaml
# error-budget-policy.yaml - kept in the service repo, reviewed quarterly
service: checkout-api
slo:
  objective: 99.9 # availability, measured at the load balancer
  window: 28d
approvers: [vp-engineering, head-of-product, sre-lead]
thresholds:
  - remaining_below: 25%
    actions:
      - require SRE review for schema changes and infra changes
      - canary duration doubled
  - remaining_below: 0%
    actions:
      - freeze feature releases until remaining > 10%
      - top 3 reliability actions staffed before new feature work
always_allowed: [security-fix, data-loss-fix, legal-requirement]
exception_approver: vp-engineering # recorded in the change ticket
postmortem_required_if_single_incident_burns: 20%
```

## Interview tips

- Say that an error budget without an agreed policy is just a metric; the policy is what converts reliability into engineering priority.
- Describe graded thresholds and an exception path - a single hard freeze with no escape valve gets bypassed.
- Mention burn-rate alerting as the early-warning half of the system and a deploy gate as the enforcement half.
- Name the anti-pattern of relaxing the SLO to escape the freeze, and say SLOs change only in scheduled reviews.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
