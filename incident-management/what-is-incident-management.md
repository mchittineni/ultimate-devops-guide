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

**Tooling:** an alerting and on-call system (PagerDuty, incident.io, Rootly, Grafana Cloud IRM, or Jira Service Management - note Opsgenie is end-of-sale with support ending April 2027, and Grafana OnCall OSS was archived in 2026), a chat channel per incident with a bot that timestamps actions, a status page, and a tracker for post-mortem actions.

**Trade-off.** Process has a cost: heavyweight declaration for every blip teaches people to avoid declaring. Keep declaration one command away, scale the roles to the severity, and reserve the full structure for incidents that need it.

## Example

```text
One incident, walked through the lifecycle

10:02 DETECT     burn-rate page: login errors 18% (SLO 99.9%)
10:05 DECLARE    on-call declares SEV-2 in #inc-login, takes IC; asks @ops-dana to investigate
10:09 RESPOND    comms lead posts status page "investigating"; scribe starts timeline
10:14 MITIGATE   correlated with 09:58 IdP config change -> reverted
10:19 RESOLVE    errors back to baseline 0.05%; monitored 30 min, then resolved
+3d   REVIEW     blameless review: config changes to the IdP now go through CI with a canary;
                 2 action items, owners and due dates in Jira
```

## Interview tips

- "Mitigate first, diagnose later" is the instinct interviewers are testing for.
- Emphasise that the incident commander coordinates rather than fixes - it is the most misunderstood role.
- A timeline captured live, not reconstructed afterwards, is a detail that shows real incident experience.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
