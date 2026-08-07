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
- **Regulatory obligations** - for a security incident, breach notification timelines (GDPR's 72 hours, for example) and who contacts legal.
- **Recovery and closure criteria** - how you decide the incident is over.
- **Post-incident process** - timeline for the review and who owns it.

**Making it real.** A plan that lives only in a document is a plan that fails. It must be: accessible when your systems are down (offline copy, out-of-band chat), rehearsed through tabletop exercises and game days, updated after every incident, and short enough that a stressed engineer can actually use it at 3 a.m.

**Security incidents** need extra steps: evidence preservation before remediation, credential rotation, forensic capture, and a decision path for law enforcement and regulator contact.

## Interview tips

- Pre-written communication templates are a small detail that clearly signals real experience.
- "Accessible when the systems it covers are down" catches a genuine and common failure.
- Mention tabletop exercises - an untested plan is an assumption.

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
