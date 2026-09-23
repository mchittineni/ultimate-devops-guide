---
title: "What is a Blameless Post-Mortem and how do you write effective incident reviews that drive systemic changes?"
id: 645
category: "Site Reliability Engineering (SRE)"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - sre
  - post-mortem
  - incident-management
  - culture
quiz:
  stem: "What is the primary danger of practicing 'blameful' post-mortems where engineers are punished for operational mistakes?"
  options:
    - "It violates cloud provider terms of service"
    - "Engineers become fearful and cover up mistakes, delay reporting incidents, and stop innovating or refactoring legacy systems"
    - "Blameful post-mortems consume too much disk storage"
    - "It forces all systems to use relational databases"
  answer: 2
  explanation: "Blaming individuals creates a culture of fear. Employees conceal failures, avoid taking risks, and delay reporting incidents, leaving underlying systemic vulnerabilities unpatched."
---

# What is a Blameless Post-Mortem and how do you write effective incident reviews that drive systemic changes?

**Short answer:** A blameless post-mortem assumes that engineers act with good intentions given the information they had; it investigates systemic vulnerabilities, missing automated guardrails, and confusing tooling rather than punishing individuals, producing concrete action items to prevent recurrence.

## Detail

Punishing engineers for human error ('human error' is a symptom, not a cause) encourages a culture of fear where employees hide mistakes, delay reporting outages, and avoid taking ownership.

### Principles of Blameless Culture

- **Second Story Principle**: Dig past the superficial 'engineer typed the wrong command' to discover _why_ the tooling allowed a human to type a destructive command without validation, or _why_ production permissions were not restricted.
- **Counterfactuals are Banned**: Phrases like 'Engineer should have known better' or 'If they had only checked X' are unconstructive and forbidden.

### Anatomy of an SRE Post-Mortem Document

1. **Summary & Impact**: Duration of outage, customer accounts impacted, revenue/SLO loss.
2. **Timeline of Events (UTC)**: Detailed chronological breakdown from trigger to detection, triage, and mitigation.
3. **Root Causes**: Systemic architecture and process flaws.
4. **What Went Well / What Went Poorly**: Evaluation of alerting speed and runbook clarity.
5. **Action Items (Preventative Tasks)**: Jira (or equivalent) tickets assigned with specific owners, prioritized above new features.

**Blameless is not accountability-free.** People are still accountable for completing action items and for telling the truth in the review; what is removed is punishment for decisions that were reasonable given what the person knew at the time. The limitation is cultural: a single manager who punishes someone after a "blameless" review undoes it for years, so leadership has to model it.

## Example

```markdown
# Post-incident review: checkout 5xx, 2026-08-07

**Impact:** 27 min, ~40% of checkout requests failed, 2,100 customers, 31% of the monthly error budget.

## Timeline (UTC)
- 09:02 release 1.9.0 starts canary
- 09:04 burn-rate page fires (detect: 2 min)
- 09:12 incident declared, IC assigned
- 09:23 rollback complete; 09:31 error rate at baseline (mitigate: 27 min)

## Contributing factors
- The migration took a table lock that the staging dataset was too small to reveal.
- Canary promotion was time-based, not metric-based.

## What went well / where we got lucky
- The page fired within 2 minutes. Lucky: it happened during business hours.

## Action items
| Action | Owner | Due |
| --- | --- | --- |
| Lint migrations for lock-taking DDL in CI | @dana | 2026-08-21 |
| Gate canary promotion on 5xx ratio | @kai | 2026-08-28 |
```

## Interview tips

- Assuming people act with good intentions given the context and tooling available.
- Blaming systems, guardrails, and tooling rather than punishing humans.
- Avoiding hindsight bias ('they should have known').
- Actionable engineering items prioritized in sprint backlogs.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?]] (`#675`): [What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?](../incident-management/what-are-incident-severity-levels-sev-1-to-sev-4-and-how-do-they-govern-response-slas-and-war-rooms.md)
- [[What is the Five Whys root cause analysis technique and how do you avoid stopping at human error?]] (`#678`): [What is the Five Whys root cause analysis technique and how do you avoid stopping at human error?](../incident-management/what-is-the-five-whys-root-cause-analysis-technique-and-how-do-you-avoid-stopping-at-human-error.md)
- [[How do you conduct post-incident action item tracking to prevent repeat outages?]] (`#680`): [How do you conduct post-incident action item tracking to prevent repeat outages?](../incident-management/how-do-you-conduct-post-incident-action-item-tracking-to-prevent-repeat-outages.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
