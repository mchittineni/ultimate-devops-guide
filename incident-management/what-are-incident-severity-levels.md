---
title: "What are Incident Severity Levels?"
id: 124
category: "Incident Management"
difficulty: "Beginner"
tags:
  - devops
  - incident-management
  - interview-questions
---

# What are Incident Severity Levels?

**Short answer:** Severity levels classify incidents by user impact, driving the response - who is paged, how fast, how often stakeholders are updated, and whether a post-mortem is mandatory. A typical scale runs SEV-1 (critical) to SEV-4 (minor).

## Detail

| Level     | Impact                                                                        | Response                                               | Comms                                                    |
| --------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ | -------------------------------------------------------- |
| **SEV-1** | Complete outage or critical data/security impact; most users affected         | Immediate page, all-hands, incident commander assigned | Status page, executive updates every 30 min              |
| **SEV-2** | Major functionality degraded, significant user subset affected, no workaround | Page on-call immediately                               | Internal updates hourly, status page if customer-visible |
| **SEV-3** | Minor degradation or a workaround exists                                      | Business hours, ticketed                               | Internal only                                            |
| **SEV-4** | Cosmetic or low-impact issue                                                  | Backlog                                                | None                                                     |

**Define by impact, not by cause.** "Database is down" is not a severity - "checkout is failing for all users" is. Cause-based severity leads to arguments; impact-based severity is assessable in seconds by whoever is paged.

**Make the criteria concrete.** Include measurable triggers: error rate above X%, more than Y customers affected, any confirmed data loss, any suspected security breach. Ambiguity leads to under-declaring, which is the far more common failure.

**Severity can change.** Start high and downgrade when the impact is understood. Over-declaring costs one interrupted engineer; under-declaring costs an extra hour of customer downtime.

**What each level triggers** should be automatic and documented: paging policy, communication cadence, whether a status page update is required, whether an incident commander is assigned, and whether a post-mortem is mandatory (usually SEV-1 and SEV-2 always).

## Interview tips

- Impact-based over cause-based classification is the key principle to state.
- "Declare high, downgrade later" is the correct instinct and worth saying explicitly.
- Tie each severity to concrete consequences - a severity that changes nothing is just a label.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#20`): [What is the difference between Continuous Delivery and Continuous Deployment?](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
