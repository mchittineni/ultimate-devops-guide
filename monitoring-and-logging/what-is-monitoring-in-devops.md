---
title: "What is monitoring in DevOps?"
id: 31
category: "Monitoring and Logging"
difficulty: "Beginner"
tags:
  - devops
  - monitoring-and-logging
  - interview-questions
---

# What is monitoring in DevOps?

**Short answer:** Monitoring is the continuous collection and evaluation of system signals - metrics, logs, traces, and events - to know whether a service is healthy, to alert humans when it is not, and to give evidence during diagnosis.

## Detail

Monitoring answers known questions: is the error rate above threshold, is the disk filling, is latency degrading. (Observability, by contrast, is about being able to answer questions you did not anticipate.)

**The layers you monitor:**

- **Infrastructure** - CPU, memory, disk, network on hosts and nodes.
- **Platform** - Kubernetes pod restarts, scheduler pressure, queue depth.
- **Application** - request rate, error rate, latency, saturation of connection pools and thread pools.
- **Business** - checkouts per minute, signups, revenue-affecting flows. Often the fastest signal that something is broken.
- **User experience** - real user monitoring and synthetic probes from outside your network.

**Two useful frameworks:** the **RED** method for request-driven services (Rate, Errors, Duration) and the **USE** method for resources (Utilisation, Saturation, Errors). Between them they cover most of what matters.

**Alerting discipline** is the part most teams get wrong. Alert on symptoms that affect users, not on every cause. Every alert should be actionable, urgent, and linked to a runbook. Alerts nobody acts on train people to ignore the pager.

## Example

```yaml
# Prometheus: alert on the symptom (user-visible errors), not the cause
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{job="api",status=~"5.."}[5m]))
          / sum(rate(http_requests_total{job="api"}[5m])) > 0.02
        for: 10m
        labels: { severity: page }
        annotations:
          summary: "API 5xx rate above 2% for 10 minutes"
          runbook: "https://runbooks.example.com/api-high-error-rate"
```

## Interview tips

- Lead with RED and USE - they show a systematic approach rather than a list of tools.
- "Alert on symptoms, diagnose with causes" is a phrase that lands well.
- Be ready to discuss alert fatigue and how you reduced it.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What is Infrastructure Monitoring?]] (`#131`): [What is Infrastructure Monitoring?](../infrastructure-monitoring/what-is-infrastructure-monitoring.md)
- [[What are Monitoring Tools?]] (`#132`): [What are Monitoring Tools?](../infrastructure-monitoring/what-are-monitoring-tools.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
