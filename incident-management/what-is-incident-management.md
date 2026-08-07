---
title: "What is Incident Management?"
id: 121
category: "Incident Management"
difficulty: "Beginner"
tags:
  - devops
  - incident-management
  - interview-questions
---

# What is Incident Management?

**Short answer:** Incident management is the structured process for detecting, responding to, resolving, and learning from unplanned service disruptions - with defined roles, severity levels, communication paths, and a blameless review afterwards.

## Detail

**The lifecycle**

1. **Detect** - monitoring alerts, synthetic checks, or customer reports.
2. **Triage and declare** - assess user impact, assign a severity, and declare an incident. Declaring early is almost always better than debating whether it counts.
3. **Respond** - assign roles, open a dedicated channel, begin investigation, and communicate status.
4. **Mitigate** - restore service first. Roll back, fail over, disable the feature flag, or shed load. Root cause can wait.
5. **Resolve** - confirm recovery with real signals, not assumption.
6. **Review** - a blameless post-mortem producing tracked, owned action items.

**Roles** (scaled to incident size)

- **Incident Commander** - owns coordination and decisions; explicitly does _not_ debug.
- **Operations / subject-matter experts** - investigate and apply fixes.
- **Communications lead** - updates stakeholders, customers, and the status page.
- **Scribe** - maintains the timeline as events happen; invaluable later.

**Why the process matters more than heroics.** Without structure, incidents devolve into several people making uncoordinated changes, no record of what was tried, and stakeholders interrupting responders for updates. The commander role exists to prevent exactly that.

**Tooling:** an alerting and on-call system (PagerDuty, Opsgenie, Grafana OnCall), a chat channel per incident with a bot that timestamps actions, a status page, and a tracker for post-mortem actions.

## Interview tips

- "Mitigate first, diagnose later" is the instinct interviewers are testing for.
- Emphasise that the incident commander coordinates rather than fixes - it is the most misunderstood role.
- A timeline captured live, not reconstructed afterwards, is a detail that shows real incident experience.

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
