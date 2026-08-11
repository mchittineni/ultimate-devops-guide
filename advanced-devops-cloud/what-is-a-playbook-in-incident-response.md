---
title: "What is a Playbook in Incident Response?"
id: 152
category: "Advanced DevOps & Cloud"
difficulty: "Intermediate"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is a Playbook in Incident Response?

**Short answer:** A playbook is the coordinated response process for a class of incident - who does what, in what order, with what decision points and communications - as opposed to a runbook, which is the technical procedure for one specific task.

## Detail

**Runbook vs playbook**

|          | Runbook                      | Playbook                            |
| -------- | ---------------------------- | ----------------------------------- |
| Scope    | One task or alert            | A class of incident                 |
| Content  | Commands and checks          | Roles, decisions, comms, escalation |
| Audience | The engineer fixing it       | The whole response team             |
| Example  | "Restart the stuck consumer" | "Suspected data breach response"    |

**What a playbook defines**

- **Activation criteria** - what triggers this playbook, and who can invoke it.
- **Roles** - incident commander, technical lead, communications lead, scribe, and any specialist roles (legal, security, customer support).
- **Decision points** - the judgement calls, with the criteria and the authority for each: when to fail over, when to notify customers, when to involve law enforcement.
- **Communication plan** - internal channel, stakeholder cadence, customer messaging templates, and regulator obligations with deadlines.
- **Response phases** - typically detect, contain, eradicate, recover, and review, each with its own actions.
- **Evidence handling** - for security incidents, what to preserve before remediating.
- **Exit criteria** - how you decide the incident is over.

**Common playbooks:** security breach, data loss, region outage, third-party provider failure, ransomware, and DDoS. Security incident response playbooks are frequently mandated by compliance frameworks.

**Playbooks must be rehearsed.** Tabletop exercises reveal the gaps - nobody knew who could authorise the failover, the contact list was stale, the plan lived only in the wiki that was down. Discovering that during a drill is the entire point.

## Interview tips

- The runbook/playbook distinction is the core of the question - answer it directly and early.
- Decision authority ("who can declare, who can approve failover") is what playbooks uniquely provide.
- Mention regulatory notification deadlines for security incidents; it shows breadth beyond the technical.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Docker?]] (`#6`): [What is Docker?](../docker/what-is-docker.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
