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

## Example

```markdown
# Playbook: Regional outage (primary region unavailable)

**Activate when:** SLO burn-rate page for 2+ tier-1 services in the same region, or provider status confirms a regional event.
**Who can activate:** any on-call incident commander (IC).

## Roles

- IC - owns decisions and timeline; does not debug.
- Tech lead - coordinates responders; owns the failover runbook.
- Comms lead - status page every 30 min, customer-success briefing.
- Scribe - timeline in the incident channel.

## Decision points

| Decision                  | Criteria                                               | Authority        |
| ------------------------- | ------------------------------------------------------ | ---------------- |
| Fail over to secondary    | Primary impaired > 15 min and no provider ETA < 30 min | IC + eng. VP     |
| Customer notification     | Any customer-visible impact > 10 min                   | IC               |
| Regulator notification    | Personal-data exposure suspected                       | DPO + legal      |

## Phases

1. Detect and declare (SEV1), open the incident channel and bridge.
2. Contain: freeze deploys; enable degraded mode (read-only checkout).
3. Recover: run `runbooks/region-failover.md`; verify SLIs in the secondary.
4. Exit when SLIs are green for 30 min; schedule the postmortem within 5 working days.
```

## Interview tips

- The runbook/playbook distinction is the core of the question - answer it directly and early.
- Decision authority ("who can declare, who can approve failover") is what playbooks uniquely provide.
- Mention regulatory notification deadlines for security incidents; it shows breadth beyond the technical.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
