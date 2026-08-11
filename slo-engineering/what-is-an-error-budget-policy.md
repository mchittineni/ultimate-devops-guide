---
title: "What is an error budget policy?"
id: 180
category: "SLO Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - slo-engineering
  - interview-questions
---

# What is an error budget policy?

**Short answer:** The error budget policy is the written, pre-agreed answer to "what changes when the budget runs out?" It names the thresholds, the actions at each threshold, who has authority to enforce them, and the escape hatch. Without it, an error budget is a dashboard nobody acts on.

## Detail

**Why it must be written in advance.** Once an outage has happened and a launch date is at risk, nobody negotiates a freeze objectively. The policy is signed off by engineering, product, and the business while everyone is calm, so that enforcement later is administrative rather than political.

**What it contains:**

- The SLO and window it applies to, and the SLI definition.
- Thresholds and consequences - for example: below 50% budget remaining, no risky migrations; below 25%, extended canary periods and a reliability item in every sprint; exhausted, feature work stops until the budget recovers or a defined amount of reliability work ships.
- Who decides and who can override - typically the service owner enforces, and an override needs a named executive plus a recorded reason and expiry.
- Exemptions - security patches and compliance work are usually allowed to ship during a freeze; document it rather than arguing about it mid-incident.
- What counts as budget-consuming: whether planned maintenance, load tests in production, and dependency failures outside your control are excluded - decide this up front, since it is the most common dispute.

**"Freeze" needs a definition.** A total halt is rarely what anyone wants. Useful policies define the freeze as "no new feature flags enabled, no schema migrations, no infrastructure changes outside the reliability backlog" - specific enough that people know whether their change is permitted.

**Recovery must be defined too.** Rolling windows recover automatically as bad days age out; calendar windows reset abruptly on the first of the month, which can create perverse behaviour late in a bad month. State which model you use, and prefer rolling windows for exactly that reason.

**The policy has failed if it is never triggered.** Perpetually healthy budgets mean the target is too loose. Perpetual exhaustion with no behaviour change means the policy has no teeth - either way, review it quarterly with the SLO.

## Example

```yaml
# error-budget-policy.yaml - lives in the service repository, reviewed quarterly
service: checkout
slo: 99.9% availability over a rolling 30 days
sli: successful (non-5xx) HTTP requests / total requests, measured at the edge
thresholds:
  - remaining: "> 50%"
    actions: ["normal velocity", "experiments permitted"]
  - remaining: "25-50%"
    actions: ["canary duration doubled", "no schema migrations"]
  - remaining: "< 25%"
    actions: ["one reliability item per sprint", "change advisory for risky work"]
  - remaining: "0%"
    actions: ["feature freeze", "reliability work prioritised until 25% recovered"]
exemptions: ["security patches", "regulatory deadlines", "incident remediation"]
excluded_from_budget: ["announced maintenance windows"]
enforced_by: service owner
override: VP Engineering, recorded in the incident channel with an expiry date
```

## Interview tips

- The sentence that lands: "an error budget without a policy is just a chart."
- Name the override path - a policy with no escape hatch gets ignored the first time it is inconvenient.
- Expect the exclusions question: planned maintenance, third-party outages, and load tests are the classic three.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
