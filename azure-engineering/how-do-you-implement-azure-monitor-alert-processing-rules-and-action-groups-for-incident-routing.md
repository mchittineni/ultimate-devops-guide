---
title: "How Do You Implement Azure Monitor Alert Processing Rules and Action Groups for Incident Routing?"
id: 744
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - azure-engineering
  - azure-monitor
  - action-groups
  - incident-management
quiz:
  stem: "What is the primary operational advantage of using Azure Monitor Alert Processing Rules to manage maintenance windows?"
  options:
    - "They permanently delete the underlying virtual machines during downtime."
    - "They suppress notifications and action group triggers during scheduled intervals without requiring engineers to disable or reconfigure the underlying alert rules."
    - "They convert Azure alerts into AWS CloudWatch events automatically."
    - "They prevent virtual machines from consuming electricity during off-peak hours."
  answer: 2
  explanation: "Alert Processing Rules intercept fired alerts and suppress notification delivery during scheduled maintenance windows, eliminating alert fatigue while keeping the underlying alert rules intact."
---

# How Do You Implement Azure Monitor Alert Processing Rules and Action Groups for Incident Routing?

**Short answer:** Azure Monitor Alert Processing Rules intercept fired alerts to modify behavior—such as suppressing notifications during planned maintenance or dynamically applying Action Groups—while Action Groups define the exact notification recipients and automated remediation webhooks (e.g., PagerDuty, Logic Apps, Runbooks).

**Short answer:** Alert rules decide _whether_ something is wrong; **action groups** decide _who or what is told_ (email, SMS, push, voice, webhooks, Logic Apps, Functions, Automation runbooks, ITSM, Event Hubs); and **alert processing rules** sit between them, applying at fire time to add action groups or suppress notifications for a scope and schedule - for example, silencing a resource group during a maintenance window without disabling any rule. The benefit is centralized, scope-based routing; the risk is a suppression rule that silently hides a real outage.

## Detail

### 1. Alert Rules

- **Metric alerts** (static or dynamic thresholds, e.g. CPU > 90% for 5 minutes) - cheapest and fastest.
- **Log search alerts** - a KQL query over Log Analytics or Application Insights evaluated on a schedule.
- **Activity log alerts** - control-plane events (a deleted resource, a Service Health incident, a policy change).
- **Prometheus alerts** - rule groups over Azure Monitor managed service for Prometheus, typically for AKS.

Each fired alert carries a severity (Sev0-Sev4) and the resource it relates to, and is stateful (fired, then resolved) for metric and most log alerts.

### 2. Alert Processing Rules

- Evaluated after an alert fires, against **scope** (subscription, resource group, resource) and **filters** (severity, alert rule name, monitor service, resource type, alert context).
- **Two actions:**
  1. **Add action groups** - route all Sev0/Sev1 alerts in a production subscription to the on-call pager without editing every rule.
  2. **Suppress notifications** - one-off or recurring schedules (e.g. Sundays 02:00-04:00 UTC). Alerts still fire and are recorded; only the notifications are withheld.
- They replaced the older "action rules" feature.

### 3. Action Groups

- Reusable sets of receivers and actions, referenced by many rules.
- **Notifications**: email, SMS, Azure mobile app push, voice, and email to Azure Resource Manager roles (e.g. subscription Owners).
- **Actions**: webhooks and **secure webhooks** (Entra ID-authenticated), Logic Apps, Azure Functions, Automation runbooks, Event Hubs, and ITSM connectors. Paging tools such as PagerDuty and Opsgenie integrate via webhook; Slack or Teams usually via a Logic App or the tool's own integration.
- Use the **common alert schema** so every receiver gets one consistent payload.

```text
[Metric / KQL / Activity log alert fires]
               │
               ▼
[Alert Processing Rules] ── in maintenance window for this scope? ── YES: suppress notifications
               │ NO (and add on-call action group for Sev0/Sev1)
               ▼
       [Action Groups]
   ┌───────────┼───────────┐
   ▼           ▼           ▼
[Paging tool] [ChatOps]  [Logic App / runbook remediation]
```

**Trade-offs.** Centralized routing is powerful but opaque - an engineer reading an alert rule cannot see which processing rules will suppress or add to it, so keep processing rules in IaC with clear names and expiry dates for one-off suppressions. Automated remediation via runbooks should be idempotent and itself alert on failure.

### Real-World Production Scenario

An enterprise re-indexes 50 SQL databases every Saturday at midnight, spiking CPU alerts. Instead of disabling 50 rules each week, the SRE team creates a recurring alert processing rule that suppresses notifications for resources tagged `env=prod-db` during the two-hour window, while a second processing rule adds the on-call action group to every Sev0/Sev1 alert in the production subscriptions.

## Example

```bash
# Action group: on-call paging via webhook (common alert schema) plus email
az monitor action-group create -g rg-monitoring -n ag-oncall --short-name oncall \
  --action webhook pagerduty "https://events.pagerduty.com/integration/KEY/enqueue" usecommonalertschema \
  --action email sre sre-team@contoso.com

# Route every Sev0/Sev1 alert in the prod subscription to on-call
az monitor alert-processing-rule create -g rg-monitoring -n apr-prod-oncall \
  --scopes "/subscriptions/$PROD_SUB" \
  --rule-type AddActionGroups \
  --action-groups "$(az monitor action-group show -g rg-monitoring -n ag-oncall --query id -o tsv)" \
  --filter-severity Equals Sev0 Sev1

# Recurring Saturday maintenance window: suppress notifications for one resource group
az monitor alert-processing-rule create -g rg-monitoring -n apr-sql-maintenance \
  --scopes "/subscriptions/$PROD_SUB/resourceGroups/rg-sql-prod" \
  --rule-type RemoveAllActionGroups \
  --schedule-recurrence-type Weekly --schedule-recurrence Saturday \
  --schedule-recurrence-start-time 00:00:00 --schedule-recurrence-end-time 02:00:00 \
  --schedule-time-zone UTC
```

## Interview tips

- Separate the three roles: alert rules detect, processing rules route or suppress at fire time, action groups deliver.
- Stress that suppression withholds notifications but the alert still fires and is recorded - useful for post-maintenance review.
- Mention the common alert schema and secure webhooks for integrating paging tools.
- Name the risk: a forgotten suppression rule hiding a real incident - manage processing rules as code with expiry dates.
- Expect a follow-up on alert fatigue: severity discipline, dynamic thresholds, and alerting on symptoms (SLO burn rate) rather than every cause.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What happens when a Kubernetes control-plane node or etcd fails?]] (`#448`): [What happens when a Kubernetes control-plane node or etcd fails?](../kubernetes/what-happens-when-a-kubernetes-control-plane-node-or-etcd-fails.md)
- [[How do you troubleshoot a DNS problem in production?]] (`#435`): [How do you troubleshoot a DNS problem in production?](../cloud-engineering/how-do-you-troubleshoot-a-dns-problem-in-production.md)
- [[How does networking differ across AWS, Azure, and GCP?]] (`#282`): [How does networking differ across AWS, Azure, and GCP?](../cloud-platforms/how-does-networking-differ-across-aws-azure-and-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
