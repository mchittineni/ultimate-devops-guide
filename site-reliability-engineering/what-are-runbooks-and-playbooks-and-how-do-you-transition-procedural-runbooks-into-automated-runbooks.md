---
title: "What are Runbooks and Playbooks and how do you transition procedural runbooks into automated runbooks?"
id: 648
category: "Site Reliability Engineering (SRE)"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - sre
  - runbooks
  - automation
  - incident-response
quiz:
  stem: "Why must every production PagerDuty alert include a direct link to a verified Runbook?"
  options:
    - "To satisfy cloud billing requirements"
    - "To provide stressed on-call engineers with clear diagnostic commands and immediate mitigation steps without relying on tribal memory under pressure"
    - "To prevent the alert from triggering SMS messages"
    - "To automatically restart the affected container"
  answer: 2
  explanation: "During high-severity incidents, cognitive stress is extreme. Linking direct runbooks ensures on-call engineers have clear, tested triage and mitigation steps ready immediately."
---

# What are Runbooks and Playbooks and how do you transition procedural runbooks into automated runbooks?

**Short answer:** Runbooks provide step-by-step procedures for diagnosing and mitigating specific alert conditions; maturing SRE organizations evolve static documentation into executable interactive notebooks and ultimately automated self-healing scripts.

## Detail

When an engineer is woken up at 3 a.m., stress impairs cognitive function. Clear runbooks prevent costly triage mistakes:

### The Runbook Evolution Hierarchy

```text
Level 1: Unwritten Knowledge (Tribal memory - highly dangerous)
   └── Level 2: Static Documentation (Markdown runbook linked in alert)
          └── Level 3: Interactive Runbooks (Jupyter / Runme executable code blocks)
                 └── Level 4: Fully Automated Self-Healing (Operator / SSM Automation / Lambda remediation)
```

### Essential Elements of a Great Runbook

- Linked directly in the PagerDuty alert description (`Runbook: https://wiki/alerts/db-high-lag`).
- **What this alert means**: In plain English, what business functionality is degraded.
- **Diagnostic commands**: Exact commands to run (`kubectl get endpoints`, `pg_stat_activity`).
- **Immediate mitigation**: How to stop customer pain fast (e.g. failover command, scaling replica count) before performing deep root-cause debugging.
- **Escalation path**: Who to escalate to if standard mitigation fails.

**Runbook versus playbook.** A runbook is the procedure for one specific alert or task ("replica lag high on orders-db"); a playbook is the broader response strategy for a class of situation (a security incident, a regional failover), which usually links to several runbooks.

**Automate in steps, not in one leap.** Promote a runbook one level at a time: first make the diagnostic commands executable (so the output is attached to the page), then automate the mitigation behind a human "approve" button, and only fully automate once the step has run safely many times. Automation needs guardrails - rate limits, a blast-radius cap, and a stop condition that pages a human - or it amplifies the incident it was meant to fix. The trade-off is that fully automated fixes can hide a recurring cause, so every automated remediation should still emit an event that someone reviews.

## Example

```markdown
# Runbook: OrdersDbReplicaLagHigh

**What it means:** read replicas are > 30 s behind; order history pages show stale data. Writes are unaffected.

## Diagnose

1. Lag per replica (run on the primary): `SELECT client_addr, state, replay_lag FROM pg_stat_replication;`
2. Oldest running queries (run on the replica): `SELECT pid, now() - xact_start AS age, query FROM pg_stat_activity WHERE state <> 'idle' ORDER BY age DESC LIMIT 5;`

## Mitigate (stop the customer pain first)

1. Route reads to the primary: `kubectl -n orders set env deploy/orders-api READ_FROM_REPLICA=false`
2. If a long-running query is blocking replay, cancel it: `SELECT pg_cancel_backend(<pid>);`

## Escalate

Lag still rising after 15 minutes: page the database on-call (`@db-oncall`).
```

## Interview tips

- Linking runbooks directly in the alerting payload.
- Prioritizing customer mitigation (stopping the bleeding) over immediate root-cause investigation.
- Evolving procedural manual steps into automated self-healing controllers.
- Clear diagnostic commands and escalation paths.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?]] (`#675`): [What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?](../incident-management/what-are-incident-severity-levels-sev-1-to-sev-4-and-how-do-they-govern-response-slas-and-war-rooms.md)
- [[What are Automated Remediation and Self-Healing systems and when should automation halt?]] (`#679`): [What are Automated Remediation and Self-Healing systems and when should automation halt?](../incident-management/what-are-automated-remediation-and-self-healing-systems-and-when-should-automation-halt.md)
- [[What is Error Budget Burn-Rate Alerting and How Do You Tune Thresholds?]] (`#721`): [What is Error Budget Burn-Rate Alerting and How Do You Tune Thresholds?](../slo-engineering/what-is-error-budget-burn-rate-alerting-and-how-do-you-tune-thresholds.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
