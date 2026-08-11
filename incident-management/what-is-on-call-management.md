---
title: "What is On-Call Management?"
id: 125
category: "Incident Management"
difficulty: "Intermediate"
tags:
  - devops
  - incident-management
  - interview-questions
---

# What is On-Call Management?

**Short answer:** On-call management is the practice of organising who responds to production alerts outside normal hours - rotations, escalation policies, compensation, and the alert hygiene that makes the rotation sustainable.

## Detail

**Structure**

- **Rotation** - typically weekly, with a primary and a secondary. Follow-the-sun rotations across time zones eliminate night pages entirely and are the best option where team distribution allows.
- **Escalation policy** - if the primary does not acknowledge within a few minutes, escalate to the secondary, then to a manager. Automatic, not hopeful.
- **Handover** - a documented shift handover covering ongoing issues, recent changes, and known risks.
- **Compensation** - paid, in money or time off. Unpaid on-call is a retention problem waiting to happen.

**What makes it sustainable**

- **Alert hygiene above all.** Every page must be urgent, actionable, and real. Track pages per shift and the percentage that were actionable; anything that pages without needing human action tonight becomes a ticket instead.
- **Runbooks linked from every alert**, so the responder is not starting from a blank page.
- **You build it, you run it.** Teams on call for their own services fix the causes of their own pages - the incentive alignment is the whole point.
- **Onboarding** - shadow shifts before carrying the pager alone, and access verified in advance.
- **Follow-up** - review pages weekly, convert noisy alerts into fixes, and treat a night page as a bug in the system.

**Healthy targets:** fewer than two pages per shift on average, and near-zero pages that required no action. Beyond that, you are burning people out and training them to ignore the pager.

## Interview tips

- Alert quality is the answer to almost every on-call question - noise is the core problem.
- Naming compensation and sustainable limits shows you think about people, not just systems.
- "You build it, you run it" plus weekly page review is the loop that actually improves things.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
