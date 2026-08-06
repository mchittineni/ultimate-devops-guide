---
title: "What are Monitoring Best Practices?"
id: 133
category: "Infrastructure Monitoring"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-monitoring
  - interview-questions
---

# What are Monitoring Best Practices?

**Short answer:** Monitor what users experience, alert only on actionable symptoms, define signals with USE and RED, keep dashboards purposeful, manage cardinality and cost, and treat monitoring configuration as code.

## Detail

**What to measure**

- Start from user-visible outcomes and SLOs, then add the supporting resource signals.
- Use **RED** (Rate, Errors, Duration) for services and **USE** (Utilisation, Saturation, Errors) for resources.
- Include business metrics — a drop in orders per minute is often the fastest, clearest outage signal you have.

**Alerting**

- Every alert must be **urgent, actionable, and real**. If none of those hold, it is a dashboard or a ticket.
- Alert on symptoms (users failing) rather than causes (one node unhealthy). Cause-based alerts multiply and page for things that self-heal.
- Use SLO burn-rate alerts with multiple windows instead of static thresholds.
- Every alert carries a runbook link, an owner, and a clear severity.
- Review page volume weekly and delete or fix noisy alerts. Alert fatigue is the primary failure mode of monitoring.

**Dashboards**

- One purpose per dashboard: a service overview answering "is it healthy?" in five seconds, with drill-downs beneath.
- Consistent layout across services so responders do not relearn each one.
- Annotate deploys and incidents — "what changed?" is the first question in every investigation.

**Operational hygiene**

- Monitoring configuration (dashboards, alert rules, recording rules) lives in Git and is deployed by pipeline.
- Control metric cardinality; unbounded labels are the most common cause of a monitoring system falling over.
- Set retention deliberately, and downsample old data for long-term trends.
- Monitor the monitoring — a dead-man's-switch alert that fires when the pipeline goes quiet.

## Interview tips

- "Urgent, actionable, real" is a crisp three-part test worth memorising.
- The dead-man's switch (alerting on silence) is a detail few candidates mention.
- Cardinality control is the operational answer that shows you have run Prometheus at scale.

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
