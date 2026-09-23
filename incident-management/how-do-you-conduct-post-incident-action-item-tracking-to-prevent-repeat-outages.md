---
title: "How do you conduct post-incident action item tracking to prevent repeat outages?"
id: 680
category: "Incident Management"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - incident-management
  - action-items
  - post-mortem
  - governance
quiz:
  stem: "What policy prevents engineering teams from perpetually delaying post-incident reliability action items in favor of new product features?"
  options:
    - "Deleting customer tickets after 7 days"
    - "Enforcing error budget policies that halt new feature deployments until overdue high-severity incident action items are completed"
    - "Fining product managers for every unresolved bug"
    - "Prohibiting code releases on Mondays"
  answer: 2
  explanation: "Linking action items to error budget governance creates real business incentives: teams cannot ship new features until outstanding critical reliability vulnerabilities are remediated."
---

# How do you conduct post-incident action item tracking to prevent repeat outages?

**Short answer:** Post-incident action items must be prioritized as engineering bug tickets with strict completion SLAs, single assignees, and executive visibility, preventing preventative reliability work from being buried under product feature backlog.

## Detail

The most common organizational failure after an incident is holding a great post-mortem, writing 10 action items, and **completing none of them** because product managers prioritize new features. Six months later, the exact same outage recurs!

### Ensuring Action Items Actually Get Fixed

1. **Specific, Measurable Tasks**:
   - Bad: _'Improve monitoring.'_
   - Good: _'Add Prometheus alert for PostgreSQL connection pool saturation > 85% with runbook link.'_
2. **Strict SLAs Based on Severity**:
   - Sev-1 Action Items: Must be completed within **14 to 30 days**.
   - Sev-2 Action Items: Must be completed within **60 days**.
3. **Single Accountable Owner**: Every ticket is assigned to a specific engineer, not a team alias.
4. **Error Budget Enforcement**: If a team has overdue Sev-1 action items, the error budget policy freezes feature releases until the reliability tickets are resolved.
5. **Track It as a Metric**: Review open and overdue post-incident actions weekly (per team, visible to leadership), and link each ticket back to its incident so repeat incidents with an unfinished fix are obvious.

**Trade-off.** Too many action items is as bad as too few: a review that produces fifteen items guarantees most will rot. Prefer two or three that remove a class of failure (an automated gate, a guardrail) over a list of reminders, and explicitly close items that are no longer worth doing rather than letting them age.

## Example

```bash
# Jira: every open post-incident action past its due date, oldest first
jql='labels = postincident AND statusCategory != Done AND due < now() ORDER BY due ASC'
curl -s -u "$JIRA_USER:$JIRA_TOKEN" -G "https://acme.atlassian.net/rest/api/3/search/jql" \
  --data-urlencode "jql=$jql" --data-urlencode "fields=key,summary,assignee,duedate" \
  | jq -r '.issues[] | [.key, .fields.duedate, (.fields.assignee.displayName // "UNASSIGNED"), .fields.summary] | @tsv'
```

## Interview tips

- The pattern of repeat outages caused by neglected action items.
- Action items must be specific, testable engineering tasks, not vague aspirations.
- Strict SLAs (e.g. 14-30 days for Sev-1 actions).
- Halting feature releases if teams fail to resolve high-severity incident action items.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
