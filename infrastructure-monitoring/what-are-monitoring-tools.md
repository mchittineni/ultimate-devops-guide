---
title: "What are Monitoring Tools?"
id: 132
category: "Infrastructure Monitoring"
difficulty: "Beginner"
tags:
  - devops
  - infrastructure-monitoring
  - interview-questions
---

# What are Monitoring Tools?

**Short answer:** Prometheus with Grafana is the open-source standard for metrics; ELK/OpenSearch or Loki for logs; Jaeger or Tempo for traces; and Datadog, New Relic, or Dynatrace as commercial all-in-one platforms - plus the cloud providers' native offerings.

## Detail

| Category        | Open source                                | Commercial / cloud                            |
| --------------- | ------------------------------------------ | --------------------------------------------- |
| Metrics         | Prometheus, VictoriaMetrics, Thanos, Mimir | Datadog, New Relic, CloudWatch, Azure Monitor |
| Visualisation   | Grafana                                    | Datadog dashboards, Kibana                    |
| Logs            | Loki, Elasticsearch/OpenSearch, Fluent Bit | Splunk, Datadog Logs, CloudWatch Logs         |
| Traces          | Jaeger, Tempo, Zipkin                      | Datadog APM, New Relic, X-Ray, Honeycomb      |
| Alerting        | Alertmanager, Grafana Alerting             | PagerDuty, Opsgenie                           |
| Synthetic / RUM | Blackbox exporter, Checkly                 | Datadog Synthetics, Pingdom                   |
| Profiling       | Pyroscope, Parca                           | Datadog Profiler                              |

**OpenTelemetry** is the important development: a vendor-neutral standard for instrumenting applications and shipping metrics, logs, and traces. Instrumenting with OTel means you can change backends without re-instrumenting - which is the strongest defence against observability vendor lock-in and the default recommendation for new work.

**Choosing.** Weigh cost at your data volume (commercial platforms are excellent and become extremely expensive at scale), the operational burden of self-hosting, existing team skills, ecosystem fit (Prometheus is native to Kubernetes), and long-term retention needs.

A very common pattern: Prometheus and Grafana for metrics and dashboards, Loki for logs, Tempo or Jaeger for traces, all instrumented via OpenTelemetry, with PagerDuty for on-call - self-hosted, portable, and cost-predictable.

## Interview tips

- Lead with OpenTelemetry; it is the answer that shows current thinking rather than tool trivia.
- Be ready to discuss cost - observability spend rivalling infrastructure spend is a real and common problem.
- Have a reasoned opinion on build-versus-buy rather than a favourite tool.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[What is GitLab CI?]] (`#19`): [What is GitLab CI?](../cicd/what-is-gitlab-ci.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
