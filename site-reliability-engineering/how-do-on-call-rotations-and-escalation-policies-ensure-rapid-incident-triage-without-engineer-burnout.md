---
title: "How do On-Call rotations and escalation policies ensure rapid incident triage without engineer burnout?"
id: 647
category: "Site Reliability Engineering (SRE)"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - sre
  - on-call
  - pagerduty
  - burnout
  - incident-management
quiz:
  stem: "Under Google SRE best practices, what should happen if an alert repeatedly pages an on-call engineer for an issue that resolves itself automatically within three minutes?"
  options:
    - "The engineer should be disciplined for not responding fast enough"
    - "The alert should be demoted to a non-paging ticket or adjusted with longer evaluation windows because it is non-actionable toil"
    - "The server should be rebooted every three minutes"
    - "The on-call shift duration should be doubled"
  answer: 2
  explanation: "If a condition self-heals without human action, paging a human is pure toil and causes alert fatigue. Alerts must be reserved strictly for events requiring immediate human intervention."
---

# How do On-Call rotations and escalation policies ensure rapid incident triage without engineer burnout?

**Short answer:** Healthy on-call rotations distribute operational burden across teams with clear primary and secondary escalation tiers, compensation, follow-the-sun scheduling, and strict caps on alert volume (< 2 pages per 12-hour shift) to prevent burnout.

## Detail

Toxic on-call cultures where engineers are paged 10 times a night lead to attrition, operational blindness, and catastrophic outages.

### Core Principles of Sustainable On-Call

1. **Primary & Secondary Tiers**:
   - **Primary**: Acknowledges and triages the incident within SLA (e.g. 5–15 minutes).
   - **Secondary (Backup)**: Paged automatically if the Primary fails to acknowledge after 10 minutes.
2. **Follow-the-Sun Rotations**: Hand off shifts between global teams (US, Europe, Asia) so engineers are on-call during their local daytime, eliminating 3 a.m. pages.
3. **Page Budget (< 2 Actionable Alerts / Shift)**:
   - A human should only be paged for issues requiring **immediate, intelligent human intervention**.
   - If a page self-resolves in 5 minutes, it is a bug in the alerting system and must be silenced.
4. **Compensated On-Call Time**: Provide time off in lieu or financial stipends for on-call shifts.

**The trade-off.** Follow-the-sun needs at least two well-staffed sites with genuine ownership of the service, and every handover is a point where context is lost; a single-site team usually runs a weekly primary/secondary rotation of six to eight engineers instead, and accepts some night pages. The page budget only works if exceeding it triggers something - alert clean-up or reliability work - rather than being quietly absorbed.

## Example

```hcl
# PagerDuty via Terraform: primary, then secondary after 10 minutes, then the manager
resource "pagerduty_escalation_policy" "checkout" {
  name      = "checkout"
  num_loops = 2

  rule {
    escalation_delay_in_minutes = 10
    target {
      type = "schedule_reference"
      id   = pagerduty_schedule.checkout_primary.id
    }
  }

  rule {
    escalation_delay_in_minutes = 10
    target {
      type = "schedule_reference"
      id   = pagerduty_schedule.checkout_secondary.id
    }
  }

  rule {
    escalation_delay_in_minutes = 15
    target {
      type = "user_reference"
      id   = pagerduty_user.eng_manager.id
    }
  }
}
```

## Interview tips

- Primary and secondary escalation tiers with timeouts.
- Capping alert volume to prevent fatigue (< 2 pages per shift).
- Paging only for actionable incidents requiring real human intervention.
- Follow-the-sun models to reduce sleep disruption.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?]] (`#675`): [What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?](../incident-management/what-are-incident-severity-levels-sev-1-to-sev-4-and-how-do-they-govern-response-slas-and-war-rooms.md)
- [[What is Incident Management?]] (`#121`): [What is Incident Management?](../incident-management/what-is-incident-management.md)
- [[What is an Incident Response Plan?]] (`#122`): [What is an Incident Response Plan?](../incident-management/what-is-an-incident-response-plan.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
