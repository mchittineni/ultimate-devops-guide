---
title: "What is a Runbook?"
id: 151
category: "Advanced DevOps & Cloud"
difficulty: "Beginner"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is a Runbook?

**Short answer:** A runbook is a documented procedure for performing a specific operational task or responding to a specific alert - the diagnostic and remediation steps, in order, that let any qualified engineer handle the situation consistently.

## Detail

**What a good runbook contains**

- **Trigger** - the exact alert or symptom this runbook addresses.
- **Impact** - what users experience, so the responder can judge urgency.
- **Prerequisites** - required access, tools, and any safety warnings.
- **Diagnosis** - ordered checks with the commands or dashboard links to run, and what each result means.
- **Remediation** - the actions to take for each diagnosis branch, with expected effect.
- **Verification** - how to confirm the problem is genuinely resolved.
- **Rollback** - how to undo the remediation if it makes things worse.
- **Escalation** - who to contact, when, and how.

**Practices that make runbooks useful rather than decorative**

- **Link from the alert.** A runbook nobody can find at 3 a.m. does not exist. Put the URL in the alert annotation.
- **Keep them close to the code** and update them as part of the change that affects them.
- **Write for a tired engineer** - imperative, specific, copy-pasteable commands, no assumed context.
- **Validate them during incidents and game days**, then fix what was wrong.
- **Treat every runbook as an automation backlog item.** A procedure clear enough to write down is usually clear enough to script.

**Runbook versus playbook.** A runbook is a specific technical procedure; a playbook is broader - the coordination, communication, and decision process for a class of situation. The terms are often used interchangeably, so define your usage if it matters.

## Example

```markdown
# Alert: APIHighErrorRate

**Impact:** users see 5xx responses on checkout.

## Diagnose

1. Recent deploy? `kubectl rollout history deploy/api -n prod` - if within 30 min, suspect the release.
2. Dependency health: check the payments dashboard and DB connection saturation.
3. Errors by cause: `sum by (error_type) (rate(api_errors_total[5m]))`

## Remediate

- Bad release → `kubectl rollout undo deploy/api -n prod` (expect recovery in ~2 min).
- Payment provider down → disable flag `payments-external`, degrade to queued processing.
- DB connections exhausted → scale down non-critical consumers; check for a long-running query.

## Verify

Error rate below 0.5% for 10 consecutive minutes on the API SLO dashboard.

## Escalate

Not resolved in 20 minutes → page the platform on-call (#incident channel).
```

## Interview tips

- "Every runbook is an automation candidate" is the DevOps framing of this question.
- Linking runbooks directly from alert annotations is the practical detail that shows experience.
- Note that runbooks decay - validating them during game days is how you keep them true.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
