---
title: "How do you write effective PromQL queries and Alertmanager rules?"
id: 253
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - monitoring-and-logging
  - interview-questions
---

# How do you write effective PromQL queries and Alertmanager rules?

**Short answer:** Write effective PromQL queries by using `rate()` over range vectors for counter metrics, `histogram_quantile()` for latency percentiles, and structuring Alertmanager rules with multi-window burn rates, inhibition rules, and routing trees to prevent alert fatigue.

## Detail

Prometheus Query Language (PromQL) and Alertmanager form the core monitoring and alerting stack in cloud-native environments:

### 1. Key PromQL Functions & Best Practices

- **Instant Vector vs Range Vector:** An instant vector returns the single newest sample per series; a range vector (`http_requests_total[5m]`) returns a window of historical samples.
- **`rate()` vs `increase()`:**
- `rate(http_requests_total[5m])`: Calculates per-second average rate of increase over a counter. Always use `rate()` on Counters, never on Gauges.
- `increase(http_requests_total[1h])`: Calculates absolute count increase over the time window.
- **`histogram_quantile()`:** Calculates p90/p99 latency percentiles from Prometheus histogram buckets: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`

### 2. Prometheus Alerting Rules Structure

Alert rules evaluate PromQL expressions continuously. If an expression evaluates to true for longer than the `for` duration, the alert transitions from `PENDING` to `FIRING`.

### 3. Alertmanager Routing & Inhibition

- **Routing Trees:** Direct alerts to appropriate receivers (Slack, PagerDuty, Opsgenie) based on severity labels (`severity: critical` vs `severity: warning`).
- **Inhibition Rules:** Suppress downstream notification spam when a root cause alert is already firing (e.g. inhibit `InstanceDown` warnings if `ClusterUnreachable` critical alert is firing).
- **Group Waiting & Interval:** Buffer alerts (`group_wait: 30s`, `group_interval: 5m`) to send a single consolidated notification during incident cascades.

## Example

**1. Production Prometheus Alert Rules (`alerts.yml`):**

```yaml
groups:
  - name: production-workload-alerts
    rules:
      # High Error Rate Alert
      - alert: HighHttpErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m])) * 100 > 5
        for: 3m
        labels:
          severity: critical
          team: devops
        annotations:
          summary: "High HTTP 5xx error rate on {{ $labels.service }}"
          description: "Service {{ $labels.service }} has a 5xx error rate of {{ $value | printf \"%.2f\" }}% over the last 5 minutes."

      # Latency P99 Spike Alert
      - alert: HighP99Latency
        expr: |
          histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)) > 2.0
        for: 5m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "P99 latency exceeding 2 seconds on {{ $labels.service }}"
```

**2. Alertmanager Routing & Inhibition Configuration (`alertmanager.yml`):**

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-notifications'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-oncall'

inhibit_rules:
  # Inhibit node warnings if whole cluster is unreachable
  - source_match:
      alertname: 'ClusterDown'
    target_match:
      severity: 'warning'
    equal: ['cluster']

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts-prod'
        send_resolved: true

  - name: 'pagerduty-oncall'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
        send_resolved: true
```

## Interview tips

- Highlight why `rate()` must only be used on **Counter** metrics: counters strictly reset to 0 on container restarts; `rate()` handles counter resets automatically.
- Explain **Histogram Quantile calculation**: explain that histograms store cumulative bucket counts (`le`), enabling accurate percentile calculation across aggregated multi-instance pods.
- Mention **Inhibition rules** in Alertmanager: they prevent alert storms during major outages, keeping on-call engineers focused on root causes rather than secondary symptoms.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What are Monitoring Tools?]] (`#132`): [What are Monitoring Tools?](../infrastructure-monitoring/what-are-monitoring-tools.md)
- [[What are Monitoring Best Practices?]] (`#133`): [What are Monitoring Best Practices?](../infrastructure-monitoring/what-are-monitoring-best-practices.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
