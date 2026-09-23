---
title: "What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?"
id: 675
category: "Incident Management"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - incident-management
  - severity-levels
  - sla
  - sre
quiz:
  stem: "Which operational scenario warrants declaring a Sev-1 incident under standard enterprise incident management frameworks?"
  options:
    - "An internal engineering wiki has a broken stylesheet"
    - "A core payment processing API is failing globally, preventing all customers from completing transactions"
    - "A daily analytics batch job completed 10 minutes late"
    - "A developer forgot their staging VPN password"
  answer: 2
  explanation: "Sev-1 is reserved for catastrophic outages affecting core business functionality, causing severe revenue loss or critical customer impact, and requiring immediate all-hands mobilization."
---

# What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?

**Short answer:** Severity levels categorize incident business impact (Sev-1 is critical global outage; Sev-4 is minor internal bug), defining strict operational response SLAs, notification escalation paths, and war room protocols.

## Detail

Without clear severity classification, teams panic over minor bugs or fail to escalate catastrophic revenue-losing outages:

### Standard Severity Matrix

| Level                | Definition                            | Impact                                                        | Response SLA             | Protocol                                                                         |
| -------------------- | ------------------------------------- | ------------------------------------------------------------- | ------------------------ | -------------------------------------------------------------------------------- |
| **Sev-1 (Critical)** | Core service down globally            | Millions lost, data loss, full customer disruption            | **Immediate (< 5 mins)** | Incident Commander assigned, 24/7 War Room, C-suite & public status page alerts  |
| **Sev-2 (Major)**    | Major feature impaired; no workaround | High business impact (e.g. checkout failing in Europe)        | **< 15 minutes**         | Active Incident Commander, dedicated Slack channel/bridge, hourly status updates |
| **Sev-3 (Moderate)** | Non-critical component degraded       | Workaround exists; minimal customer impact                    | **< 2 hours**            | Managed during business hours; ticket filed                                      |
| **Sev-4 (Minor)**    | Minor cosmetic or internal annoyance  | Zero customer impact (e.g. internal reporting dashboard slow) | Next sprint              | Standard backlog prioritization                                                  |

Clear severity criteria prevent alert inflation and establish predictable communication cadences.

**Make the criteria measurable** ("more than 5% of checkouts failing", "any confirmed data loss or security breach", "a single enterprise customer fully down") so the person paged can classify in seconds. Security incidents often get their own track because they add legal, evidence-preservation, and regulatory-notification steps. **Declare high and downgrade**: over-declaring costs a few people's attention; under-declaring costs customer impact. The trade-off is severity inflation - if every incident is a Sev-1, the label stops mobilising anyone, so review severity assignments in post-incident reviews.

## Example

```yaml
# severity-policy.yaml - the triggers are measurable, the consequences automatic
sev1:
  when: ["core journey (login, checkout, payments) failing for > 5% of users", "confirmed data loss", "suspected security breach"]
  page: [service on-call, incident commander rotation, communications lead]
  ack_within: 5m
  comms: { status_page: required, internal_update_every: 30m, exec_notify: true }
  post_incident_review: required
sev2:
  when: ["major feature impaired, no workaround", "single region or large customer segment affected"]
  page: [service on-call]
  ack_within: 15m
  comms: { status_page: if_customer_visible, internal_update_every: 60m }
  post_incident_review: required
sev3:
  when: ["degraded, workaround exists", "internal tooling down"]
  page: none # ticket, business hours
  post_incident_review: optional
sev4:
  when: ["cosmetic issue", "no customer impact"]
  page: none # backlog
```

## Interview tips

- Severity tied directly to customer/business impact, not technical difficulty.
- Sev-1: catastrophic global impact, 24/7 war room, immediate <5 min SLA.
- Incident Commander role activated for high severity (Sev-1/Sev-2).
- Predictable communication cadences (internal stakeholders and public status page).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
