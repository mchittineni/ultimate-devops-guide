---
title: "What is the Incident Commander (IC) role and how does command structure coordinate major outages?"
id: 676
category: "Incident Management"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - incident-management
  - incident-commander
  - ics
  - leadership
quiz:
  stem: "Why must the Incident Commander (IC) refrain from actively debugging code or running terminal commands during a major Sev-1 outage?"
  options:
    - "Incident Commanders are not allowed to have terminal access"
    - "Direct technical troubleshooting causes tunnel vision, destroying the IC's high-level situational awareness required to coordinate responders, communication, and mitigation"
    - "Only external consultants can run commands during outages"
    - "To prevent git merge conflicts"
  answer: 2
  explanation: "If the IC gets bogged down debugging a technical detail, they lose oversight of the broader incident response, leaving communication neglected and technical teams uncoordinated."
---

# What is the Incident Commander (IC) role and how does command structure coordinate major outages?

**Short answer:** The Incident Commander (IC) leads the incident response, holding ultimate decision-making authority; the IC does not debug or write code, but directs the response, assigns roles (Ops Lead, Comms Lead), manages cognitive load, and coordinates mitigation.

## Detail

Adapted from the Incident Command System (ICS) used by firefighters: when an outage hits, chaos ensues unless a single person takes command.

### The Cardinal Rule of the Incident Commander

**The Incident Commander does NOT troubleshoot or touch keyboard systems!**
If the IC starts debugging SQL queries, they develop tunnel vision and lose situational awareness of the global incident.

### The Command Roles

1. **Incident Commander (IC)**: Sets strategy, authorizes risky mitigations (e.g. database failovers), manages pacing, and removes blockers.
2. **Operations Lead (Tech Lead)**: Directs engineers running commands, testing hypotheses, and rolling back code; the only person who authorises changes to production during the incident.
3. **Communications Lead**: Writes internal status updates for leadership and publishes customer updates to the public status page (`status.company.com`), shielding engineers from executive interruptions.
4. **Scribe**: Logs all key timestamps, commands executed, and hypothesis results for the post-mortem.

**Scaling the structure.** In a small incident one person may be IC and scribe; in a very large one there are sub-leads per workstream (database, network, customer support), each reporting to the IC - the ICS idea of a manageable span of control (roughly 3-7 direct reports). The IC also owns handoff: after a few hours, a documented handover to a fresh IC. The limitation of the model is that it depends on practice - an IC rotation that never trains or runs drills will freeze on its first real Sev-1.

## Example

```text
IC opening script (first 5 minutes of a SEV-1)

"I am the incident commander. @dana is ops lead - all production changes go through Dana.
 @sam is comms lead - status page within 10 minutes, then every 30.
 @kai is scribe in the incident doc.
 Current impact: checkout failing for ~40% of users since 09:04.
 First question: what changed at 09:00? Dana, check deploys and flags; report back in 5.
 Next check-in 09:20. If you are not in a role, stay off the bridge unless asked."
```

## Interview tips

- The IC directs the response and does NOT write code or run commands.
- Maintaining global situational awareness and avoiding tunnel vision.
- Role delegation: Operations Lead, Comms Lead, Scribe.
- Shielding technical responders from executive and customer inquiries.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
