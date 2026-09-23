---
title: "What is an Incident Response Plan?"
id: 122
category: "Incident Management"
difficulty: "Intermediate"
tags:
  - devops
  - incident-management
  - interview-questions
---

# What is an Incident Response Plan?

**Short answer:** An incident response plan is the documented, rehearsed procedure for handling incidents - defining severity criteria, roles, escalation paths, communication templates, and the steps for detection through post-incident review.

## Detail

**What the document must contain**

- **Scope and definitions** - what counts as an incident, and the severity matrix with concrete examples.
- **Declaration authority** - who can declare an incident, and how (deliberately low-friction; anyone should be able to).
- **Roles and responsibilities** - incident commander, operations lead, communications lead, scribe, and how they are assigned.
- **Escalation paths** - primary and secondary on-call per service, the manager escalation ladder, and vendor support contacts with account numbers.
- **Communication plan** - internal channel conventions, stakeholder update cadence per severity, customer-facing status page policy, and pre-approved templates so nobody drafts prose during an outage.
- **Response procedures** - the standard sequence, plus links to service-specific runbooks.
- **Regulatory obligations** - for a security incident, breach notification timelines and who contacts legal: GDPR's 72 hours to the supervisory authority, NIS2's 24-hour early warning and 72-hour notification for in-scope EU entities, the EU DORA regime for financial entities, and for US-listed companies a Form 8-K disclosure within four business days of deciding a cyber incident is material.
- **Recovery and closure criteria** - how you decide the incident is over.
- **Post-incident process** - timeline for the review and who owns it.

**Making it real.** A plan that lives only in a document is a plan that fails. It must be: accessible when your systems are down (offline copy, out-of-band chat), rehearsed through tabletop exercises and game days, updated after every incident, and short enough that a stressed engineer can actually use it at 3 a.m.

**Security incidents** need extra steps: evidence preservation before remediation, credential rotation, forensic capture, and a decision path for law enforcement and regulator contact.

## Example

```markdown
# Incident Response Plan - Payments Platform (v3.2, reviewed 2026-07)

**Declare:** anyone can, via `/incident declare` in Slack or the PagerDuty "Major Incident" button.

| Severity | Trigger (examples) | Who is paged | Updates |
| --- | --- | --- | --- |
| SEV-1 | checkout failing for > 5% of users; data loss; suspected breach | on-call, IC rotation, comms lead | every 30 min, status page |
| SEV-2 | major feature impaired, no workaround | service on-call | hourly, internal |

**Roles:** IC (coordinates, does not debug), Ops lead (only person changing prod), Comms lead, Scribe.

**Out-of-band:** if Slack or SSO is down, bridge on the Zoom link in the printed on-call card; this plan is mirrored to the offline wiki export.

**Security incidents:** preserve evidence before remediation; notify Legal (legal-oncall@) within 1 hour - regulatory clocks may already be running.

**Closure:** metrics at baseline for 30 min; customer comms sent; review scheduled within 5 business days.
```

## Interview tips

- Pre-written communication templates are a small detail that clearly signals real experience.
- "Accessible when the systems it covers are down" catches a genuine and common failure.
- Mention tabletop exercises - an untested plan is an assumption.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
