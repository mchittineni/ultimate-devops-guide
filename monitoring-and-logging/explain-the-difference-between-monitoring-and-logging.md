---
title: "Explain the difference between monitoring and logging"
id: 35
category: "Monitoring and Logging"
difficulty: "Beginner"
tags:
  - devops
  - monitoring-and-logging
  - interview-questions
---

# Explain the difference between monitoring and logging

**Short answer:** Logging records discrete events with context, one line at a time; monitoring collects and evaluates aggregated numeric signals over time. Logs tell you what happened in a specific request; monitoring tells you how the system is behaving overall.

## Detail

|                   | Monitoring (metrics)               | Logging                                       |
| ----------------- | ---------------------------------- | --------------------------------------------- |
| Data              | Numeric time series with labels    | Timestamped event records, often text or JSON |
| Question answered | "Is something wrong, and how bad?" | "What exactly happened here?"                 |
| Cardinality       | Must stay low                      | Can be very high                              |
| Storage cost      | Cheap, compresses extremely well   | Expensive, grows with traffic                 |
| Retention         | Months to years                    | Days to weeks, typically                      |
| Best for          | Alerting, dashboards, trends, SLOs | Debugging, audit trails, forensics            |
| Tools             | Prometheus, Grafana, CloudWatch    | ELK/OpenSearch, Loki, Splunk                  |

Traces are the third pillar: they follow a single request across services and explain _where_ time was spent, bridging the two.

**The practical workflow** during an incident: an alert fires from a metric (error ratio above SLO), a dashboard narrows it to a service and version, traces identify the slow or failing dependency, and logs for those specific trace IDs reveal the exact cause.

The connective tissue is correlation IDs - a trace ID propagated through headers and included in every log line and metric exemplar. Without it, you are searching by timestamp and hoping.

## Example

```text
The same failed request, seen by each signal

metric  http_requests_total{service="checkout",route="/pay",code="502"}  +1
        (one number in a counter shared by thousands of requests - cheap, alertable)

log     {"ts":"2026-09-23T10:32:11Z","level":"error","service":"checkout",
         "trace_id":"4bf92f3577b34da6a3ce929d0e0e4736","route":"/pay",
         "msg":"payment provider timeout after 5000ms","provider":"acme-pay"}
        (one record with the detail - searchable, expensive at volume)

trace   4bf92f35...  checkout /pay 5.1s -> payments-client 5.0s (timeout)
        (the same trace_id joins the log line to the request's path)
```

## Interview tips

- Mention the three pillars (metrics, logs, traces) and how you move between them.
- Structured JSON logging with a trace ID is the single highest-value logging practice - say it.
- Cost is a legitimate engineering concern: sample verbose logs, keep metrics for trends, keep logs short-lived.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What is Infrastructure Monitoring?]] (`#131`): [What is Infrastructure Monitoring?](../infrastructure-monitoring/what-is-infrastructure-monitoring.md)
- [[What are Monitoring Tools?]] (`#132`): [What are Monitoring Tools?](../infrastructure-monitoring/what-are-monitoring-tools.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
