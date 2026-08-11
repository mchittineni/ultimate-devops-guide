---
title: "What is SOAR and what should you automate first?"
id: 176
category: "SecOps and Threat Detection"
difficulty: "Intermediate"
tags:
  - devops
  - secops
  - interview-questions
---

# What is SOAR and what should you automate first?

**Short answer:** SOAR (Security Orchestration, Automation and Response) executes playbooks across your security tools - enriching alerts, opening cases, and taking contained actions. Automate enrichment first, because it is safe, high-volume, and immediately removes the most tedious analyst work; automate response actions only where the action is reversible and the detection is precise.

## Detail

**Enrichment before action.** Before an analyst sees an alert, a playbook can attach: identity context (who owns this account, is it a service account, when did it last change), asset context (which team owns this workload, is it internet-facing, what data classification), reputation lookups, related alerts within the last 24 hours, and the relevant runbook link. This turns a 15-minute manual gather into a populated case, and it cannot break production.

**A sane automation ladder:**

1. Enrich and deduplicate alerts; auto-close known-benign patterns with a recorded reason.
2. Open and route cases with correct ownership and severity.
3. Request human confirmation for actions with blast radius (Slack approval with one click).
4. Auto-execute only narrow, reversible containment: revoke a session, disable an access key, quarantine an email, isolate a laptop.
5. Never auto-execute broad or destructive actions - deleting resources, blocking large network ranges, disabling production identities.

**The false-positive multiplier.** Automated response amplifies detection errors: a rule with 5% false positives that disables user accounts will lock out real people weekly. Require a measured precision threshold before a detection is allowed to trigger automated action, and keep a kill switch plus an audit trail of every automated action taken.

**Where DevOps tooling overlaps.** Much of this is achievable with the pipelines you already run - an event-driven function reacting to a cloud audit event, or a GitHub Actions workflow. Whether it is called SOAR matters less than whether the playbooks are version-controlled, tested, and reviewed like other code.

**Measure the benefit.** Track analyst minutes saved per playbook run, mean time to triage before and after, and the number of playbook failures. Playbooks silently failing on an API change is a common and dangerous outcome - monitor the automation itself.

## Example

```yaml
# Playbook: leaked cloud access key detected - enrich, contain narrowly, notify
on:
  detection: cloudtrail.access_key_from_new_asn
steps:
  - id: enrich
    parallel:
      - iam: describe_access_key_last_used
      - cmdb: lookup_owner_by_principal
      - siem: related_alerts_last_24h
  - id: decide
    when: "{{ enrich.iam.principal_type == 'service_account' }}"
    then: contain
    else: ask_human # human accounts route to an approval prompt
  - id: contain
    actions:
      - iam: deactivate_access_key # reversible
      - iam: revoke_active_sessions
  - id: notify
    actions:
      - slack: post_to_channel { channel: "{{ enrich.cmdb.owner_channel }}" }
      - case: open { severity: high, assign: "{{ enrich.cmdb.owner_team }}" }
```

## Interview tips

- "Enrichment first, response only where reversible" is the answer that shows judgement rather than enthusiasm.
- Raise the false-positive multiplier yourself - it is the risk interviewers want to hear you name.
- Expect: "would you auto-disable a user account?" - only with a precise detection, a reversible action, an audit trail, and a documented unlock path.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
