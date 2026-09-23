---
title: "What is Post-Mortem Analysis?"
id: 123
category: "Incident Management"
difficulty: "Intermediate"
tags:
  - devops
  - incident-management
  - interview-questions
---

# What is Post-Mortem Analysis?

**Short answer:** A post-mortem is a written, blameless analysis after an incident that establishes the timeline, identifies contributing factors, and produces owned, tracked actions to make recurrence less likely or less severe.

## Detail

**Blameless is the essential property.** The premise is that people act reasonably given the information and incentives they had at the time. If an engineer could run a command that took production down, the system allowed it - that is the finding, not the engineer's carelessness. The moment reviews assign blame, people hide information, and the organisation stops learning.

**Structure of a good document**

- **Summary** - what happened, impact, and duration in plain language.
- **Impact** - users affected, requests failed, revenue or SLO budget consumed.
- **Timeline** - timestamped events from first symptom to resolution, including what responders believed at each point (not just what was true).
- **Contributing factors** - plural, deliberately. Complex system failures rarely have a single root cause; the "five whys" is a starting technique, not a complete method.
- **What went well** - genuinely useful; it identifies what to protect.
- **Where we got lucky** - an underused section that surfaces latent risk.
- **Action items** - each with an owner, a priority, and a tracking ticket.

**Action items are where post-mortems live or die.** Vague items ("improve monitoring") never get done. Specific, small, owned items do. Track completion rate as a metric; an organisation with a backlog of unfinished post-mortem actions is one that keeps having the same incident.

**Which incidents get one:** every incident above an agreed severity, plus any near miss the team found instructive. Publish them internally - the learning value is mostly in the reading.

## Example

```markdown
# Post-mortem: EU checkout errors, 2026-02-11 (SEV-1, 78 min)

**Summary:** A database failover took longer than the application's connection timeout; checkout failed for EU customers for 78 minutes.

**Impact:** 412 enterprise tenants; ~38,000 failed checkouts; 62% of the monthly error budget; SLA breached for EU (credits applied).

**Timeline (UTC):** 03:04 primary DB host failure · 03:06 page · 03:21 IC declared · 03:55 pools restarted · 04:22 recovered.
What we believed at 03:30: "the network is partitioned" (it was not - pools were stuck on dead connections).

**Contributing factors:** connection pools with no validation on borrow; failover never tested under load; runbook assumed automatic reconnection.

**What went well:** the page fired in 2 minutes. **Where we got lucky:** it happened at 03:00, off-peak.

**Actions:** enable connection validation (@dana, 2026-02-25) · quarterly failover test under load (@kai, 2026-03-15) · update runbook (@sam, 2026-02-18)
```

## Interview tips

- Explain _why_ blamelessness produces better information - the psychological-safety argument, not just the rule.
- "Contributing factors, not root cause" is a modern, senior framing worth using.
- Tracking action-item completion is the practice that turns post-mortems from ritual into improvement.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
